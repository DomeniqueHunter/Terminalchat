import random
from typing import Any

from .config import (
    BREEDING_CHANCE, DEFAULT_BREEDING_CHANCE, HUNG_GENDERS, INTIMACY_BOND,
    INTIMACY_MIN_AGE, INTIMACY_NPC_TIER, INTIMACY_RELIEF,
    MPREG_BUILD_SCALE, MPREG_DEFAULT_SCALE, MPREG_FACTOR,
    PARTY_PREGNANCY_CHANCE,
)
from .content import OFFSPRING_TEXTS
from .locations.common import pronouns
from .models import Message, Player
from .needs import satisfy
from .party_talk import bonds
from .preferences import scene_defaults
from .scenes import DEFAULTS, POSITIONS, describe, parse_options
from .town_buildings.chat import TIERS, tier_of
from .town_buildings.family import relations


PARENT_CHILD = ("mother", "father", "son", "daughter")
SCENES = (
    "{a} and {b} slip away from the others. Hands find hands, the "
    "world narrows to breath and warmth, and the rest is theirs alone.",
    "{a} pulls {b} close. Neither says much. Later they lie tangled "
    "together, quiet and flushed, and smile at nothing.",
    "{b} laughs softly as {a} leans in. The light dims, the "
    "tension of the road melts away, and the night is kind.",
)
REFUSALS = {
    "stranger": "{b} shakes {their} head. 'I don't know you well "
                "enough for that, {a}.'",
    "acquaintance": "{b} smiles apologetically. 'Not yet, {a}. Give it "
                    "time.'",
}


def fertility(player:Player) -> float:
    if player.pregnant or player.gender == "None":
        return 0.0
    if player.gender == "Male":
        scale = MPREG_BUILD_SCALE.get(player.body.get("build"),
                                      MPREG_DEFAULT_SCALE)
        return MPREG_FACTOR * scale
    return BREEDING_CHANCE.get(player.gender, DEFAULT_BREEDING_CHANCE)


def pregnancy_pair(first:Player, second:Player,
                   rng:random.Random) -> tuple[Player, Player] | None:
    options = [(giver, carrier, fertility(carrier))
               for giver, carrier in ((first, second), (second, first))
               if giver.gender in HUNG_GENDERS and fertility(carrier) > 0]
    if not options:
        return None
    best = max(option[2] for option in options)
    chosen = rng.choice([option for option in options if option[2] == best])
    return chosen[0], chosen[1]


def pregnancy_roll(first:Player, second:Player,
                   rng:random.Random) -> list[str]:
    pair = pregnancy_pair(first, second, rng)
    if pair is None:
        return []
    return conception(pair[0], pair[1], rng, 1.0)


def conception(giver:Player, carrier:Player, rng:random.Random,
               factor:float) -> list[str]:
    if (factor <= 0 or giver.gender not in HUNG_GENDERS
            or rng.random() >= (PARTY_PREGNANCY_CHANCE * factor
                                * fertility(carrier))):
        return []
    carrier.pregnant = "party"
    carrier.profile["pregnant_by"] = giver.name
    carrier.profile["pregnant_by_id"] = giver.id
    return [f"👶 {OFFSPRING_TEXTS['pregnant_party'].format(
        name=carrier.name, their=pronouns(carrier.gender)[2],
        parent=giver.name)}"]


def situation(session:Any) -> str:
    if session.state in ("idle", "lobby"):
        return ""
    event = session.events.event
    if (session.state == "event" and event.get("kind") == "bivouac"
            and event["data"].get("lit")):
        return ""
    return "Not now. Only in town or at a lit campfire."


def willing(proposer:Player, other:Player, session:Any) -> bool:
    if not other.npc and not session.is_auto(other):
        return False
    limit = next(points for points, name in TIERS
                 if name == INTIMACY_NPC_TIER)
    return bonds(proposer).get(other.id, 0) >= limit


def make_love(first:Player, second:Player, session:Any,
              rng:random.Random,
              options:dict[str, str] | None=None) -> list[Message]:
    options = options or dict(DEFAULTS)
    story, giver, carrier, factor = describe(first, second, options, rng)
    lines = [f"💞 {' '.join(story)}"]
    for one, two in ((first, second), (second, first)):
        satisfy(one.needs, INTIMACY_RELIEF)
        bonds(one)[two.id] = bonds(one).get(two.id, 0) + INTIMACY_BOND
        session.repository.save(one)
    if giver is not None:
        lines += conception(giver, carrier, rng, factor)
    for one in (first, second):
        session.repository.save(one)
    return [Message("\n".join(lines))]


def find_member(session:Any, player:Player, name:str) -> Player | None:
    wanted = name.casefold()
    for member in session.party:
        if member is not player and member.name.casefold() == wanted:
            return member
    return None


def private(text:str, player:Player) -> list[Message]:
    return [Message(text, player.name)]


def intimacy_command(session:Any, proposals:dict[str, str], player:Player,
                     command:str, args:list[str], rng:random.Random
                     ) -> list[Message]:
    if session.member(player.name) is None or not player.alive:
        return private("Only living party members can do that.", player)
    options = scene_defaults(player)
    if command == "intimate":
        args, options = parse_options(args, options)
    other = find_member(session, player, " ".join(args))
    if other is None:
        return private(f"Usage: {command} <party member> [position] "
                       f"[top|bottom] [little|some|much] [in|on]", player)
    if command == "refuse":
        if proposals.get(player.name) != other.name:
            return private(f"{other.name} has not asked you.", player)
        del proposals[player.name]
        session.proposal_options.pop(player.name, None)
        return [Message(f"{player.name} gently declines {other.name}.")]
    if command == "consent":
        if proposals.get(player.name) != other.name:
            return private(f"{other.name} has not asked you.", player)
        del proposals[player.name]
        chosen = session.proposal_options.pop(player.name, DEFAULTS)
        return make_love(other, player, session, rng, chosen)
    return propose(session, proposals, player, other, rng, options)


def propose(session:Any, proposals:dict[str, str], player:Player,
            other:Player, rng:random.Random,
            options:dict[str, str]) -> list[Message]:
    reason = situation(session)
    if reason:
        return private(reason, player)
    if min(player.age, other.age) < INTIMACY_MIN_AGE or not other.alive:
        return private(f"{other.name} is not available.", player)
    if relations(player).get(other.id, {}).get("role") in PARENT_CHILD:
        return private(f"{other.name} is your "
                       f"{relations(player)[other.id]['role']}. Not "
                       f"like that.", player)
    if proposals.get(other.name) == player.name:
        return private(f"You already asked {other.name}.", player)
    if proposals.get(player.name) == other.name:
        del proposals[player.name]
        chosen = session.proposal_options.pop(player.name, DEFAULTS)
        return make_love(other, player, session, rng, chosen)
    if other.npc or session.is_auto(other):
        if willing(player, other, session):
            return make_love(player, other, session, rng, options)
        tier = tier_of(bonds(player).get(other.id, 0))
        text = REFUSALS.get(tier, REFUSALS["acquaintance"])
        return [Message(text.format(a=player.name, b=other.name,
                                    their=pronouns(other.gender)[2]))]
    proposals[other.name] = player.name
    session.proposal_options[other.name] = options
    return [Message(f"💬 {player.name} looks at {other.name} and asks "
                    f"quietly ({POSITIONS[options['position']][0]}, "
                    f"{player.name} {options['role']}). "
                    f"[consent {player.name}] or [refuse {player.name}]")]

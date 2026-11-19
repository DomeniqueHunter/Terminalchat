import random
import re
from typing import Any

from .config import (
    HUNG_GENDERS, INTIMACY_BOND, INTIMACY_MIN_AGE, INTIMACY_RELIEF,
    VAGINA_GENDERS,
)
from .house_titles import title_line, titles_of
from .partner_detail import partner_line
from .family_scenes import family_close, family_open
from .house_regulars import is_regular
from .intimacy import conception, fertility
from .models import Message, Player
from .needs import satisfy
from .npc_menu import bump
from .orientation import reaction
from .scenes import AMOUNTS, DEFAULTS, WHERE
from .town_buildings.brothel.practices import (
    can_do, describe, parse_direction,
)
from .town_buildings.brothel.practices_content import (
    ACT_ALIASES, ACT_LABELS, DOMINANT_ACTS, ROLE_WORDS,
)


FEEDING = {
    "oral": ("giver", {"hunger": -15, "thirst": -10}, "swallows"),
    "watersports": ("receiver", {"thirst": -30, "hunger": -5}, "drinks"),
    "scat": ("receiver", {"hunger": -20}, "eats"),
}
CONCEIVING = ("vaginal", "anal")
USAGE = ("Usage: home practice <name> <act> <give|receive> [little|some|much]"
         " [in|on]. Acts: " + ", ".join(ACT_LABELS))


def parse_practice(args:list[str]) -> tuple[list[str], str, str,
                                            dict[str, str], str]:
    words = list(args)
    options = {"amount": DEFAULTS["amount"], "where": DEFAULTS["where"]}
    direction = parse_direction(words[-1:]) if words else ""
    if direction:
        words.pop()
    while words and (words[-1].casefold() in AMOUNTS
                     or words[-1].casefold() in WHERE):
        word = words.pop().casefold()
        options["amount" if word in AMOUNTS else "where"] = word
    role = ""
    if words and words[-1].casefold() in ROLE_WORDS:
        role = ROLE_WORDS[words.pop().casefold()]
    act = ""
    if words:
        word = ACT_ALIASES.get(words[-1].casefold(), words[-1].casefold())
        if word in ACT_LABELS:
            act = word
            words.pop()
    return words, act, role, options, direction


def other_role(role:str) -> str:
    return "receive" if role == "give" else "give"


def partner_text(text:str, name:str) -> str:
    text = re.sub(r"\b[Tt]he client's\b", f"{name}'s", text)
    text = re.sub(r"\b[Tt]he client\b", name, text)
    text = re.sub(r"\bclient's\b", f"{name}'s", text)
    return re.sub(r"\bclient\b", name, text)


def feed(who:Player, effects:dict[str, int], factor:float) -> None:
    satisfy(who.needs, {need: round(amount * factor)
                        for need, amount in effects.items()})


def feeding_lines(act:str, role:str, player:Player, other:Player,
                  options:dict[str, str]) -> list[str]:
    lines: list[str] = []
    factor = AMOUNTS[options["amount"]][1]
    if act in FEEDING and options["where"] == "in":
        target, effects, verb = FEEDING[act]
        giver, receiver = ((player, other) if role == "give"
                           else (other, player))
        fed = giver if target == "giver" else receiver
        if not is_regular(fed):
            feed(fed, effects, factor)
        lines.append(f"🍽 {fed.name} {verb} {AMOUNTS[options['amount']][0]}"
                     f" and is fuller for it.")
    return lines


SETTINGS = (
    "The door is latched, the curtains are drawn, and the only light is "
    "the little lamp on the dresser. {a} and {b} are alone.",
    "The house creaks around them as the evening settles. {b} watches "
    "{a} cross the room, and the air between them gets thicker with "
    "every step.",
    "Rain taps on the roof. {a} lights a second candle, {b} loosens a "
    "collar, and nobody pretends this is a normal visit any more.",
)
AFTERGLOW = (
    "Afterwards the house is very quiet. {a} and {b} lie where they "
    "ended up, breathing slowly, the lamp guttering, neither in any "
    "hurry to move.",
    "{b} laughs softly into the pillow and {a} runs a lazy hand over "
    "{b}'s back. 'Same again tomorrow?' someone murmurs, and nobody "
    "bothers to answer out loud.",
    "The sweat cools slowly. {a} pulls the blanket over both of them "
    "and {b} finds {a}'s hand under it, fingers lacing without a word.",
)


def barrier(carrier:Player) -> str:
    if carrier.pregnant:
        return ""
    if fertility(carrier) > 0:
        return ""
    return f"{carrier.name} ({carrier.gender}) cannot carry a child."


def pregnancy_lines(act:str, role:str, player:Player, other:Player,
                    options:dict[str, str],
                    rng:random.Random) -> tuple[list[str], bool]:
    if act not in CONCEIVING or options["where"] != "in":
        return [], False
    giver, carrier = ((player, other) if role == "give" else (other, player))
    if giver.gender not in HUNG_GENDERS:
        return [], False
    if act == "vaginal" and carrier.gender not in VAGINA_GENDERS:
        return [], False
    if is_regular(carrier):
        return [f"(Regulars cannot become pregnant: {carrier.name} has no "
                f"character file.)"], False
    reason = barrier(carrier)
    if reason:
        return [f"(No chance of pregnancy: {reason})"], False
    lines = conception(giver, carrier, rng, AMOUNTS[options["amount"]][1])
    return lines, bool(lines) and carrier is other


def practice(player:Player, other:Player, home:dict[str, Any],
             args:list[str], repository:Any,
             rng:random.Random) -> list[Message]:
    _, act, role, options, direction = parse_practice(args)
    if not act or not role:
        return [Message(USAGE, player.name)]
    if min(player.age, other.age) < INTIMACY_MIN_AGE:
        return [Message(f"{other.name} is not available.", player.name)]
    if not can_do(player.gender, act, role, player.body):
        return [Message(f"You cannot do {ACT_LABELS[act]} {role} with "
                        f"your body.", player.name)]
    if not can_do(other.gender, act, other_role(role), other.body):
        return [Message(f"{other.name} cannot do the other side of "
                        f"{ACT_LABELS[act]}.", player.name)]
    story = partner_text(describe(player, act, role, rng, direction),
                         other.name)
    owed = titles_of(home).get(other.id) or titles_of(home).get(player.id)
    opener = "" if owed else family_open(player, other, rng)
    lines = [rng.choice(SETTINGS).format(a=player.name, b=other.name),
             partner_line(act, role, player, other, rng)]
    if opener:
        lines.append(opener)
    lines.append(f"💞 {story}")
    lines += feeding_lines(act, role, player, other, options)
    found, expecting = pregnancy_lines(act, role, player, other, options,
                                       rng)
    lines += found
    satisfy(player.needs, INTIMACY_RELIEF)
    mood_lines, mood = ([], 0)
    if other.npc:
        mood_lines, mood = reaction(other, player, role == "receive"
                                    and act in DOMINANT_ACTS)
        lines += mood_lines
        home["mood_delta"] = mood
    if other.npc and not is_regular(other):
        extra = 1 if act in DOMINANT_ACTS else 0
        note = bump(other, player, max(0, INTIMACY_BOND + extra + mood))
        if note:
            lines.append(note.strip())
    if expecting and not is_regular(other):
        listed = home.setdefault("expecting", [])
        if other.id not in listed:
            listed.append(other.id)
    closing = family_close(player, other, rng) if opener else ""
    if closing:
        lines.append(closing)
    called = title_line(home, player, other, rng)
    if called:
        lines.append(called)
    lines.append(rng.choice(AFTERGLOW).format(a=player.name,
                                              b=other.name))
    repository.save(player)
    if not is_regular(other):
        repository.save(other)
    return [Message("\n".join(lines))]

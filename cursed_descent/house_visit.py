import random
import time
from typing import Any

from .config import (
    HOUSE_HOLD_ACTS, HOUSE_HOLD_SECONDS, HOUSE_RELEASE_BASE, HOUSE_RELEASE_STEP, HOUSE_ACTIONS, HOUSE_FAMILY_CHANCE, HOUSE_GUEST_CHANCE, HOUSE_MATE_POINTS,
    HOUSE_OWNER_HOME, INTIMACY_MIN_AGE,
)
from .home_practice import other_role, parse_practice, practice
from .house_regulars import (
    PREFIX as PREFIX_REG, SavingOnly, is_regular, regular_by_id)
from .house_titles import order_title, parse_title
from .content import ITEMS
from .models import Message, Player
from .orientation import likes_of
from .needs import satisfy
from .npcs.talk import town_company
from .party_talk import banter
from .preferences import prefs_of
from .town_buildings.chat import chat, friendship, split_topic
from .town_buildings.brothel.practices import can_do
from .town_buildings.brothel.practices_content import (
    ACT_LABELS, DOMINANT_ACTS,
)
from .towns.last_light_humans.cafe.guests import DEADLY
from .towns.last_light_humans.cafe.vore import outcome_from, vore_roll
from .town_buildings.bodies import body_line as size_line
from .town_buildings.regular_body import body_line as shape_line
from .town_buildings.regular_talk import regular_talk


KEY = "house_visit"
ACTION_WORDS = tuple(HOUSE_ACTIONS)
USAGE = ("At a house: [house look], [house talk <name>], "
         + ", ".join(f"[house {word}]" for word in ACTION_WORDS)
         + ", [house sex <name>], [house back], [house leave].")
HOUSES = {
    "cafe": "A tidy house that smells of tea, lavender and old upholstery. "
            "The drawing room is dominated by a wide, well-used armchair.",
    "brothel": "Heavy curtains, a red lamp by the door and a bed that has "
               "seen more than its share of evenings.",
    "default": "A modest house: a table, a few chairs, a bed upstairs and a "
               "tub behind a screen.",
}
PLACES = {
    "event": "You walk out to {place}. Getting there and back is no "
             "trouble at all.",
    "town": "You walk to {place}.",
}
ARRIVE_HOME = (
    "{name} opens the door and lets you in. 'Come, make yourself at home.'",
    "{name} is at home and waves you into the hall with a smile.",
)
ARRIVE_EMPTY = (
    "Nobody answers. The door is on the latch, so you let yourself in "
    "and look around the empty rooms.",
    "The house is quiet – {name} seems to be out. You step inside anyway.",
)
FAMILY_LINES = (
    "{name} nods politely and goes back to what they were doing.",
    "{name} gives you a long look and says nothing.",
)
ACTION_TEXTS = {
    "eat": ("{host} sets a plate in front of you. 'Eat, you look hungry.'",
            "You raid the pantry and eat whatever you find."),
    "sleep": ("{host} shows you a bed. You sleep deeply under their roof.",
              "You find a spare bed and sleep, hoping nobody minds."),
    "rest": ("You sit with {host} for a while and rest your feet.",
             "You drop into a chair and rest for a while."),
    "relax": ("{host} pours tea and you both let the hours drift by.",
              "You stretch out on the sofa and let the hours drift by."),
    "bathe": ("{host} fills the tub for you. The water is hot and the soap "
              "smells of lavender.",
              "You fill the tub yourself and soak until the water cools."),
}


FEMALE_TITLES = ("mistress", "herrin", "goddess", "madam", "mommy", "queen")
MALE_TITLES = ("master", "sir")
DEMANDS = (
    "{b} lets the silence stretch until you lower your eyes, then says, "
    "very softly: 'In this house you will call me {title}. Every time. "
    "Do we understand each other?' 'Yes, {title},' you answer.",
    "{b} takes {their} time looking you over. 'Manners first. You address "
    "me as {title}, and you will find me generous.' You swallow. "
    "'Yes, {title}.'",
    "'Before anything else,' {b} says, tilting your chin up with one "
    "finger, 'the proper word is {title}. Say it for me.' "
    "'{title},' you say, and mean it.",
)
YOURS = (
    "'Thank you, {title},' you breathe.",
    "'Yes, {title},' you whisper, not daring to look up.",
    "You add, almost reverently: '{title}.'",
)


WEAR = {
    "cafe": "a loose lavender house dress",
    "brothel": "a silk robe, loosely tied",
    "default": "plain, comfortable homewear",
}
DOING = {
    "owner": ("pouring tea at the table", "mending a dress by the window",
              "leafing through a book with {their} feet up",
              "stirring something on the stove", "tidying the rooms"),
    "visitor": ("leaning in the doorway with a cup in hand",
                "sitting on the sofa, legs crossed",
                "browsing the bookshelf"),
    "family": ("reading the paper in the corner",
               "polishing a pair of boots"),
    "player": ("settled in an armchair", "looking around the rooms"),
}


def wearing(other:Player, building:str) -> str:
    worn = [ITEMS[item]["name"] for item in other.equipment.values()
            if item in ITEMS][:3]
    return ", ".join(worn) if worn else WEAR.get(building, WEAR["default"])


def describe_person(entry:dict[str, str], other:Player | None,
                    state:dict[str, Any], rng:random.Random) -> str:
    kind = entry["kind"]
    if other is None:
        doing = rng.choice(DOING["family"])
        return (f"👁 {entry['name']} – family of the house, {doing}. "
                f"{entry['name']} nods without much interest.")
    their = "his" if other.gender == "Male" else "her"
    height = other.body.get("height", 0)
    weight = other.body.get("weight", 70)
    head = (f"👁 {other.name} – "
            + shape_line({"gender": other.gender,
                          "bust": other.body.get("bust", 0),
                          "endowment": other.body.get("endowment", 0)})
            + f". {size_line(other.age, height, weight)}.")
    look = other.profile.get("look", "")
    doing = rng.choice(DOING.get(kind, DOING["visitor"])).format(
        their=their)
    lines = [head]
    if look:
        lines.append(look)
    lines.append(f"{other.first_name or other.name} wears "
                 f"{wearing(other, state['building'])}.")
    lines.append(f"Right now {other.first_name or other.name} is {doing}.")
    likes = likes_of(other)
    if likes != "both":
        lines.append(f"{other.first_name or other.name} seems to prefer "
                     f"partners with a {likes}.")
    return "\n".join(lines)


def state_of(player:Player) -> dict[str, Any] | None:
    return player.profile.get(KEY) or None


def private(text:str, player:Player) -> list[Message]:
    return [Message(text, player.name)]


def describe_house(state:dict[str, Any]) -> str:
    base = HOUSES.get(state["building"], HOUSES["default"])
    return f"{base} ({state['address']})"


def others_here(player:Player, repository:Any,
                state:dict[str, Any]) -> list[dict[str, str]]:
    found = []
    for name in repository.names():
        if name == player.name:
            continue
        other = repository.load(name)
        theirs = state_of(other) if other is not None else None
        if theirs and theirs["host_id"] == state["host_id"]:
            found.append({"id": other.id, "name": other.name,
                          "kind": "player"})
    return found


def present(player:Player, repository:Any,
            state:dict[str, Any]) -> list[dict[str, str]]:
    return state["present"] + others_here(player, repository, state)


def entry_by_name(entries:list[dict[str, str]],
                  text:str) -> dict[str, str] | None:
    wanted = text.strip().casefold()
    if not wanted:
        return None
    for entry in entries:
        words = entry["name"].casefold().split()
        if wanted == entry["name"].casefold() or wanted in words:
            return entry
    return None


def person_of(entry:dict[str, str], repository:Any,
              regulars:Any) -> Player | None:
    if entry["kind"] == "family":
        return None
    if is_regular_id(entry["id"]):
        return regular_by_id(regulars, entry["id"])
    return repository.load_by_id(entry["id"])


def is_regular_id(entry_id:str) -> bool:
    return entry_id.startswith("reg:")


def enter(player:Player, host:Player, kind:str, building:str,
          address:str, display:str, married_to:str, repository:Any,
          rng:random.Random) -> tuple[list[Message], bool]:
    home = rng.random() < HOUSE_OWNER_HOME
    crowd: list[dict[str, str]] = []
    if home:
        crowd.append({"id": host.id, "name": host.name, "kind": "owner"})
        if married_to and rng.random() < HOUSE_FAMILY_CHANCE:
            crowd.append({"id": "", "name": married_to, "kind": "family"})
    if rng.random() < HOUSE_GUEST_CHANCE:
        locals_ = [npc for npc in town_company(repository)
                   if npc.id != host.id and npc.age >= INTIMACY_MIN_AGE]
        if locals_:
            guest = rng.choice(locals_)
            crowd.append({"id": guest.id, "name": guest.name,
                          "kind": "visitor"})
    state = {"kind": kind, "building": building, "host_id": host.id,
             "host": host.name, "address": display or address,
             "present": crowd, "sex_with": ""}
    player.profile[KEY] = state
    place = PLACES["event" if address.startswith("event:") else "town"]
    lines = [place.format(place=display or "their house")]
    lines.append(rng.choice(ARRIVE_HOME if home else ARRIVE_EMPTY).format(
        name=host.first_name or host.name))
    if home and dynamic_of(player, host, state) == "npc":
        lines.append(demand_title(player, host, rng))
    others = [entry["name"] for entry in present(player, repository, state)
              if entry["kind"] != "owner"]
    if others:
        lines.append("Also here: " + ", ".join(others) + ".")
    repository.save(player)
    return [Message("\n".join(lines), player.name)], home


def sexual_partner(player:Player, entry:dict[str, str], other:Player
                   ) -> str:
    if min(player.age, other.age) < INTIMACY_MIN_AGE:
        return f"{other.name} is not available."
    if (other.npc and not is_regular(other)
            and friendship(other, player) < HOUSE_MATE_POINTS):
        return f"{other.first_name} smiles politely. 'Not yet.'"
    return ""


def role_of(other:Player, state:dict[str, Any]) -> str:
    role = prefs_of(other)["role"]
    if role == "switch" and is_regular(other) and state["building"] == "cafe":
        return "dom"
    return role


def dynamic_of(player:Player, other:Player, state:dict[str, Any]) -> str:
    mine, theirs = prefs_of(player)["role"], role_of(other, state)
    if mine == "dom" and theirs == "sub":
        return "player"
    if mine == "sub" and theirs == "dom":
        return "npc"
    return ""


def options_for(player:Player, other:Player) -> list[tuple[str, str]]:
    return [(act, role) for act in ACT_LABELS for role in ("give", "receive")
            if can_do(player.gender, act, role, player.body)
            and can_do(other.gender, act, other_role(role), other.body)]


def pick_for(player:Player, other:Player, rng:random.Random,
             dominant:bool) -> tuple[str, str] | None:
    found = options_for(player, other)
    flow = prefs_of(other)["flow"]
    liked = [pair for pair in found
             if ("G" if pair[1] == "receive" else "T")
             in flow.get(pair[0], "")]
    pool = liked or found
    if dominant:
        pool = [pair for pair in pool if pair[1] == "receive"
                and pair[0] in DOMINANT_ACTS] or [
            pair for pair in pool if pair[1] == "receive"] or pool
    return rng.choice(pool) if pool else None


def demand_title(player:Player, other:Player, rng:random.Random) -> str:
    calls = player.profile.setdefault("i_call", {})
    if other.id in calls:
        return ""
    pool = MALE_TITLES if other.gender == "Male" else FEMALE_TITLES
    title = rng.choice(pool)
    calls[other.id] = title
    their = "his" if other.gender == "Male" else "her"
    return rng.choice(DEMANDS).format(
        b=other.first_name or other.name, title=title.capitalize(),
        their=their)


HELD_BLOCKED = ("leave", "back", "eat", "sleep", "rest", "relax", "bathe")
PINNED = (
    "{name} does not move an inch. 'Leave? I decide when this is over.' "
    "You can't shift under {their} weight.",
    "{name} tightens {their} thighs and hums. 'Not yet, little seat.'",
)
RELEASED = ("{name} finally lifts {their} weight off you with a lazy sigh: "
            "'Fine. You may go – for now.'")


def pinned(player:Player, state:dict[str, Any], repository:Any,
           rng:random.Random) -> list[Message]:
    state["held_tries"] = state.get("held_tries", 0) + 1
    chance = HOUSE_RELEASE_BASE + HOUSE_RELEASE_STEP * (
        state["held_tries"] - 1)
    name = state["held_by"]
    their = "their"
    if rng.random() < chance:
        state["held_by"] = ""
        state["held_tries"] = 0
        repository.save(player)
        return private(RELEASED.format(name=name, their=their), player)
    repository.save(player)
    return private(rng.choice(PINNED).format(name=name, their=their),
                   player)


HOLD_UPDATES = (
    "{name} shifts and settles again, keeping you exactly where you are.",
    "{name} hums contentedly and takes {their} time with you.",
    "You cannot move. {name} presses down and does not hurry.",
    "{name} lazily checks on you: 'Still there? Good.'",
    "A minute passes under {name}. {name} is clearly in no rush.",
    "{name} grinds down slowly and watches you squirm.",
)


def hold_update(player:Player, rng:random.Random) -> list[Message]:
    state = state_of(player)
    if state is None or not state.get("held_by"):
        return []
    return private(rng.choice(HOLD_UPDATES).format(
        name=state["held_by"], their="their"), player)


def release(player:Player, repository:Any) -> list[Message]:
    state = state_of(player)
    if state is None or not state.get("held_by"):
        return []
    name = state["held_by"]
    state["held_by"] = ""
    state["held_tries"] = 0
    repository.save(player)
    return private(RELEASED.format(name=name, their="their"), player)


def leave(player:Player, repository:Any) -> list[Message]:
    state = player.profile.pop(KEY, None)
    repository.save(player)
    if state is None:
        return private("You are not visiting anybody.", player)
    return private(f"You say goodbye and walk back from {state['address']}.",
                   player)


def do_action(player:Player, word:str, state:dict[str, Any],
              repository:Any, rng:random.Random) -> list[Message]:
    entries = state["present"]
    hosted = any(entry["kind"] == "owner" for entry in entries)
    texts = ACTION_TEXTS[word]
    first = state["host"].split()[0]
    text = texts[0].format(host=first) if hosted else texts[1]
    satisfy(player.needs, HOUSE_ACTIONS[word])
    if word == "bathe":
        player.sweat = 0
    repository.save(player)
    return private(text, player)


def house_command(player:Player, args:list[str], repository:Any,
                  rng:random.Random, regulars:Any) -> list[Message]:
    state = state_of(player)
    if state is None:
        return private("You are not at anybody's house. [visit <name>] "
                       "– see [regulars].", player)
    word = args[0].casefold() if args else "look"
    rest = args[1:]
    if state.get("held_by") and word in HELD_BLOCKED:
        return pinned(player, state, repository, rng)
    if word in ("look", "examine") and rest:
        entry = entry_by_name(present(player, repository, state),
                              " ".join(rest))
        if entry is None:
            return private(f"Nobody called '{' '.join(rest)}' is here.",
                           player)
        return private(describe_person(
            entry, person_of(entry, repository, regulars), state, rng),
            player)
    if word in ("look", "examine"):
        names = [f"{entry['name']}" for entry in
                 present(player, repository, state)]
        crowd = ("Present: " + ", ".join(names) + "." if names
                 else "Nobody is here.")
        return private(f"{describe_house(state)}\n{crowd}", player)
    if word == "leave":
        return leave(player, repository)
    if word == "back":
        state["sex_with"] = ""
        repository.save(player)
        return private("You leave the bedroom and return to the rooms.",
                       player)
    if word in ACTION_WORDS:
        return do_action(player, word, state, repository, rng)
    if word not in ("talk", "sex", "practice", "order"):
        return private(USAGE, player)
    name_words = parse_practice(rest)[0] if word == "practice" else rest
    title = ""
    if word == "order":
        name_words, title = parse_title(rest)
    topic = ""
    if word == "talk":
        text, topic = split_topic(rest)
        name_words = text.split()
    entry = entry_by_name(present(player, repository, state),
                          " ".join(name_words))
    if entry is None:
        return private(f"Nobody called '{' '.join(name_words)}' is here.",
                       player)
    other = person_of(entry, repository, regulars)
    if other is None:
        if word == "talk":
            return private(rng.choice(FAMILY_LINES).format(
                name=entry["name"]), player)
        return private(f"{entry['name']} is not available.", player)
    saver = SavingOnly(repository) if is_regular(other) else repository
    if word == "talk":
        if is_regular(other):
            building = other.id[4:].partition(":")[0]
            record = regulars.get(building, other.name) or {"name": other.name}
            return private(regular_talk(record, building, rng), player)
        if other.npc:
            messages = chat(player, other, topic, rng)
            repository.save(other)
            return messages
        return banter(player, other, topic, rng)
    refusal = sexual_partner(player, entry, other)
    if refusal:
        return private(refusal, player)
    mood = dynamic_of(player, other, state)
    calls_me = player.profile.setdefault("calls_me", {})
    if word == "order":
        if mood != "player":
            return private("Only a dominant player can order an NPC "
                           "to use a title.", player)
        return order_title(player, {"titles": calls_me}, other, title,
                           saver, rng)
    if word == "sex":
        state["sex_with"] = entry["name"]
        state["dynamic"] = mood
        wish = pick_for(player, other, rng, False) if mood == "player" else None
        state["wish"] = list(wish) if wish else []
        repository.save(player)
        text = f"You and {entry['name']} withdraw to a quiet room."
        if mood == "player":
            text += (f" {other.first_name} is yours to command – but "
                     f"{other.first_name} has wishes"
                     + (f": {ACT_LABELS[wish[0]]}." if wish else "."))
        if mood == "npc":
            text += (f" {other.first_name} is in charge here: you may "
                     f"suggest, but {other.first_name} decides.")
            text += "\n" + demand_title(player, other, rng)
        return private(text.strip(), player)
    practice_args = rest[len(name_words):]
    intro = ""
    if mood == "npc":
        _, act, role, options, direction = parse_practice(practice_args)
        chosen = pick_for(player, other, rng, True)
        if chosen is not None:
            practice_args = [chosen[0], chosen[1], options["amount"],
                             options["where"]] + ([direction]
                                                  if direction else [])
            intro = (f"{other.first_name} ignores your suggestion and "
                     f"decides: {ACT_LABELS[chosen[0]]}.\n")
    home = {"residents": [], "guests": [], "titles": calls_me}
    messages = practice(player, other, home, practice_args, saver, rng)
    if is_regular(other) and home.get("mood_delta"):
        regulars.mood(other.id[len(PREFIX_REG):].partition(":")[0],
                      other.name, home["mood_delta"])
    fate = vore_roll(outcome_from(other.profile), rng, DEADLY["on"])
    if fate and messages:
        player.profile["house_fate"] = fate
    _, held_act, held_role, *_ = parse_practice(practice_args)
    if (held_act in HOUSE_HOLD_ACTS and held_role == "receive" and messages
            and mood != "player"):
        state["held_by"] = other.first_name or other.name
        state["held_tries"] = 0
        state["held_until"] = time.time() + rng.uniform(
            *HOUSE_HOLD_SECONDS)
        player.profile[KEY] = state
        saver.save(player)
        messages.append(Message(
            f"{state['held_by']} holds you pinned. You will leave when "
            f"{state['held_by']} decides.", player.name))
    title = player.profile.get("i_call", {}).get(other.id, "")
    if mood == "npc" and title and messages:
        intro += rng.choice(YOURS).format(title=title.capitalize()) + "\n"
    if intro and messages:
        messages[0] = Message(intro + messages[0].text, messages[0].recipient)
    return messages

import random
from typing import Any

from ..body import bust_label
from ..config import (
    HUNG_GENDERS, REGULAR_BANNED_GENDERS, REGULAR_BUST_RANGE,
    REGULAR_ENDOWMENT_RANGE, REGULAR_FLAT_BUST_RANGE,
    REGULAR_GENDER_WEIGHTS, REGULAR_SMELL_MAX, REGULAR_SMELL_START,
    REGULAR_SMELL_WORDS,
)


FLAT_GENDERS = ("Male",)
BODY_KEYS = ("gender", "bust", "endowment")
FAMILY_ROLES = ("spouse", "son", "girlfriend")


def random_gender(building:str, rng:random.Random) -> str:
    weights = REGULAR_GENDER_WEIGHTS[building]
    return rng.choices(list(weights), list(weights.values()))[0]


def body_values(building:str, name:str,
                gender:str="") -> dict[str, Any]:
    rng = random.Random(f"{building}:{name.casefold()}")
    drawn = random_gender(building, rng)
    gender = gender or drawn
    bust_range = (REGULAR_FLAT_BUST_RANGE if gender in FLAT_GENDERS
                  else REGULAR_BUST_RANGE[building])
    endowment = (rng.randint(*REGULAR_ENDOWMENT_RANGE)
                 if gender in HUNG_GENDERS else 0)
    values = {"gender": gender, "bust": rng.randint(*bust_range),
              "endowment": endowment,
              "sweat": rng.randint(*REGULAR_SMELL_START),
              "musk": rng.randint(*REGULAR_SMELL_START)}
    if building == "cafe":
        from ..towns.last_light_humans.cafe.ambient import GIRLFRIENDS
        from ..towns.last_light_humans.cafe.stools import NAMES
        values["son"] = rng.choice(NAMES)
        values["girlfriend"] = rng.choice(GIRLFRIENDS)
    return values


def complete(building:str, record:dict[str, Any]) -> dict[str, Any]:
    if record.get("gender") in REGULAR_BANNED_GENDERS.get(building, ()):
        record = {key: value for key, value in record.items()
                  if key not in BODY_KEYS}
    if "cruel" in record:
        record = dict(record, cruel=max(0, min(2, int(record["cruel"]))))
    missing = {key: value
               for key, value in body_values(building, record["name"]).items()
               if key not in record}
    return dict(record, **missing)


def drift(record:dict[str, Any]) -> dict[str, Any]:
    rng = random.Random(f"{record['name']}:{record.get('visits', 1)}")
    changed = dict(record)
    for key in ("sweat", "musk"):
        if key in record:
            changed[key] = min(REGULAR_SMELL_MAX,
                               max(0, record[key] + rng.choice((-1, 0, 1))))
    return changed


def smell_word(level:int) -> str:
    steps = len(REGULAR_SMELL_WORDS) - 1
    return REGULAR_SMELL_WORDS[round(level / REGULAR_SMELL_MAX * steps)]


def family_text(record:dict[str, Any]) -> str:
    parts = [f"{role} {record[role]}" for role in FAMILY_ROLES
             if record.get(role)]
    return "Family: " + ", ".join(parts) if parts else ""


def body_line(record:dict[str, Any]) -> str:
    if "gender" not in record:
        return ""
    parts = [record["gender"]]
    if record.get("bust", 0) > 0:
        parts.append(f"{bust_label(record['bust'])} bust "
                     f"({round(record['bust'])} cc)")
    if record.get("endowment", 0) > 0:
        parts.append(f"{record['endowment']} cm")
    if "sweat" in record:
        parts.append(f"sweat {smell_word(record['sweat'])}")
    if "musk" in record:
        parts.append(f"musk {smell_word(record['musk'])}")
    line = ", ".join(parts)
    family = family_text(record)
    return f"{line}. {family}" if family else line


SWEAT_NOTES = (
    "", "",
    "{name} is a little damp at the collar.",
    "{name} is sweating through the fabric, and you can feel the heat "
    "coming off her.",
    "{name} is drenched in sweat; it runs down and everything clings.",
)
MUSK_NOTES = (
    "", "",
    "A faint musk follows {name} into the room.",
    "{name} carries a thick, warm musk you cannot ignore.",
    "{name}'s musk is so heavy that every breath tastes of her.",
)


def smell_tier(level:int) -> int:
    return min(len(SWEAT_NOTES) - 1, level * len(SWEAT_NOTES)
               // (REGULAR_SMELL_MAX + 1))


def smell_note(name:str, sweat:int, musk:int) -> str:
    notes = (SWEAT_NOTES[smell_tier(sweat)], MUSK_NOTES[smell_tier(musk)])
    return " ".join(note.format(name=name) for note in notes if note)


def smell_of(building:str, name:str) -> tuple[int, int]:
    values = body_values(building, name)
    return values["sweat"], values["musk"]

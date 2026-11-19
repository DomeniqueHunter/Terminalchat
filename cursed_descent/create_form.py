import re
from dataclasses import dataclass, field
from typing import Any

from .body import default_body
from .body_creation import fields_for, parse_body_input
from .config import (
    CREATE_GENDERS, FLIST_PREFIX, FORM_NAME_MAX, FORM_TEXT_MAX, MAX_AGE,
    MIN_AGE, START_FREE_POINTS, START_STAT_VALUE, STAT_NAMES,
)
from .creation import playable_races
from .models import Player
from .orientation import LIKES


NAME_PATTERN = re.compile(r"^[^\W\d_](?:[^\W\d_]|[ '-])*$")
FLIST_PATTERN = re.compile(r"^(?:[A-Za-z0-9 _.'~+-]|%[0-9A-Fa-f]{2}){1,120}$")
CONTROL = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")
NUMERIC_BODY = ("height", "weight", "bust", "fake", "muscle", "butt",
                "endowment", "girth", "balls")
CHOICE_BODY = ("build", "shape")
FORM_PREFIX = "cf_"


@dataclass
class FormResult:
    player: Player
    errors: list[str] = field(default_factory=list)
    points_left: int = START_FREE_POINTS
    fields: dict[str, str] = field(default_factory=dict)


class Problems:
    def __init__(self) -> None:
        self.fields: dict[str, str] = {}

    def add(self, key:str, message:str) -> None:
        self.fields.setdefault(f"{FORM_PREFIX}{key}", message)


def clean_text(value:Any) -> str:
    return CONTROL.sub("", str(value or "")).strip()


def clean_name(value:str, key:str, label:str, problems:Problems,
               required:bool) -> str:
    value = " ".join(clean_text(value).split())
    if not value:
        if required:
            problems.add(key, f"{label} is required.")
        return ""
    if len(value) > FORM_NAME_MAX or not NAME_PATTERN.match(value):
        problems.add(key, f"{label}: letters only (plus space, ' and -), "
                          f"at most {FORM_NAME_MAX} characters.")
        return ""
    return value


def clean_flist(value:str, problems:Problems) -> str:
    value = clean_text(value)
    if not value:
        return ""
    name = value[len(FLIST_PREFIX):] if value.startswith(FLIST_PREFIX) else ""
    if not name or not FLIST_PATTERN.match(name):
        problems.add("flist", f"F-List link: use {FLIST_PREFIX}<name>.")
        return ""
    return FLIST_PREFIX + name


def clean_long(value:str, key:str, label:str, problems:Problems) -> str:
    text = clean_text(value)
    if len(text) > FORM_TEXT_MAX:
        problems.add(key, f"{label}: at most {FORM_TEXT_MAX} characters "
                          f"({len(text)} given).")
        return ""
    return text


def read_stats(data:dict[str, str], problems:Problems
               ) -> tuple[dict[str, int], int]:
    stats: dict[str, int] = {}
    for stat in STAT_NAMES:
        raw = clean_text(data.get(f"{FORM_PREFIX}stat_{stat}", "0"))
        if not raw.isdigit():
            problems.add(f"stat_{stat}", f"{stat.capitalize()}: please "
                                         f"give a whole number.")
            raw = "0"
        stats[stat] = int(raw)
    left = START_FREE_POINTS - sum(stats.values())
    if left != 0:
        for stat in STAT_NAMES:
            problems.add(f"stat_{stat}", f"Distribute exactly "
                                         f"{START_FREE_POINTS} stat points "
                                         f"({left} left).")
    return stats, left


def apply_field(body:dict[str, Any], gender:str, key:str, value:str,
                problems:Problems) -> dict[str, Any]:
    result = parse_body_input(f"{key} {value.replace(' ', '')}", body,
                              gender)
    if isinstance(result, str):
        lines = [line for line in result.splitlines()
                 if line and not line.startswith("Several values")]
        problems.add(key, lines[0] if lines else f"Invalid {key}.")
        return body
    return result


def read_body(data:dict[str, str], gender:str, race,
              problems:Problems) -> dict[str, Any]:
    body = default_body()
    length, girth, balls = race.member
    body.update(endowment=length, girth=girth, balls=balls,
                endowment_shape=race.member_shape)
    allowed = set(fields_for(gender)) | {"fake"}
    for key in CHOICE_BODY[:1] + NUMERIC_BODY + CHOICE_BODY[1:]:
        value = clean_text(data.get(f"{FORM_PREFIX}{key}", ""))
        if value and key in allowed:
            body = apply_field(body, gender, key, value, problems)
    for key, (low, high) in (("height", race.height),
                             ("weight", race.weight)):
        if not low <= body[key] <= high:
            problems.add(key, f"{key.capitalize()} must be {low}-{high} "
                              f"for a {race.name}.")
            body[key] = min(max(body[key], low), high)
    return body


def evaluate(data:dict[str, str], repository:Any=None) -> FormResult:
    problems = Problems()
    first = clean_name(data.get(f"{FORM_PREFIX}first", ""), "first",
                       "First name", problems, True)
    last = clean_name(data.get(f"{FORM_PREFIX}last", ""), "last",
                      "Last name", problems, False)
    gender = clean_text(data.get(f"{FORM_PREFIX}gender", ""))
    if gender not in CREATE_GENDERS:
        problems.add("gender", "Please choose a gender.")
        gender = CREATE_GENDERS[0]
    races = playable_races()
    race_key = clean_text(data.get(f"{FORM_PREFIX}race", "human")) or "human"
    if race_key not in races:
        problems.add("race", "Please choose a race.")
        race_key = next(iter(races))
    race = races[race_key]
    age_text = clean_text(data.get(f"{FORM_PREFIX}age", ""))
    age = int(age_text) if age_text.isdigit() else 0
    if not MIN_AGE <= age <= MAX_AGE:
        problems.add("age", f"Age must be {MIN_AGE} to {MAX_AGE}.")
        age = min(max(age, MIN_AGE), MAX_AGE)
    body = read_body(data, gender, race, problems)
    stats, left = read_stats(data, problems)
    personality = clean_long(data.get(f"{FORM_PREFIX}personality", ""),
                             "personality", "Personality", problems)
    look = clean_long(data.get(f"{FORM_PREFIX}look", ""), "look",
                      "Appearance", problems)
    flist = clean_flist(data.get(f"{FORM_PREFIX}flist", ""), problems)
    likes = clean_text(data.get(f"{FORM_PREFIX}orientation", "both"))
    if likes not in LIKES:
        problems.add("orientation", "Please choose an orientation.")
        likes = "both"
    handle = " ".join(part for part in (first, last) if part) or "New"
    if repository is not None and first:
        handle = repository.unique_handle(handle)
    player = Player(name=handle, gender=gender, free_points=0, body=body,
                    first_name=first, last_name=last, race=race_key,
                    age=age, personality=personality)
    for stat, value in stats.items():
        player.stats[stat] = START_STAT_VALUE + value
    player.profile["orientation"] = likes
    if look:
        player.profile["look"] = look
    if flist:
        player.profile["flist"] = flist
    errors = list(dict.fromkeys(problems.fields.values()))
    return FormResult(player, errors, left, problems.fields)

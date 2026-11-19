from typing import Any

from ..body import BUILDS, CREATION_LIMITS, ENDOWMENT_SHAPES, default_body
from ..config import (
    CREATE_GENDERS, DEFAULT_AGE, FLIST_PREFIX, FORM_NAME_MAX, FORM_TEXT_MAX,
    HUNG_GENDERS, MAX_AGE, MIN_AGE, START_FREE_POINTS, STAT_NAMES,
)
from ..create_form import FORM_PREFIX, evaluate
from ..creation import playable_races
from .tabs import figure_svg


START_SPLIT = (3, 3, 2, 2)


def form_context() -> dict[str, Any]:
    body = default_body()
    races = list(playable_races().values())
    length, girth, balls = races[0].member
    limits = dict(CREATION_LIMITS)
    limits["height"] = races[0].height
    limits["weight"] = races[0].weight
    return {
        "limits": limits,
        "genders": CREATE_GENDERS, "races": races, "builds": BUILDS,
        "shapes": ENDOWMENT_SHAPES, "min_age": MIN_AGE, "max_age": MAX_AGE,
        "default_age": DEFAULT_AGE, "points": START_FREE_POINTS,
        "name_max": FORM_NAME_MAX, "text_max": FORM_TEXT_MAX,
        "flist": FLIST_PREFIX, "hung_genders": sorted(HUNG_GENDERS),
        "stats": [{"key": stat, "title": stat.capitalize(), "value": value}
                  for stat, value in zip(STAT_NAMES, START_SPLIT)],
        "body": {"height": body["height"], "weight": body["weight"],
                 "build": body.get("build", "Average"),
                 "bust": body.get("bust", 0),
                 "muscle": body.get("muscle", 25),
                 "butt": body.get("butt", 95)},
        "hung": {"length": length, "girth": girth, "balls": balls,
                 "shape": races[0].member_shape},
    }


def form_values(data:dict[str, Any]) -> dict[str, str]:
    return {key: str(value) for key, value in data.items()
            if key.startswith(FORM_PREFIX)}


def preview(data:dict[str, Any], strict:bool=False
            ) -> tuple[str, int, list[str], list[str]]:
    result = evaluate(form_values(data))
    keys = [key for key, _ in result.fields.items()
            if strict or (str(data.get(key, "")).strip()
                          and not key.startswith(f"{FORM_PREFIX}stat_"))]
    messages = list(dict.fromkeys(result.fields[key] for key in keys))
    return figure_svg(result.player), result.points_left, messages, keys

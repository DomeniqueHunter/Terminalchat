import math
from typing import Any

from .config import HUNG_GENDERS


BUILDS = ("Thin", "Slim", "Average", "Toned", "Muscular", "Curvy", "Chubby",
          "Heavy")
BREAST_SIZES = ("None", "Flat", "Small", "Medium", "Large", "Huge",
                "Massive")
DEFAULT_BODY = {"height": 170, "weight": 65, "build": "Average",
                "breasts": "None"}

BUST_CC = {"None": 0, "Flat": 50, "Small": 150, "Medium": 300, "Large": 500,
           "Huge": 800, "Massive": 1200}
BUST_OVERFLOW_NAMES = ((6400, "Planetary"), (3200, "Titanic"),
                       (1800, "Colossal"))
MUSCLE_DEFAULT = {"Muscular": 70, "Toned": 45, "Heavy": 30, "Average": 25,
                  "Curvy": 20, "Slim": 15, "Chubby": 15, "Thin": 8}
BUTT_DEFAULT = {"Thin": 82, "Slim": 88, "Average": 95, "Toned": 96,
                "Muscular": 100, "Curvy": 108, "Chubby": 108, "Heavy": 112}
DEFAULT_BALLS = 5
GIRTH_RATIO = 0.8
GROWTH_PARTS = ("height", "weight", "bust", "muscle", "butt", "endowment",
                "girth", "balls")
HEIGHT_GROWTH_START = 220
CREATION_LIMITS = {"height": (100, 250), "weight": (30, 200),
                   "bust": (0, 1200), "fake": (0, 1200), "muscle": (0, 100),
                   "butt": (60, 140), "endowment": (4, 40), "girth": (4, 30),
                   "balls": (2, 12)}

SIZE_CLASSES = (
    (140, "tiny"),
    (160, "short"),
    (180, "average"),
    (200, "tall"),
    (10_000, "huge"),
)
SIZE_EFFECTS = {
    "tiny": {"hp": -10, "melee": -0.10, "dodge": 0.06},
    "short": {"hp": -5, "melee": -0.05, "dodge": 0.03},
    "average": {},
    "tall": {"hp": 5, "melee": 0.05, "dodge": -0.02},
    "huge": {"hp": 10, "melee": 0.10, "dodge": -0.04},
}
BUILD_EFFECTS = {
    "Thin": {"hp": -10, "dodge": 0.04},
    "Slim": {"dodge": 0.03},
    "Average": {},
    "Toned": {"melee": 0.03, "dodge": 0.01},
    "Muscular": {"melee": 0.08, "dodge": -0.01},
    "Curvy": {"hp": 5, "discount": 0.05, "allure": 1},
    "Chubby": {"hp": 15, "armor": 2, "dodge": -0.02},
    "Heavy": {"hp": 25, "armor": 4, "dodge": -0.04},
}
BREAST_EFFECTS = {
    "Large": {"discount": 0.05, "allure": 1},
    "Huge": {"discount": 0.05, "allure": 1},
    "Massive": {"discount": 0.05, "allure": 2},
}

ENDOWMENT_SHAPES = ("Human", "Equine", "Canine", "Draconic", "Stout",
                    "Clockwork", "Knobbed")
BUST_CM = {"None": 82, "Flat": 84, "Small": 88, "Medium": 94, "Large": 102,
           "Huge": 115, "Massive": 132}
DEFAULT_ENDOWMENT = 15


MUSCLE_BUILD_BONUS = {"Muscular": 8, "Toned": 4, "Heavy": 2, "Slim": -2,
                      "Chubby": -2, "Thin": -4}
MUSCLE_TIERS = ((18, "leather"), (11, "velvet"), (-99, "silk"))


def muscle_baseline(build:str) -> int:
    return MUSCLE_DEFAULT.get(build, 25)


def muscle_tier(stats:dict[str, int], build:str | dict[str, Any]) -> str:
    if isinstance(build, dict):
        extra = round((build.get("muscle", muscle_baseline(build["build"]))
                       - muscle_baseline(build["build"])) / 10)
        build = build["build"]
    else:
        extra = 0
    score = stats["strength"] + MUSCLE_BUILD_BONUS.get(build, 0) + extra
    for limit, tier in MUSCLE_TIERS:
        if score >= limit:
            return tier
    return "silk"


def size_class(height:int) -> str:
    for limit, label in SIZE_CLASSES:
        if height < limit:
            return label
    return "huge"


def default_body() -> dict[str, Any]:
    return normalize_body(dict(DEFAULT_BODY))


def bust_tier(cc:float) -> str:
    tier = "None"
    for name, limit in BUST_CC.items():
        if cc >= limit:
            tier = name
    return tier


def bust_label(cc:float) -> str:
    for limit, name in BUST_OVERFLOW_NAMES:
        if cc >= limit:
            return name
    return bust_tier(cc)


def fake_amount(body:dict[str, Any], part:str) -> int:
    return min(body.get("fake", {}).get(part, 0), body.get(part, 0))


def normalize_body(body:dict[str, Any]) -> dict[str, Any]:
    build = body.get("build", "Average")
    if "bust" not in body:
        body["bust"] = BUST_CC.get(body.get("breasts", "None"), 300)
    body.setdefault("muscle", muscle_baseline(build))
    body.setdefault("butt", BUTT_DEFAULT.get(build, 95))
    body.setdefault("endowment", DEFAULT_ENDOWMENT)
    body.setdefault("girth", round(body["endowment"] * GIRTH_RATIO))
    body.setdefault("balls", DEFAULT_BALLS)
    body["fake"] = {part: min(amount, body.get(part, 0))
                    for part, amount in body.get("fake", {}).items()
                    if amount > 0}
    body["breasts"] = bust_tier(body["bust"])
    body["breasts_real"] = bust_tier(body["bust"] - fake_amount(body, "bust"))
    return body


def bust_cm(body:dict[str, Any]) -> int:
    cc = body.get("bust", BUST_CC.get(body["breasts"], 300))
    if cc <= BUST_CC["Massive"]:
        base = BUST_CM.get(bust_tier(cc), 94)
    else:
        base = BUST_CM["Massive"] + 20 * math.log2(cc / BUST_CC["Massive"])
    return round(base * body["height"] / 170)


def apply_body_mods(body:dict[str, Any],
                    mods:dict[str, Any]) -> dict[str, Any]:
    if "breasts" in mods and "bust" not in mods:
        mods["bust"] = BUST_CC.get(mods.pop("breasts"), 300)
    else:
        mods.pop("breasts", None)
    if "bust" in mods:
        body.pop("bust", None)
    body.update(mods)
    return normalize_body(body)


def growth_effect(body:dict[str, Any], key:str) -> float:
    if key == "hp":
        return 5 * max(0.0, math.log2(max(1, body["height"]
                                          / HEIGHT_GROWTH_START)))
    if key == "melee":
        base = muscle_baseline(body["build"])
        return 0.12 * math.tanh((body.get("muscle", base) - base) / 60)
    octaves = max(0.0, math.log2(max(1.0, body.get("bust", 0)
                                     / BUST_CC["Massive"])))
    if key == "allure":
        butt = body.get("butt", 95) - BUTT_DEFAULT.get(body["build"], 95)
        cock = max(0, body.get("endowment", DEFAULT_ENDOWMENT) - 25)
        return (math.floor(octaves) + math.floor(max(0, butt) / 15)
                + math.floor(cock / 10))
    if key == "discount":
        return min(0.02 * octaves, 0.15)
    if key == "dodge":
        return -0.02 * octaves
    return 0.0


def body_effect(body:dict[str, Any], key:str) -> float:
    effects = (SIZE_EFFECTS[size_class(body["height"])],
               BUILD_EFFECTS.get(body["build"], {}),
               BREAST_EFFECTS.get(body["breasts"], {}))
    return (sum(effect.get(key, 0) for effect in effects)
            + growth_effect(body, key))


def shape_of(gender:str, body:dict[str, Any]) -> str:
    if gender not in HUNG_GENDERS:
        return ""
    return body.get("endowment_shape", "Human")


def body_text(body:dict[str, Any]) -> str:
    cc = body.get("bust", BUST_CC.get(body["breasts"], 300))
    breasts = "" if cc <= 0 else f", {bust_label(cc)} bust ({round(cc)} cc)"
    extra = (f", muscle {body['muscle']}, butt {body['butt']} cm"
             if "muscle" in body and "butt" in body else "")
    drained = body.get("drained", {})
    marks = f", drained: {', '.join(drained.values())}" if drained else ""
    return (f"{body['height']} cm ({size_class(body['height'])}), "
            f"{body['weight']} kg, {body['build']}{breasts}{extra}{marks}")


def effects_text(body:dict[str, Any]) -> str:
    parts: list[str] = []
    for key, label, percent in (("hp", "HP", False), ("melee", "melee", True),
                                ("dodge", "dodge", True),
                                ("armor", "armor", False),
                                ("allure", "allure", False),
                                ("discount", "shop discount", True)):
        value = body_effect(body, key)
        if value:
            shown = f"{value * 100:+.0f}%" if percent else f"{value:+.0f}"
            parts.append(f"{shown} {label}")
    return ", ".join(parts) or "no modifiers"

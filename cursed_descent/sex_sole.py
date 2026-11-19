import random
from typing import Any

from .config import SOLE_DIZZY, SOLE_GAG, SOLE_SWEAT_START, SOLE_SWEAT_TIERS
from .models import Player
from .sex_core import shift_content
from .sex_sole_texts import DISOBEYED, SMELL_UP, TASTE


KIND = "sole"
SWEAT_MAX = 100
SIDES = {
    "giver": ("rest", "press", "rub", "pinch", "toes", "lift", "order",
              "stop"),
    "receiver": ("breath", "worship", "suck", "struggle", "tap", "giveup"),
}
LABELS = {
    "rest": "Rest foot", "press": "Press down", "rub": "Rub on face",
    "pinch": "Pinch nose", "toes": "Toes in mouth", "lift": "Lift foot",
    "order": "Command: Lick", "worship": "Lick sole",
    "suck": "Suck toes",
}
FX = {
    "rest": {}, "press": {"drain": 5},
    "rub": {"drain": 5, "heat": (1, 0)},
    "pinch": {"drain": 15, "heat": (1, 0)},
    "toes": {"drain": 5, "heat": (1, 0)},
    "lift": {"air": 30, "safe": True}, "order": {},
    "worship": {"heat": (1, 0)}, "suck": {"heat": (1, 1)},
}
SWEAT_GAIN = {"rest": 2, "press": 3, "rub": 10, "pinch": 3, "toes": 5,
              "lift": -8}
GRANTS = {"more": ("rub", "press", "toes"), "mercy": ("lift",)}
OBEYING = ("worship", "suck")


def tier_of(value:int) -> int:
    return sum(value >= limit for limit in SOLE_SWEAT_TIERS)


def start_value(giver:Player) -> int:
    from .sweat import sweat_tier
    return min(SOLE_SWEAT_TIERS[0] - 1, sweat_tier(giver) * SOLE_SWEAT_START)


def after_beat(scene:dict[str, Any], giver:Player, receiver:Player,
               shown:str, taken:str | None, rng:random.Random,
               words:dict[str, str]) -> tuple[list[str], int]:
    lines: list[str] = []
    before = tier_of(scene["sweat"])
    scene["sweat"] = max(0, min(SWEAT_MAX, scene["sweat"]
                                + SWEAT_GAIN.get(shown, 0)))
    tier = tier_of(scene["sweat"])
    extra = 0
    if scene.pop("order", False):
        if taken in OBEYING:
            lines.append(rng.choice(TASTE[tier]).format(**words))
            extra += SOLE_GAG[tier]
        else:
            lines.append(rng.choice(DISOBEYED).format(**words))
            shift_content(giver, receiver, -1)
    if shown == "order":
        scene["order"] = True
    if tier > before:
        lines.append(SMELL_UP[tier].format(**words))
    if not FX.get(shown, {}).get("safe"):
        extra += SOLE_DIZZY[tier]
    return lines, extra

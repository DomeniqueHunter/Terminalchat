import random
from typing import Any

from ....config import VORE_CHANCE


OUTCOME_FATE = {"vore": "vored", "anal_vore": "anal_vored"}
VORE_FATES = tuple(OUTCOME_FATE.values())
BAD_END = ("💀 BAD END – {name} is gone for good: swallowed whole, no "
           "safeword, no way back.")


def outcome_from(record:dict[str, Any]) -> str:
    prefs = record.get("prefs") or {}
    for tag in prefs.get("outcomes", []):
        if tag in OUTCOME_FATE:
            return OUTCOME_FATE[tag]
    return ""


def vore_roll(fate:str, rng:random.Random, deadly:bool=False) -> str:
    if not fate:
        return ""
    return fate if deadly or rng.random() < VORE_CHANCE else ""

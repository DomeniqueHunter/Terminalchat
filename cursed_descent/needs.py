from typing import Any

from .config import (
    NEED_ITEM_EFFECTS, NEED_ITEM_PREFIXES, NEED_LEVELS, NEED_PENALTIES,
    NEED_RATES, NEEDS,
)
from .content import ITEMS


NEED_LABELS = {
    "hunger": ("fed", "peckish", "hungry", "starving"),
    "thirst": ("quenched", "thirsty", "parched", "dehydrated"),
    "sleep": ("rested", "tired", "exhausted", "dead on their feet"),
    "arousal": ("calm", "flushed", "aroused", "desperate"),
}
AROUSAL_ALLURE = (0, 1, 2, 3)


def new_needs() -> dict[str, int]:
    return {need: 0 for need in NEEDS}


def level_of(value:int) -> int:
    return sum(value >= limit for limit in NEED_LEVELS)


def label_of(need:str, value:int) -> str:
    return NEED_LABELS[need][level_of(value)]


def penalty(needs:dict[str, int], stat:str) -> int:
    return sum(amounts[level_of(needs.get(need, 0))]
               for need, (target, amounts) in NEED_PENALTIES.items()
               if target == stat)


def allure_bonus(needs:dict[str, int]) -> int:
    return AROUSAL_ALLURE[level_of(needs.get("arousal", 0))]


def advance(needs:dict[str, int],
            extra:dict[str, int] | None=None) -> list[tuple[str, int]]:
    risen: list[tuple[str, int]] = []
    for need in NEEDS:
        before = level_of(needs[need])
        needs[need] = min(100, needs[need] + NEED_RATES[need]
                          + (extra or {}).get(need, 0))
        after = level_of(needs[need])
        if after > before:
            risen.append((need, after))
    return risen


def starving(needs:dict[str, int]) -> list[str]:
    return [need for need in ("hunger", "thirst")
            if level_of(needs[need]) >= len(NEED_LEVELS)]


def item_needs(item_id:str) -> dict[str, int]:
    item = ITEMS.get(item_id, {})
    if "needs" in item:
        return dict(item["needs"])
    if item_id in NEED_ITEM_EFFECTS:
        return dict(NEED_ITEM_EFFECTS[item_id])
    for prefix, effects in NEED_ITEM_PREFIXES:
        if item_id.startswith(prefix):
            return dict(effects)
    return {}


def satisfy(needs:dict[str, int], effects:dict[str, int]) -> dict[str, int]:
    changes: dict[str, int] = {}
    for need, amount in effects.items():
        if need not in needs:
            continue
        new = max(0, min(100, needs[need] + amount))
        if new != needs[need]:
            changes[need] = new - needs[need]
        needs[need] = new
    return changes


def needs_line(needs:dict[str, Any]) -> str:
    parts = [f"{need} {needs[need]} ({label_of(need, needs[need])})"
             for need in NEEDS]
    return "Needs: " + " | ".join(parts)

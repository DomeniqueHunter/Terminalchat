from typing import Any

from .config import (
    SMOKERY_CURE_STAGES, SMOKERY_DEFAULT_CURE, SMOKERY_MAX_CURE,
)


def cure_level(entry:dict[str, Any]) -> int:
    return entry.get("cure", SMOKERY_DEFAULT_CURE)


def cure_stage(entry:dict[str, Any]) -> tuple[str, float, float]:
    level = cure_level(entry)
    for limit, label, heal, price in SMOKERY_CURE_STAGES:
        if level >= limit:
            return label, heal, price
    return SMOKERY_CURE_STAGES[-1][1:]


def ripen(entry:dict[str, Any]) -> bool:
    before = cure_stage(entry)[0]
    entry["cure"] = min(cure_level(entry) + 1, SMOKERY_MAX_CURE)
    return cure_stage(entry)[0] != before

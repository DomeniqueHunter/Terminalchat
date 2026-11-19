from typing import Any

from ..config import CYCLE_LENGTH, DEFAULT_GENDER, PRONOUNS, VENUE_LIST_MAX
from ..identity import character_key


def pronouns(gender:str) -> tuple[str, str, str]:
    return PRONOUNS.get(gender, PRONOUNS[DEFAULT_GENDER])


def cycle_stage(stage:int) -> int:
    return (stage - 1) % CYCLE_LENGTH + 1


def nearest(stages:list[int], stage:int) -> int:
    current = cycle_stage(stage)
    later = [value for value in sorted(stages) if value >= current]
    return later[0] if later else min(stages)


def unique_names(entries:list[dict[str, Any]]) -> list[dict[str, Any]]:
    first: dict[str, dict[str, Any]] = {}
    for entry in entries:
        first.setdefault(character_key(entry), entry)
    return list(first.values())


def listing(entries:list[dict[str, Any]], line:str, more:str,
            **extra:Any) -> list[str]:
    lines = [line.format(dead=entry["name"], stage=entry["stage"],
                         **{key: value(entry) for key, value in extra.items()})
             for entry in entries[-VENUE_LIST_MAX:]]
    if len(entries) > VENUE_LIST_MAX:
        lines.append(more.format(count=len(entries) - VENUE_LIST_MAX))
    return lines

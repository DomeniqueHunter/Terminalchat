import json
from typing import NamedTuple

from .base import Place
from .board import PLACES, WINDOWS, homes
from .discovery import TOWNS_DIR

FILE = "routines.json"
_CACHE: dict[str, dict[str, "Entry"]] = {}


class Entry(NamedTuple):
    examine: str = ""
    dialogues: tuple[str, ...] = ()


def place_key(npc:str, place:Place) -> str:
    home = homes().get(npc)
    if home is not None and place.town == home.town:
        return place.building
    return f"{place.town}:{place.building}"


def texts() -> dict[str, dict[str, Entry]]:
    if not _CACHE:
        for path in sorted(TOWNS_DIR.glob(f"*/*/{FILE}")):
            data = json.loads(path.read_text(encoding="utf-8"))
            for npc, places in data.items():
                if npc in _CACHE:
                    raise ValueError(f"{path}: {npc} is already described")
                _CACHE[npc] = {
                    key: Entry(str(value.get("examine", "")).strip(),
                               tuple(line for line in value.get(
                                   "dialogues", []) if str(line).strip()))
                    for key, value in places.items()}
    return _CACHE


def reset() -> None:
    _CACHE.clear()


def entry_for(npc:str, place:Place) -> Entry:
    return texts().get(npc, {}).get(place_key(npc, place), Entry())


def at_place(npc:str) -> Entry | None:
    place = PLACES.get(npc)
    if place is not None:
        return entry_for(npc, place)
    window = WINDOWS.get(npc)
    if window:
        return texts().get(npc, {}).get(f"@{window}", Entry())
    return None

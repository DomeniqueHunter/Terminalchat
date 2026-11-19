from importlib import import_module
from pathlib import Path

from .base import Routine

TOWNS_DIR = Path(__file__).resolve().parent.parent / "towns"
_FOUND: dict[str, Routine] = {}


def routines() -> dict[str, Routine]:
    if not _FOUND:
        for path in sorted(TOWNS_DIR.glob("*/*/routines.py")):
            town, building = path.parent.parent.name, path.parent.name
            module = import_module(
                f"cursed_descent.towns.{town}.{building}.routines")
            for routine in module.ROUTINES:
                if not isinstance(routine, Routine):
                    raise TypeError(f"{path}: {routine!r} is not a Routine")
                if routine.npc in _FOUND:
                    raise ValueError(
                        f"{path}: {routine.npc} already has a routine")
                _FOUND[routine.npc] = routine
    return _FOUND


def reset() -> None:
    _FOUND.clear()

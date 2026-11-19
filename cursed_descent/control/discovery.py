from importlib import import_module
from pathlib import Path

from .base import ControlKind

TOWNS_DIR = Path(__file__).resolve().parent.parent / "towns"
_FOUND: dict[str, ControlKind] = {}


def kinds() -> dict[str, ControlKind]:
    if not _FOUND:
        for path in sorted(TOWNS_DIR.glob("*/*/control.py")):
            town, building = path.parent.parent.name, path.parent.name
            module = import_module(
                f"cursed_descent.towns.{town}.{building}.control")
            for kind in module.KINDS:
                if not isinstance(kind, ControlKind):
                    raise TypeError(f"{path}: {kind!r} is not a ControlKind")
                if kind.key in _FOUND:
                    raise ValueError(f"{path}: {kind.key} already exists")
                _FOUND[kind.key] = kind
    return _FOUND


def reset() -> None:
    _FOUND.clear()

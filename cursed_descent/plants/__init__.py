import importlib
import pkgutil
from typing import Any

PLANTS: dict[str, dict[str, Any]] = {}
ITEMS: dict[str, dict[str, Any]] = {}
BUFFS: dict[str, dict[str, Any]] = {}
DROPS: list[dict[str, Any]] = []


def load() -> None:
    for info in sorted(pkgutil.iter_modules(__path__), key=lambda i: i.name):
        if not info.ispkg:
            continue
        base = f"{__name__}.{info.name}"
        plant = importlib.import_module(f"{base}.plant").PLANT
        PLANTS[info.name] = plant
        ITEMS.update(importlib.import_module(f"{base}.items").ITEMS)
        BUFFS.update(importlib.import_module(f"{base}.buffs").BUFFS)
        drop = importlib.import_module(f"{base}.drops").DROP
        if drop:
            DROPS.append(drop)


load()

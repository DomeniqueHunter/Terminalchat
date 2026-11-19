from importlib import import_module
from pathlib import Path

from .base import Building


TOWNS_DIR = Path(__file__).resolve().parent.parent / "towns"
TOWNS_PACKAGE = f"{__package__.rsplit('.', 1)[0]}.towns"
_MOUNTED: dict[str, tuple[Building, ...]] = {}


def town_folders() -> list[str]:
    return sorted(path.name for path in TOWNS_DIR.iterdir()
                  if path.is_dir() and (path / "town.py").exists())


def building_folders(town_folder:str) -> list[str]:
    return sorted(path.name for path in (TOWNS_DIR / town_folder).iterdir()
                  if path.is_dir() and (path / "__init__.py").exists()
                  and not path.name.startswith("_"))


def load_building(town_folder:str, name:str) -> Building:
    module = import_module(f"{TOWNS_PACKAGE}.{town_folder}.{name}")
    building = getattr(module, "BUILDING", None)
    if not isinstance(building, Building):
        raise TypeError(f"towns/{town_folder}/{name}/__init__.py must define "
                        f"BUILDING = <Building subclass>()")
    if not building.key:
        type(building).key = name
    if building.key != name:
        raise ValueError(f"towns/{town_folder}/{name}: folder name and "
                         f"building key {building.key!r} must match")
    building.town = town_folder
    return building


def mounted(town_folder:str) -> tuple[Building, ...]:
    if town_folder not in _MOUNTED:
        found = [load_building(town_folder, name)
                 for name in building_folders(town_folder)]
        _MOUNTED[town_folder] = tuple(
            sorted(found, key=lambda item: (item.order, item.key)))
    return _MOUNTED[town_folder]


def building_module(town_folder:str, name:str, part:str):
    if not (TOWNS_DIR / town_folder / name / f"{part}.py").exists():
        return None
    return import_module(f"{TOWNS_PACKAGE}.{town_folder}.{name}.{part}")


def npc_keys(town_folder:str, name:str) -> list[str]:
    module = building_module(town_folder, name, "npcs")
    return list(getattr(module, "NPCS", {})) if module else []


def topics(town_folder:str, name:str) -> dict:
    module = building_module(town_folder, name, "dialogue")
    return getattr(module, "TOPICS", {}) if module else {}

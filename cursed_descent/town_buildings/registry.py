from collections.abc import Callable

from . import discovery
from .base import Building

_SPECS: dict[str, Building] = {}


def specs() -> dict[str, Building]:
    if not _SPECS:
        for folder in discovery.town_folders():
            for building in discovery.mounted(folder):
                _SPECS.setdefault(building.key, building)
    return _SPECS


def get(key:str, town:str="") -> Building | None:
    if town:
        from ..towns import TOWNS
        folder = TOWNS[town].folder if town in TOWNS else town
        for building in discovery.mounted(folder):
            if building.key == key:
                return building
    return specs().get(key)


def panel_for(key:str, services, player):
    spec = get(key)
    if spec is None:
        return None
    if spec.ui is not None:
        return spec.ui(services, player)
    if spec.counter is not None:
        from .counter import counter_ui
        return counter_ui(key)(services, player)
    return None


def info_lines(key:str, services, player) -> tuple[str, ...]:
    spec = get(key)
    if spec is None or spec.info is None:
        return ()
    return tuple(spec.info(services, player))


def commands() -> dict[str, Callable]:
    return {name: handler for spec in specs().values()
            for name, handler in spec.commands.items()}


def register_items(items:dict) -> None:
    for spec in specs().values():
        if spec.items is not None:
            items.update(spec.items())


def run_setup(services) -> None:
    for spec in specs().values():
        if spec.setup is not None:
            spec.setup(services)


def run_save(services) -> None:
    for spec in specs().values():
        if spec.save is not None:
            spec.save(services)


def run_idle(player) -> None:
    for spec in specs().values():
        if spec.idle_hook is not None:
            spec.idle_hook(player)


def session_lines() -> dict[str, list[str]]:
    return {job: lines for spec in specs().values()
            for job, lines in spec.session_lines.items()}


def place_of() -> dict[str, str]:
    return {command: spec.key for spec in specs().values()
            for command in spec.place_commands}


class Layered(dict):
    def __init__(self, legacy:dict, field_name:str) -> None:
        super().__init__(legacy)
        self.field_name = field_name

    def __missing__(self, key:str):
        spec = get(key)
        if spec is None:
            raise KeyError(key)
        return getattr(spec, self.field_name)

    def get(self, key:str, default=None):
        try:
            return self[key]
        except KeyError:
            return default

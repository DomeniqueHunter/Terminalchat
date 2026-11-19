import importlib
import pkgutil
from dataclasses import dataclass, replace

from ..settings import prototype
from ..town_buildings import Building, discovery


@dataclass(frozen=True)
class Resident:
    key: str
    first_name: str
    last_name: str
    role: str
    building: str
    gender: str
    age: int
    personality: str
    look: str
    quotes: tuple[str, ...]
    body: tuple[tuple[str, object], ...] = ()
    topics: tuple[tuple[str, tuple[str, ...]], ...] = ()
    race: str = ""


def resident(key:str) -> Resident:
    record = prototype(key)
    profile = record["profile"]
    return Resident(
        key, record["first_name"], record["last_name"], profile["role"],
        profile["building"], record["gender"], record["age"],
        record["personality"], profile["look"], tuple(profile["quotes"]),
        topics=tuple((topic, tuple(lines))
                     for topic, lines in profile["topics"].items()),
        body=tuple(record["body"].items()), race=record["race"])


_RESIDENTS: dict[str, tuple[Resident, ...]] = {}


@dataclass(frozen=True)
class Town:
    key: str
    name: str
    race: str
    race_key: str
    blurb: str
    folder: str = ""
    happenings: tuple[str, ...] = ()
    rumors: tuple[str, ...] = ()
    hub: bool = False
    lines: tuple[str, ...] = ()
    decency: int = 2
    wip: bool = False
    gaze: tuple[str, ...] = ()

    def building_list(self) -> list[Building]:
        return list(discovery.mounted(self.folder))

    @property
    def residents(self) -> tuple[Resident, ...]:
        if self.folder not in _RESIDENTS:
            found = []
            for building in self.building_list():
                spoken = discovery.topics(self.folder, building.key)
                for key in discovery.npc_keys(self.folder, building.key):
                    person = resident(key)
                    if key in spoken:
                        person = replace(person, topics=tuple(
                            (topic, tuple(lines))
                            for topic, lines in spoken[key].items()))
                    found.append(person)
            _RESIDENTS[self.folder] = tuple(found)
        return _RESIDENTS[self.folder]

    @property
    def buildings(self) -> tuple[str, ...]:
        return tuple(building.key for building in self.building_list())


def load_towns() -> dict[str, Town]:
    towns: dict[str, Town] = {}
    for info in pkgutil.iter_modules(__path__):
        if not info.ispkg:
            continue
        module = importlib.import_module(f"{__name__}.{info.name}.town")
        town = replace(module.TOWN, folder=info.name)
        towns[town.key] = town
    return dict(sorted(towns.items()))


TOWNS = load_towns()
START_TOWN = "last_light"


def town_text(town:Town, happening:str="") -> str:
    lines = [f"🏘️ {town.name} ({town.race})", town.blurb]
    if happening:
        lines.append(f"✦ {happening}")
    for building in town.building_list():
        lines.append(f"  [{building.command}] {building.button} – "
                     f"{building.blurb}")
    if town.residents:
        lines.append("Locals ([meet <name>]): " + ", ".join(
            resident.first_name for resident in town.residents))
    lines.append("[rumors] – listen to the talk of the town")
    return "\n".join(lines)


def town_key(player) -> str:
    key = player.profile.get("town", START_TOWN)
    return key if key in TOWNS else START_TOWN


def town_of(player) -> Town:
    return TOWNS[town_key(player)]


def fare_between(origin:str, goal:str) -> int:
    from ..config import TRAVEL_FARE_HUB, TRAVEL_FARE_FAR
    if origin == goal:
        return 0
    if TOWNS[origin].hub or TOWNS[goal].hub:
        return TRAVEL_FARE_HUB
    return TRAVEL_FARE_FAR


def visited(player) -> list[str]:
    seen = [key for key in player.profile.get("towns_seen", [])
            if key in TOWNS]
    for key in (START_TOWN, town_key(player)):
        if key not in seen:
            seen.append(key)
    return seen


def mark_visited(player, key:str) -> None:
    seen = list(player.profile.get("towns_seen", []))
    if key not in seen:
        seen.append(key)
    player.profile["towns_seen"] = seen


def destinations(player) -> list[str]:
    from ..town_buildings.station.rail_pass import passes
    here = town_key(player)
    owned = set(passes(player))
    return [key for key in TOWNS if key in owned and key != here]

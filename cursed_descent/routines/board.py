import random

from .base import Place
from .discovery import routines

PLACES: dict[str, Place] = {}
WINDOWS: dict[str, str] = {}
HIDDEN: set[str] = set()


def homes() -> dict[str, Place]:
    from ..towns import TOWNS
    return {person.key: Place(town.key, person.building)
            for town in TOWNS.values() for person in town.residents}


def town_buildings() -> dict[str, tuple[str, ...]]:
    from ..towns import TOWNS
    return {town.key: tuple(key for key in town.buildings if key != "town")
            for town in TOWNS.values()}


def location_of(key:str) -> Place | None:
    return PLACES.get(key)


def away_from(town:str, building:str) -> set[str]:
    home = homes()
    return {key for key, place in PLACES.items()
            if home.get(key) == Place(town, building)}


def present(town:str, building:str) -> list[str]:
    home = homes()
    here = Place(town, building)
    return [key for key, base in home.items()
            if key not in HIDDEN and PLACES.get(key, base) == here]


def people(town:str, building:str) -> list:
    from ..towns import TOWNS
    keys = set(present(town, building))
    return [person for each in TOWNS.values() for person in each.residents
            if person.key in keys]


def reachable(player, key:str) -> bool:
    if key in HIDDEN:
        return False
    if key not in routines():
        return True
    base = homes().get(key)
    if base is None:
        return True
    from ..towns import town_key
    here = Place(town_key(player), player.profile.get("where") or "town")
    return PLACES.get(key, base) == here


def away_note(place:Place, here:str="") -> str:
    from ..town_buildings import registry
    from ..towns import TOWNS
    spec = registry.get(place.building, place.town)
    name = spec.title if spec is not None else "town square"
    town = TOWNS.get(place.town)
    where = f"the {name}"
    if town is not None and place.building != "town" and (
            place.town != here):
        return f"away: at {where} ({town.name})"
    return f"away: at {where}"


def absent(town:str, building:str) -> list[tuple]:
    from ..towns import TOWNS
    here = Place(town, building)
    home = homes()
    return [(person, away_note(PLACES[person.key], town))
            for person in TOWNS[town].residents
            if home.get(person.key) == here and person.key in PLACES]


def away_message(player, text:str) -> str:
    from ..towns import TOWNS, town_key
    wanted = text.strip().casefold()
    if not wanted:
        return ""
    for town in TOWNS.values():
        for person in town.residents:
            place = PLACES.get(person.key)
            names = (person.first_name.casefold(),
                     person.last_name.casefold(),
                     f"{person.first_name} {person.last_name}".casefold())
            if place is None or reachable(player, person.key) or not (
                    wanted in names or wanted in names[0].split()):
                continue
            return (f"{person.first_name} {person.last_name} is not here "
                    f"– {away_note(place, town_key(player))}.")
    return ""


def validate() -> None:
    home = homes()
    for key, routine in routines().items():
        base = home.get(key)
        if base is None:
            continue
        targets = [(item.town, item.building)
                   for item in (getattr(routine, "stops", ())
                                + getattr(routine, "spots", ()))]
        for town, building in targets:
            if building == base.building and town in ("", base.town):
                raise ValueError(
                    f"{key}: a routine may not name the NPC's own building "
                    f"'{building}'; it is the default place")


def where_lines() -> list[str]:
    from ..towns import TOWNS
    home = homes()
    names = {person.key: person for town in TOWNS.values()
             for person in town.residents}
    lines = ["Routine NPCs:"]
    for key in routines():
        person = names.get(key)
        if person is None:
            continue
        place = PLACES.get(key)
        where = (away_note(place, home[key].town).replace("away: at ", "")
                 if place is not None else "at home")
        lines.append(f"  {person.first_name} {person.last_name} – {where}")
    return lines if len(lines) > 1 else ["No routine NPCs."]


class RoutineBoard:
    def __init__(self, rng:random.Random | None=None) -> None:
        self.rng = rng or random.Random()
        self.state: dict[str, dict] = {}
        PLACES.clear()
        WINDOWS.clear()
        HIDDEN.clear()
        validate()

    def tick(self, now:float) -> None:
        home = homes()
        towns = town_buildings()
        for key, routine in routines().items():
            if key not in home:
                continue
            place = routine.place(now, home[key], self.rng,
                                  self.state.setdefault(key, {}), towns)
            if place == home[key]:
                PLACES.pop(key, None)
                window = routine.window(now)
                if window:
                    WINDOWS[key] = window
                else:
                    WINDOWS.pop(key, None)
            else:
                PLACES[key] = place
                WINDOWS.pop(key, None)

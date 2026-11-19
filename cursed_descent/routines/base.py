import random
from dataclasses import dataclass
from typing import NamedTuple

HOME = "@home"
ANY = "*"
DAY_HOURS = 24


class Place(NamedTuple):
    town: str
    building: str


@dataclass(frozen=True)
class Stop:
    building: str
    start: float
    end: float
    town: str = ""

    def covers(self, hour:float) -> bool:
        if self.start <= self.end:
            return self.start <= hour < self.end
        return hour >= self.start or hour < self.end


@dataclass(frozen=True)
class Window:
    name: str
    start: float
    end: float

    def covers(self, hour:float) -> bool:
        return Stop("", self.start, self.end).covers(hour)


@dataclass(frozen=True)
class Spot:
    building: str
    town: str = ""
    weight: int = 1


class Routine:
    npc: str
    uses: tuple[str, ...]
    windows: tuple["Window", ...] = ()

    def window(self, now:float) -> str:
        hour = now % DAY_HOURS
        for window in self.windows:
            if window.covers(hour):
                return window.name
        return ""

    def place(self, now:float, home:Place, rng:random.Random,
              state:dict, towns:dict[str, tuple[str, ...]]) -> Place:
        raise NotImplementedError


def resolve(town:str, building:str, home:Place) -> Place:
    place = Place(town or home.town, building)
    return home if building == HOME else place


@dataclass(frozen=True)
class Schedule(Routine):
    npc: str
    stops: tuple[Stop, ...]
    uses: tuple[str, ...] = ()
    windows: tuple[Window, ...] = ()

    def place(self, now:float, home:Place, rng:random.Random,
              state:dict, towns:dict[str, tuple[str, ...]]) -> Place:
        hour = now % DAY_HOURS
        for stop in self.stops:
            if stop.covers(hour):
                return resolve(stop.town, stop.building, home)
        return home


@dataclass(frozen=True)
class Wander(Routine):
    npc: str
    spots: tuple[Spot, ...] = ()
    towns: tuple[str, ...] = ()
    stay: tuple[float, float] = (1.0, 3.0)
    uses: tuple[str, ...] = ()

    def candidates(self, home:Place, towns:dict[str, tuple[str, ...]]
                   ) -> list[tuple[Place, int]]:
        if self.spots:
            found = [(resolve(spot.town, spot.building, home), spot.weight)
                     for spot in self.spots]
        else:
            allowed = (tuple(towns) if ANY in self.towns
                       else self.towns or (home.town,))
            found = [(Place(town, building), 1) for town in allowed
                     for building in towns.get(town, ())]
        return found or [(home, 1)]

    def place(self, now:float, home:Place, rng:random.Random,
              state:dict, towns:dict[str, tuple[str, ...]]) -> Place:
        if state.get("until", -1.0) > now and "place" in state:
            return state["place"]
        choices = self.candidates(home, towns)
        picked = rng.choices([place for place, _ in choices],
                             [weight for _, weight in choices])[0]
        state["place"] = picked
        state["until"] = now + rng.uniform(*self.stay)
        return picked

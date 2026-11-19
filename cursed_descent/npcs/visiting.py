import random
from dataclasses import dataclass
from importlib import import_module
from typing import Any

from ..config import VISIT_ROLL_SECONDS, VISIT_START_CHANCE, VISIT_STAY
from ..models import Player
from .visit_profile import VisitProfile


FEMININE = ("Female", "Herm", "Shemale")
SOURCES = ("locations.brewery.npc", "locations.fisher.npc",
           "locations.smokery.npc", "locations.sweatery.npc",
           "npcs.figures")
CACHE: dict[str, VisitProfile] = {}


def profiles() -> dict[str, VisitProfile]:
    if not CACHE:
        for source in SOURCES:
            module = import_module(f"..{source}", __package__)
            for profile in module.VISITS:
                CACHE[profile.npc] = profile
    return CACHE


def quirk_line(key:str, situation:str, rng:random.Random) -> str:
    profile = profiles().get(key)
    if profile is None:
        return ""
    lines = dict(profile.quirks).get(situation, ())
    return rng.choice(lines) if lines else ""


def roles_of(profile:VisitProfile, gender:str) -> list[tuple[str, int]]:
    return [(building, weight) for building, weight in profile.likes
            if building != "cafe" or gender in FEMININE]


def npc_record(npc:Player,
               profile:VisitProfile | None=None) -> dict[str, Any]:
    cruel = profile.cruel if profile else 1
    stance = profile.stance if profile else ""
    body = npc.body
    return {"name": npc.full_name, "npc": npc.npc, "id": npc.id, "age": npc.age,
            "race": npc.race,
            "address": npc.profile.get("address", ""),
            "home": npc.profile.get("home", ""),
            "height": body.get("height", 170),
            "weight": body.get("weight", 70), "butt": body.get("butt", 95),
            "gender": npc.gender, "bust": body.get("bust", 0),
            "endowment": body.get("endowment", 0), "cruel": cruel,
            "dominated": stance == "dominated",
            "dominant": stance == "dominant",
            "temper": "gruff" if stance == "dominant" else "",
            **({"prefs": npc.profile["prefs"]}
               if "prefs" in npc.profile else {})}


@dataclass
class Visit:
    npc: str
    town: str
    building: str
    until: float


class VisitBoard:
    def __init__(self, rng:random.Random) -> None:
        self.rng = rng
        self.visits: dict[str, Visit] = {}
        self.due: dict[str, float] = {}

    def away_kinds(self) -> set[str]:
        return {kind for key in self.visits
                for kind in profiles()[key].kinds}

    def here(self, town:str, building:str) -> list[str]:
        return [visit.npc for visit in self.visits.values()
                if visit.town == town and visit.building == building]

    def where(self, key:str) -> Visit | None:
        return self.visits.get(key)

    def tick(self, now:float, towns:tuple[str, ...], busy:set[str],
             genders:dict[str, str]) -> None:
        for key, visit in list(self.visits.items()):
            if now >= visit.until:
                del self.visits[key]
        for key, profile in profiles().items():
            if key in self.visits or key not in genders:
                continue
            due = self.due.setdefault(
                key, now + self.rng.uniform(0, VISIT_ROLL_SECONDS))
            if now < due:
                continue
            self.due[key] = now + self.rng.uniform(
                VISIT_ROLL_SECONDS, 2 * VISIT_ROLL_SECONDS)
            if busy & set(profile.kinds) or (
                    self.rng.random() >= VISIT_START_CHANCE):
                continue
            roles = roles_of(profile, genders[key])
            if not roles:
                continue
            building = self.rng.choices(
                [name for name, _ in roles], [w for _, w in roles])[0]
            self.visits[key] = Visit(
                key, self.rng.choice(towns), building,
                now + self.rng.uniform(*VISIT_STAY))

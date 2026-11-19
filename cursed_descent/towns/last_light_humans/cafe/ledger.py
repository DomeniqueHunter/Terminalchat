import random
import uuid
from pathlib import Path
from typing import Any

from ....clock import timestamp
from ....config import (
    CAFE_BERTHA_MAX, CAFE_ENGULF_WAIT, CAFE_FATE_WEIGHTS, CAFE_GROWTH,
    CAFE_STOCK, STAT_NAMES,
)
from ....content import ITEMS
from ....models import Player
from ....storage import read_json, write_json
from .content import OUTCOMES, READY_LINE


FILE_NAME = "cafe.json"


def snapshot(player:Player) -> dict[str, Any]:
    return {"name": player.name, "level": player.level,
            "gender": player.gender, "stats": dict(player.stats)}


def top_stat(victim:dict[str, Any]) -> str:
    return max(STAT_NAMES, key=lambda stat: victim["stats"][stat])


def build_cushion(victim:dict[str, Any]) -> dict[str, Any]:
    level = victim["level"]
    return {
        "name": f"{victim['name']} Seat Cushion", "slot": "accessory",
        "rarity": "epic",
        "bonus": {top_stat(victim): 2 + level // 8},
        "armor": 1 + level // 6, "allure": 3, "no_loot": True,
        "cafe": True, "made_from": victim["name"],
        "price": 150 + level * 25,
        "note": "stuffed and stitched at the Fat Ass Café – still warm "
                "where ladies have sat",
    }


def build_cake(victim:dict[str, Any]) -> dict[str, Any]:
    level = victim["level"]
    return {
        "name": f"{victim['name']}'s Cream Cake", "slot": "consumable",
        "rarity": "rare", "heal": 60 + level * 8, "mana": 20 + level * 3,
        "needs": {"hunger": -35, "thirst": -10}, "no_loot": True,
        "cafe": True, "made_from": victim["name"],
        "price": 40 + level * 6,
        "note": "a very rich slice from the Fat Ass Café kitchen",
    }


BUILDERS = {"cushion": build_cushion, "cake": build_cake}


def pick_outcome(victim:dict[str, Any], rng:random.Random) -> str:
    kinds = list(CAFE_FATE_WEIGHTS)
    return rng.choices(kinds, [CAFE_FATE_WEIGHTS[kind]
                               for kind in kinds])[0]


class CafeLedger:
    def __init__(self, data_path:Path) -> None:
        self.path = data_path / FILE_NAME
        self.entries: list[dict[str, Any]] = read_json(self.path, [])
        for entry in self.entries:
            if entry["outcome"] in BUILDERS and entry["state"] == "ready":
                ITEMS[entry["id"]] = BUILDERS[entry["outcome"]](
                    entry["victim_data"])

    def save(self) -> None:
        write_json(self.path, self.entries)

    def add(self, player:Player, fate:str, outcome:str) -> dict[str, Any]:
        entry = {"id": f"cafe_{uuid.uuid4().hex[:10]}",
                 "victim": player.name, "victim_data": snapshot(player),
                 "fate": fate, "outcome": outcome, "sold": False,
                 "state": "ready", "wait": 0, "date": timestamp()}
        if fate == "engulfed" and outcome in BUILDERS:
            entry["state"] = "digesting"
            entry["wait"] = CAFE_ENGULF_WAIT
        elif outcome in BUILDERS:
            ITEMS[entry["id"]] = BUILDERS[outcome](entry["victim_data"])
        self.entries.append(entry)
        self.save()
        return entry

    def tick(self) -> list[str]:
        lines = []
        for entry in self.entries:
            if entry["state"] != "digesting":
                continue
            entry["wait"] -= 1
            if entry["wait"] > 0:
                continue
            entry["state"] = "ready"
            ITEMS[entry["id"]] = BUILDERS[entry["outcome"]](
                entry["victim_data"])
            lines.append(READY_LINE.format(
                name=entry["victim"], item=ITEMS[entry["id"]]["name"]))
        if lines:
            self.save()
        return lines

    def stock(self) -> list[dict[str, Any]]:
        ready = [entry for entry in self.entries
                 if entry["state"] == "ready" and not entry["sold"]
                 and entry["outcome"] in BUILDERS]
        return ready[-CAFE_STOCK:]

    def sell(self, entry:dict[str, Any]) -> None:
        entry["sold"] = True
        self.save()

    def digesting(self) -> int:
        return sum(1 for entry in self.entries
                   if entry["state"] == "digesting")


def outcome_text(entry:dict[str, Any], victim:Player) -> str:
    key = entry["outcome"]
    item = ITEMS[entry["id"]]["name"] if entry["id"] in ITEMS else ""
    if entry["fate"] == "engulfed" and key in BUILDERS:
        return OUTCOMES["engulfed"]
    return OUTCOMES[key].format(item=item, name=victim.name)


def grow_keeper(keeper:Player | None, fate:str) -> None:
    if keeper is None or fate not in CAFE_GROWTH:
        return
    kilos, cm = CAFE_GROWTH[fate]
    keeper.body["weight"] = min(CAFE_BERTHA_MAX[0],
                                keeper.body["weight"] + kilos)
    keeper.body["butt"] = min(CAFE_BERTHA_MAX[1], keeper.body["butt"] + cm)

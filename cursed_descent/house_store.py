import json
import random
import string
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .items import item_from_json, item_to_json
from .storage import read_json, write_json


ID_LENGTH = 6
ID_CHARS = string.ascii_lowercase + string.digits
MEMORY_ONLY = ("guests", "scenes")
CURRENT: list["HouseStore"] = []


@dataclass
class ChestAccount:
    gold: int = 0
    items: list[str] = field(default_factory=list)
    capacity: int = 0


def current() -> "HouseStore":
    return CURRENT[-1]


class HouseStore:
    def __init__(self, data_path:Path, repository:Any) -> None:
        self.data_path = data_path
        self.repository = repository
        self.houses: dict[str, dict[str, Any]] = {}
        self.accounts: dict[str, ChestAccount] = {}
        self.written: dict[str, str] = {}
        self.day = lambda: 0
        CURRENT.append(self)

    def folder(self, town:str) -> Path:
        return self.data_path / town / "houses"

    def path(self, town:str, house_id:str) -> Path:
        return self.folder(town) / f"{house_id}.json"

    def used_ids(self) -> set[str]:
        found = set(self.houses)
        for path in self.data_path.glob("*/houses/*.json"):
            found.add(path.stem)
        return found

    def new_id(self) -> str:
        used = self.used_ids()
        while True:
            house_id = "".join(random.choices(ID_CHARS, k=ID_LENGTH))
            if house_id not in used:
                return house_id

    def create(self, town:str, owner:Any, kind:str, value:int,
               legacy:dict[str, Any] | None=None) -> dict[str, Any]:
        from .town_buildings.visits import STREETS
        house_id = self.new_id()
        legacy = legacy or {}
        house = {key: item for key, item in legacy.items()
                 if key not in ("type", "residents", "guests")}
        house.update({
            "id": house_id, "town": town, "owner": owner.id,
            "owner_name": owner.name, "type": kind, "value": value,
            "address": f"No. {random.randint(2, 60)} "
                       f"{random.choice(STREETS)}",
            "address_id": house_id, "description": "",
            "residents": list(legacy.get("residents", [])), "guests": []})
        self.houses[house_id] = house
        self.accounts[house_id] = ChestAccount()
        self.flush()
        return house

    def get(self, house_id:str, town:str) -> dict[str, Any] | None:
        if house_id in self.houses:
            return self.houses[house_id]
        data = read_json(self.path(town, house_id), None)
        if data is None:
            return None
        storage = data.pop("storage", {})
        data["guests"] = []
        self.houses[house_id] = data
        self.accounts[house_id] = ChestAccount(
            storage.get("gold", 0),
            [item_from_json(item) for item in storage.get("items", [])])
        self.written[house_id] = self.dump(data, self.accounts[house_id])
        return data

    def account(self, house:dict[str, Any]) -> ChestAccount:
        from .furnishing.rules import capacity_of
        account = self.accounts.setdefault(house["id"], ChestAccount())
        account.capacity = capacity_of(house)
        return account

    def migrate(self, player:Any, town:str) -> dict[str, Any]:
        from .config import HOUSE_TYPES
        legacy = player.profile["houses"][town]
        house = self.create(town, player, legacy["type"],
                            HOUSE_TYPES[legacy["type"]][1], legacy)
        player.profile["houses"][town] = house["id"]
        for entry in house["residents"]:
            resident = self.repository.load_by_id(entry["id"])
            if resident is not None:
                resident.profile.setdefault("lodging", {})[town] = house["id"]
                self.repository.save(resident)
        self.repository.save(player)
        return house

    def dump(self, house:dict[str, Any], account:ChestAccount) -> str:
        data = {key: value for key, value in house.items()
                if key not in MEMORY_ONLY}
        data["storage"] = {"gold": account.gold,
                           "items": [item_to_json(item)
                                     for item in account.items]}
        return json.dumps(data, indent=2, ensure_ascii=False)

    def flush(self) -> None:
        for house_id, house in self.houses.items():
            text = self.dump(house, self.account(house))
            if self.written.get(house_id) == text:
                continue
            write_json(self.path(house["town"], house_id),
                       json.loads(text))
            self.written[house_id] = text

    def guest_elsewhere(self, char_id:str,
                        house:dict[str, Any]) -> dict[str, Any] | None:
        for other in self.houses.values():
            if other["id"] != house["id"] and any(
                    entry["id"] == char_id for entry in other["guests"]):
                return other
        return None

    def sweep(self, now:float, idle:float) -> list[tuple[str, str, str]]:
        gone: list[tuple[str, str, str]] = []
        for house in self.houses.values():
            keep = []
            for entry in house["guests"]:
                if entry.get("npc") and now - entry.get("seen", now) > idle:
                    gone.append((house["owner_name"], entry["name"],
                                 entry["id"]))
                else:
                    keep.append(entry)
            house["guests"] = keep
        return gone

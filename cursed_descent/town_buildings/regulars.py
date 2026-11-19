import random
import re
from pathlib import Path
from typing import Any

from ..config import (
    HAPPY_DEFAULT, HAPPY_MAX, NPC_DIR_NAME, REGULARS_CAP, REGULARS_DIR_NAME, REGULARS_CHANCE,
)
from ..storage import read_json, write_json
from .regular_body import complete, drift


BUILDINGS = ("brothel", "cafe")
REF_TYPE = "story_npc"
SHADOWED = ("name", "npc", "age", "height", "weight", "butt", "gender",
            "bust", "endowment", "cruel", "home", "address", "prefs")


def slug(name:str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.casefold()).strip("_") or "x"


class Regulars:
    def __init__(self, data_path:Path, town:str, owner:str) -> None:
        base = data_path / NPC_DIR_NAME / REGULARS_DIR_NAME
        self.root = base / owner / town
        self.shared = base / town
        self.provider = None
        self.resolver = None
        self.credit = None
        self.owners: dict[str, str] = {}
        for building in BUILDINGS:
            self.folder(building).mkdir(parents=True, exist_ok=True)

    def visiting(self, building:str) -> list[dict[str, Any]]:
        return self.provider(building) if self.provider else []

    def folder(self, building:str) -> Path:
        return self.root / building

    def is_ref(self, stored:dict[str, Any]) -> bool:
        return stored.get("type") == REF_TYPE

    def resolve(self, stored:dict[str, Any]) -> dict[str, Any]:
        if not self.is_ref(stored):
            return stored
        real = self.resolver(stored["ref_id"]) if self.resolver else None
        if not real:
            return {}
        merged = dict(stored, **{key: real[key] for key in SHADOWED
                                 if key in real})
        if stored.get("alias"):
            merged["name"] = stored["alias"]
        return merged

    def write(self, path:Path, stored:dict[str, Any]) -> None:
        if self.is_ref(stored):
            stored = {key: value for key, value in stored.items()
                      if key not in SHADOWED}
        write_json(path, stored)

    def visit(self, building:str, record:dict[str, Any],
              alias:str="") -> dict[str, Any]:
        path = self.folder(building) / f"{slug(record['name'])}.json"
        stored = read_json(path, {}) if path.exists() else {
            "type": REF_TYPE, "ref_id": record.get("id") or record["npc"],
            "visits": 0}
        if alias:
            stored["alias"] = alias
        stored["visits"] = stored.get("visits", 0) + 1
        self.write(path, stored)
        return self.resolve(stored)

    def owner_visit(self, building:str,
                    name:str="") -> dict[str, Any] | None:
        key = self.owners.get(building)
        real = self.resolver(key) if self.resolver and key else None
        if not real:
            return None
        stored = self.visit(building, dict(real, name=name or real["name"]),
                            alias=name if name != real["name"] else "")
        return dict(real, **{k: v for k, v in stored.items()
                             if k not in SHADOWED})

    def all(self, building:str) -> list[dict[str, Any]]:
        records = (self.upgrade(building, path)
                   for path in sorted(self.folder(building).glob("*.json")))
        return [record for record in records
                if isinstance(record, dict) and record.get("name")]

    def shared_records(self, building:str) -> list[dict[str, Any]]:
        folder = self.shared / building
        records = (self.resolve(read_json(path, {}))
                   for path in sorted(folder.glob("*.json")))
        return [record for record in records
                if isinstance(record, dict) and record.get("name")]

    def pool(self, building:str) -> list[dict[str, Any]]:
        own = [record for record in self.all(building)
               if not self.is_ref(record)]
        names = {record["name"].casefold() for record in own}
        return own + [record for record in self.shared_records(building)
                      if record["name"].casefold() not in names
                      and not self.is_ref(record)]

    def pick(self, building:str,
             rng:random.Random) -> dict[str, Any] | None:
        known = self.pool(building)
        if known and rng.random() < REGULARS_CHANCE:
            return rng.choice(known)
        return None

    def count(self, building:str, name:str, key:str) -> dict[str, int]:
        path = self.folder(building) / f"{slug(name)}.json"
        if not path.exists():
            return {}
        stored = read_json(path, {})
        history = stored.setdefault("history", {})
        history[key] = history.get(key, 0) + 1
        self.write(path, stored)
        return history

    def get(self, building:str, name:str) -> dict[str, Any] | None:
        path = self.folder(building) / f"{slug(name)}.json"
        if not path.exists():
            return None
        return self.upgrade(building, path)

    def upgrade(self, building:str, path:Path) -> dict[str, Any]:
        stored = read_json(path, {})
        if self.is_ref(stored):
            return self.resolve(stored)
        full = complete(building, stored) if stored.get("name") else stored
        if full.get("name") and not full.get("home"):
            from .visits import new_home
            full = {**new_home(random.Random(slug(full["name"])),
                               full.get("age", 30)), **full}
            full["home"] = full.get("home") or new_home(
                random.Random(slug(full["name"])), 30)["home"]
        if full != stored:
            self.write(path, full)
        return full

    def set(self, building:str, name:str, values:dict[str, Any]) -> None:
        path = self.folder(building) / f"{slug(name)}.json"
        if not path.exists():
            return
        stored = read_json(path, {})
        stored.update(values)
        self.write(path, stored)

    def find(self, text:str) -> tuple[str, dict[str, Any]] | None:
        wanted = text.strip().casefold()
        if not wanted:
            return None
        for building in BUILDINGS:
            for record in self.all(building):
                name = record["name"].casefold()
                if wanted == name or wanted in name.replace(".", "").split():
                    return building, record
        return None

    def has(self, building:str, name:str) -> bool:
        return (self.folder(building) / f"{slug(name)}.json").exists()

    def forget(self, building:str, name:str) -> bool:
        path = self.folder(building) / f"{slug(name)}.json"
        if not path.exists():
            return False
        path.unlink()
        return True

    def add(self, building:str, record:dict[str, Any]) -> bool:
        if self.has(building, record["name"]):
            return False
        write_json(self.folder(building) / f"{slug(record['name'])}.json",
                   complete(building, dict(record, visits=1)))
        return True

    def fill(self, building:str, name:str, values:dict[str, Any]) -> None:
        path = self.folder(building) / f"{slug(name)}.json"
        if not path.exists():
            return
        stored = read_json(path, {})
        missing = {key: value for key, value in values.items()
                   if key not in stored}
        if missing:
            stored.update(missing)
            self.write(path, stored)

    def mood(self, building:str, name:str, delta:int) -> int:
        path = self.folder(building) / f"{slug(name)}.json"
        if not path.exists():
            return HAPPY_DEFAULT
        stored = read_json(path, {})
        stored["happiness"] = max(0, min(HAPPY_MAX, stored.get(
            "happiness", HAPPY_DEFAULT) + delta))
        self.write(path, stored)
        return stored["happiness"]

    def bump(self, building:str, name:str, key:str) -> int:
        path = self.folder(building) / f"{slug(name)}.json"
        if not path.exists():
            return 0
        stored = read_json(path, {})
        stored[key] = stored.get(key, 0) + 1
        self.write(path, stored)
        return stored[key]

    def remember(self, building:str,
                 record:dict[str, Any]) -> dict[str, Any]:
        path = self.folder(building) / f"{slug(record['name'])}.json"
        if path.exists():
            stored = complete(building, read_json(path, record))
            stored["visits"] = stored.get("visits", 1) + 1
            stored = drift(stored)
            self.write(path, stored)
            return stored
        if len(self.all(building)) >= REGULARS_CAP:
            return record
        record = complete(building, dict(record, visits=1))
        write_json(path, record)
        return record

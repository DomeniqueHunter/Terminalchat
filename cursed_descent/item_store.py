import hashlib
import json
import re
import uuid
from pathlib import Path
from typing import Any

from .config import ITEM_GENDER_CLASSES, ITEM_STAT_KEYS, ITEMS_DIR_NAME
from .config import ITEM_UNIQUE_SLOTS_EXCLUDED
from .content import ITEMS
from .items import Item, as_item
from .storage import read_json, write_json
from .models import Player


RESTRICTIONS = ("gent", "lady", "both")


def stackable(template_id:str) -> bool:
    slot = ITEMS.get(template_id, {}).get("slot", "consumable")
    return slot in ITEM_UNIQUE_SLOTS_EXCLUDED


def base_stats(template_id:str) -> dict[str, Any]:
    template = ITEMS.get(template_id, {})
    return {key: template[key] for key in ITEM_STAT_KEYS if key in template}


def stack_hash(record:dict[str, Any]) -> str:
    keys = ("template", "owner", "creator", "stats", "for", "traces",
            "soak", "name", "description")
    body = json.dumps({key: record.get(key) for key in keys},
                      sort_keys=True, ensure_ascii=False)
    return hashlib.sha1(body.encode("utf-8")).hexdigest()[:16]


def allowed_for(restriction:str, gender:str) -> bool:
    if restriction in (None, "", "both"):
        return True
    return gender in ITEM_GENDER_CLASSES.get(restriction, ())


class ItemStore:
    def __init__(self, data_path:Path) -> None:
        self.directory = data_path / ITEMS_DIR_NAME
        self.cache: dict[str, dict[str, Any]] = {}

    def path(self, item_id:str) -> Path:
        return self.directory / f"{item_id}.json"

    def get(self, item_id:str) -> dict[str, Any] | None:
        if item_id not in self.cache:
            record = read_json(self.path(item_id), None)
            if record is None:
                return None
            self.cache[item_id] = record
        return self.cache[item_id]

    def exists(self, item_id:str) -> bool:
        return self.get(item_id) is not None

    def save(self, record:dict[str, Any]) -> None:
        self.cache[record["id"]] = record
        write_json(self.path(record["id"]), record)

    def create(self, template_id:str, owner:str, creator:str,
               stats:dict[str, Any] | None=None, restriction:str="both",
               traces:dict[str, Any] | None=None, soak:int=0,
               name:str | None=None, description:str | None=None) -> str:
        template = ITEMS.get(template_id, {})
        record: dict[str, Any] = {
            "id": "", "template": template_id,
            "name": name or template.get("name", template_id),
            "description": (description if description is not None
                            else template.get("note", "")),
            "owner": owner, "creator": creator,
            "stats": dict(base_stats(template_id) if stats is None
                          else stats),
            "for": restriction, "traces": dict(traces or {}), "soak": soak,
        }
        if stackable(template_id):
            record["id"] = stack_hash(record)
            if self.exists(record["id"]):
                return record["id"]
        else:
            record["id"] = uuid.uuid4().hex
        self.save(record)
        return record["id"]

    def transfer(self, item_id:str, new_owner:str) -> str:
        record = self.get(item_id)
        if record is None or record["owner"] == new_owner:
            return item_id
        if stackable(record["template"]):
            moved = dict(record, owner=new_owner)
            moved["id"] = stack_hash(moved)
            if not self.exists(moved["id"]):
                self.save(moved)
            return moved["id"]
        record["owner"] = new_owner
        self.save(record)
        return item_id

    def improve(self, item_id:str, delta:dict[str, int]) -> bool:
        record = self.get(item_id)
        if record is None or stackable(record["template"]):
            return False
        for key, value in delta.items():
            record["stats"][key] = record["stats"].get(key, 0) + value
        self.save(record)
        return True

    def remove(self, item_id:str) -> bool:
        existed = self.exists(item_id)
        self.cache.pop(item_id, None)
        self.path(item_id).unlink(missing_ok=True)
        return existed

    def owned_by(self, owner:str) -> list[str]:
        self.directory.mkdir(parents=True, exist_ok=True)
        found = []
        for path in sorted(self.directory.glob("*.json")):
            record = self.get(path.stem)
            if record is not None and record["owner"] == owner:
                found.append(record["id"])
        return found

    def orphans(self, referenced:set[str]) -> list[str]:
        self.directory.mkdir(parents=True, exist_ok=True)
        return [path.stem for path in sorted(self.directory.glob("*.json"))
                if path.stem not in referenced]

    def record_for(self, item:Item, owner:str, item_id:str) -> dict[str, Any]:
        template = ITEMS.get(str(item), {})
        return {
            "id": item_id, "template": str(item),
            "name": template.get("name", str(item)),
            "description": template.get("note", ""),
            "owner": owner, "creator": item.creator or "shop",
            "stats": dict(base_stats(str(item)) if item.stats is None
                          else item.stats),
            "for": item.restriction, "traces": item.traces,
            "soak": item.soak,
        }

    def bind(self, item:Item, owner:str) -> Item:
        record = self.get(item.iid) if item.iid else None
        if stackable(str(item)):
            record = self.record_for(item, owner, "")
            record["id"] = stack_hash(record)
            if not self.exists(record["id"]):
                self.save(record)
            item.iid = record["id"]
        elif record is None:
            record = self.record_for(item, owner, item.iid or uuid.uuid4().hex)
            self.save(record)
            item.iid = record["id"]
        self.pull(item)
        return item

    def pull(self, item:Item) -> None:
        record = self.get(item.iid)
        if record is None:
            return
        self.refresh_text(record, str(item))
        item.traces = {key: dict(value)
                       for key, value in record["traces"].items()}
        item.soak = record["soak"]
        item.stats = dict(record["stats"])
        item.restriction = record["for"]
        item.creator = record["creator"]

    def refresh_text(self, record:dict[str, Any], template_id:str) -> None:
        template = ITEMS.get(template_id)
        if not template or not template.get("no_loot"):
            return
        text = (template["name"], template.get("note", ""))
        if (record["name"], record["description"]) != text:
            record["name"], record["description"] = text
            self.save(record)

    def push(self, item:Item, owner:str) -> None:
        record = self.get(item.iid)
        if record is None:
            return
        fresh = dict(record, traces=item.traces, soak=item.soak, owner=owner,
                     stats=(record["stats"] if item.stats is None
                            else item.stats),
                     **{"for": item.restriction})
        if record["template"] != str(item):
            template = ITEMS.get(str(item), {})
            fresh.update(template=str(item), stats=base_stats(str(item)),
                         name=template.get("name", str(item)),
                         description=template.get("note", ""))
            item.stats = dict(fresh["stats"])
        if fresh != record:
            self.save(fresh)

    def sync_item(self, item:Item, owner:str) -> None:
        if (item.iid and not stackable(str(item)) and self.exists(item.iid)):
            self.push(item, owner)
        else:
            self.bind(item, owner)

    def sync_player(self, player:Player) -> None:
        for slot, worn in player.equipment.items():
            if worn:
                item = as_item(worn)
                self.sync_item(item, player.id)
                player.equipment[slot] = item
        for index, held in enumerate(player.inventory):
            item = as_item(held)
            self.sync_item(item, player.id)
            player.inventory[index] = item

    def pull_player(self, player:Player) -> None:
        held = list(player.equipment.values()) + list(player.inventory)
        for item in held:
            if isinstance(item, Item) and item.iid:
                self.pull(item)

    def referenced(self, data_path:Path) -> set[str]:
        found: set[str] = set()
        for path in data_path.rglob("*.json"):
            if self.directory in path.parents:
                continue
            found.update(re.findall(r'"iid":\s*"([0-9a-f]+)"',
                                    path.read_text(encoding="utf-8")))
        return found

    def purge(self, data_path:Path) -> list[str]:
        gone = self.orphans(self.referenced(data_path))
        for item_id in gone:
            self.remove(item_id)
        return gone

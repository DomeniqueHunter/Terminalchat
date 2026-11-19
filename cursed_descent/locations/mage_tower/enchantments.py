# Mage tower enchanting: builds enchanted copies of items, stored per settings file.
import copy
import json
import random
import uuid
from pathlib import Path

from ...settings import get
from .content import EFFECTS, MALUS_RANGE


STATS = ("strength", "agility", "vitality", "intelligence")
PLAIN_KEYS = ("damage", "armor", "allure")
STORE = {"path": None}


def upgradable(item_id:str) -> bool:
    from ...content import ITEMS
    item = ITEMS.get(item_id)
    return (item is not None
            and item.get("slot") not in ("consumable", None))


def eligible(player) -> list[tuple[str, str]]:
    worn = [("worn", item_id) for item_id in player.equipment.values()
            if item_id and upgradable(item_id)]
    bag = [("bag", item_id) for item_id in player.inventory
           if upgradable(item_id)]
    return worn + bag


def sale_price(item_id:str) -> int:
    from ..shop.location import base_price
    return base_price(item_id) * 3


def build(item_id:str, amount:int, effect:str,
          rng:random.Random) -> tuple[dict, dict]:
    from ...content import ITEMS
    item = copy.deepcopy(ITEMS[item_id])
    for key in PLAIN_KEYS:
        if key in item:
            item[key] += amount
    bonus = dict(item.get("bonus", {}))
    for stat in STATS:
        bonus[stat] = bonus.get(stat, 0) + amount
    detail = {"effect": effect}
    if effect == "stat_malus":
        stat = rng.choice(STATS)
        cut = rng.randint(*MALUS_RANGE)
        bonus[stat] -= cut
        detail.update(stat=stat, amount=cut)
    if effect == "allure_malus":
        cut = rng.randint(*MALUS_RANGE)
        item["allure"] = item.get("allure", 0) - cut
        detail["amount"] = cut
    if effect == "soul_hunger":
        item["soul_hunger"] = True
    item["bonus"] = bonus
    base = item.get("base_name") or ITEMS[item_id]["name"].split(
        " (Mage's")[0]
    level = item.get("mage_level", 0) + 1
    item["base_name"] = base
    item["mage_level"] = level
    item["name"] = (f"{base} (Mage's)" if level == 1
                    else f"{base} (Mage's x{level})")
    item["note"] = f"enchanted {level}x by the old mage"
    item["price"] = sale_price(item_id)
    item["no_loot"] = True
    item.pop("smith", None)
    return item, detail


def pick_effect(rng:random.Random) -> str:
    return rng.choice(EFFECTS)


def reborn(old, new_id:str):
    from ...items import Item
    if not isinstance(old, Item):
        return new_id
    return Item(new_id, old.traces, old.soak, old.iid, None,
                old.restriction, old.creator)


def replace(player, old_id:str, new_id:str) -> None:
    for slot, item_id in player.equipment.items():
        if item_id == old_id:
            player.equipment[slot] = reborn(item_id, new_id)
            return
    index = player.inventory.index(old_id)
    player.inventory[index] = reborn(player.inventory[index], new_id)


def register(new_id:str, item:dict) -> None:
    from ...content import ITEMS
    ITEMS[new_id] = item


def load_all(path:Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def setup(data_path:Path) -> None:
    STORE["path"] = Path(data_path) / get("mage_tower")["file"]
    for new_id, item in load_all(STORE["path"]).items():
        register(new_id, item)


def create(player, old_id:str, amount:int, effect:str,
           rng:random.Random) -> tuple[str, dict]:
    item, detail = build(old_id, amount, effect, rng)
    new_id = f"mage_{uuid.uuid4().hex[:8]}"
    register(new_id, item)
    path = STORE["path"]
    if path is not None:
        stored = load_all(path)
        stored[new_id] = item
        path.write_text(json.dumps(stored), encoding="utf-8")
    replace(player, old_id, new_id)
    return new_id, detail

from .config import (
    BACKPACK_BASE_PRICE, BACKPACK_CHEAP_EXTRA, BACKPACK_LUXURY_FACTOR,
    BACKPACK_LUXURY_PRICE, BACKPACK_MAX_EXTRA, EQUIPMENT_SLOTS,
)
from .content import ITEMS
from .models import Player


def slot_of(item_id:str) -> str:
    return ITEMS.get(item_id, {}).get("slot", "consumable")


def is_gear(item_id:str) -> bool:
    return slot_of(item_id) in EQUIPMENT_SLOTS


def sort_key(item_id:str) -> tuple[int, int, str]:
    slot = slot_of(item_id)
    name = ITEMS.get(item_id, {}).get("name", str(item_id))
    if slot in EQUIPMENT_SLOTS:
        return 0, EQUIPMENT_SLOTS.index(slot), name
    return 1, 0, name


def sort_inventory(player:Player) -> None:
    player.inventory.sort(key=sort_key)


def grouped(player:Player) -> tuple[list[str], list[str]]:
    gear = [item for item in player.inventory if is_gear(item)]
    consumables = [item for item in player.inventory if not is_gear(item)]
    return gear, consumables


def backpack_price(player:Player) -> int:
    if player.bag_extra < BACKPACK_CHEAP_EXTRA:
        return BACKPACK_BASE_PRICE * (player.bag_extra + 1)
    steps = player.bag_extra - BACKPACK_CHEAP_EXTRA
    return round(BACKPACK_LUXURY_PRICE * BACKPACK_LUXURY_FACTOR ** steps)


def backpack_full(player:Player) -> bool:
    return player.bag_extra >= BACKPACK_MAX_EXTRA

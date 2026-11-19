from ...body import body_effect
from ...config import (
    ALLURE_DISCOUNT, MAX_DISCOUNT, RARITY_PRICES, SELL_RATIO,
    SHOP_CONSUMABLES, STAT_SHORT,
)
from ...content import ITEMS, ITEM_SETS, RARITY_LABELS
from ...formulas import allure
from ...models import Message, Player
from ...smell import smell_note
from .content import SHOPKEEPER
from .npc import greeting


STOCK_WEIGHTS = {"common": 50, "rare": 35, "epic": 10, "cursed": 5}


MAX_STOCK = 10


def item_description(item_id:str) -> str:
    item = ITEMS[item_id]
    parts: list[str] = []
    if item.get("damage"):
        parts.append(f"+{item['damage']} damage")
    if item.get("armor"):
        parts.append(f"+{item['armor']} armor")
    for stat, value in item.get("bonus", {}).items():
        parts.append(f"{value:+d} {STAT_SHORT[stat]}")
    if item.get("heal"):
        parts.append(f"heals {item['heal']}")
    if item.get("mana"):
        parts.append(f"+{item['mana']} mana")
    if item.get("allure"):
        parts.append(f"+{item['allure']} allure")
    details = ", ".join(parts)
    text = f"{item['name']} [{RARITY_LABELS[item['rarity']]}] ({details})"
    if item.get("set") in ITEM_SETS:
        text += f" – set: {ITEM_SETS[item['set']]['name']}"
    if item.get("note"):
        text += f" – {item['note']}"
    if item.get("requires"):
        text += f" – fits: {', '.join(item['requires'])}"
    text += smell_note(item_id)
    return text


def item_summary(item_id:str) -> str:
    text = item_description(item_id)
    note = ITEMS[item_id].get("note")
    return text.replace(f" – {note}", "") if note else text


def base_price(item_id:str) -> int:
    item = ITEMS[item_id]
    if "price" in item:
        return item["price"]
    return RARITY_PRICES[item["rarity"]]


def discount(player:Player | None) -> float:
    if player is None:
        return 0.0
    total = (body_effect(player.body, "discount")
             + allure(player) * ALLURE_DISCOUNT)
    return min(total, MAX_DISCOUNT)


def buy_price(item_id:str, player:Player | None=None) -> int:
    return max(1, round(base_price(item_id) * (1 - discount(player))))


def sell_price(item_id:str) -> int:
    return max(1, round(base_price(item_id) * SELL_RATIO))


def find_index(items:list[str], reference:str) -> int | None:
    reference = reference.strip()
    if reference.isdigit():
        index = int(reference) - 1
        return index if 0 <= index < len(items) else None
    wanted = reference.casefold()
    for index, item_id in enumerate(items):
        if wanted in (item_id, ITEMS[item_id]["name"].casefold()):
            return index
    return None


def velvet_extra(player:Player) -> list[str]:
    if not discount(player):
        return []
    return [SHOPKEEPER["discount"].format(
        percent=round(discount(player) * 100))]


VELVET = {
    "id": "velvet",
    "name": "<<npc.velvet_first>>'s Shop",
    "description": (
        "<<npc.velvet_first>>'s shop is a velvet-draped nook at the dungeon entrance: "
        "racks of lace and leather, a glass case of shiny things, and a "
        "cash drawer that never quite closes. <<npc.velvet_first>> sells armour and "
        "fashion for ladies and gents, a few toys for the bold, and "
        "potions. Swords are not her thing."),
    "categories": ("armor", "weapons", "consumables"),
    "stock": {"armor": 10, "weapons": 6},
    "consumables": SHOP_CONSUMABLES,
    "creator": "shop",
    "texts": {
        "greeting": greeting,
        "extra": velvet_extra,
        "talk": SHOPKEEPER["talk"],
        "buy": SHOPKEEPER["buy"],
        "sell": SHOPKEEPER["sell"],
        "sell_cursed": SHOPKEEPER["sell_cursed"],
        "broke": SHOPKEEPER["broke"],
        "full": SHOPKEEPER["full"],
        "restock": SHOPKEEPER["restock"],
        "which": ("<<npc.velvet_first>> raises an eyebrow. 'Which one, darling? "
                  "[buy <nr>] – [shop] shows the list.'"),
        "which_sell": ("'Sell what, sweetie? [sell <nr>] – your bag "
                       "number.'"),
        "no_category": ("<<npc.velvet_first>> shakes her head. 'No {category} here, "
                        "darling. Try [shop].'"),
    },
}

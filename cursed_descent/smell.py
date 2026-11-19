from .config import (
    FOREIGN_SMELL_TIERS, ITEM_SMELL_MAX, ITEM_SMELL_STAGE_GAIN, SMELL_WORDS,
)
from .items import Item, as_item
from .models import Player
from .sweat import sweat_tier


def absorb_gear(player:Player) -> None:
    tier = sweat_tier(player)
    for slot, worn in player.equipment.items():
        if not worn:
            continue
        item = as_item(worn)
        trace = item.traces.setdefault(player.id, {"strength": 0})
        trace["name"] = player.full_name
        trace["strength"] = min(
            ITEM_SMELL_MAX,
            trace["strength"] + ITEM_SMELL_STAGE_GAIN + tier)
        item.soak += tier
        player.equipment[slot] = item


def foreign_smell(player:Player) -> int:
    return sum(
        trace["strength"]
        for worn in player.equipment.values()
        if isinstance(worn, Item)
        for owner, trace in worn.traces.items() if owner != player.id)


def foreign_tier(player:Player) -> int:
    strength = foreign_smell(player)
    return next((tier for limit, tier in FOREIGN_SMELL_TIERS
                 if strength >= limit), 0)


def smell_note(item:str) -> str:
    if not isinstance(item, Item) or not item.traces:
        return ""
    trace = max(item.traces.values(), key=lambda entry: entry["strength"])
    word = next((word for limit, word in SMELL_WORDS
                 if trace["strength"] >= limit), "")
    return f" – {word} {trace['name']}" if word else ""

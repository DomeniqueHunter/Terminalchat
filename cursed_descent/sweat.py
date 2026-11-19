from .body import muscle_tier
from .config import (
    SWEAT_ARMOR_LIMIT, SWEAT_BUILD_BONUS, SWEAT_GAIN, SWEAT_GEAR_MAX,
    SWEAT_MATERIAL_WORDS, SWEAT_MUSCLE_BONUS, SWEAT_TIERS, SWEAT_TIGHT_SLOTS,
)
from .content import ITEMS, SWEAT_LABELS, SWEAT_TEXTS
from .models import Player


def sweat_tier(player:Player) -> int:
    for limit, tier in SWEAT_TIERS:
        if player.sweat >= limit:
            return tier
    return 0


def sweat_label(player:Player) -> str:
    return SWEAT_LABELS[sweat_tier(player)]


def item_sweat(item:dict) -> int:
    if "sweat" in item:
        return item["sweat"]
    text = f"{item.get('name', '')} {item.get('note', '')}".casefold()
    value = 1 if item.get("slot") in SWEAT_TIGHT_SLOTS else 0
    if item.get("armor", 0) >= SWEAT_ARMOR_LIMIT:
        value += 1
    if any(word in text for word in SWEAT_MATERIAL_WORDS):
        value += 1
    return value


def gear_sweat(player:Player) -> int:
    total = sum(item_sweat(ITEMS[item_id])
                for item_id in player.equipment.values()
                if item_id and item_id in ITEMS)
    return min(total, SWEAT_GEAR_MAX)


def condition_line(player:Player) -> str:
    tier = sweat_tier(player)
    label = f"💧 {SWEAT_LABELS[tier]}" if tier else "dry"
    gear = gear_sweat(player)
    from_gear = f", gear +{gear}/round" if gear else ""
    upcoming = [(limit, step) for limit, step in SWEAT_TIERS if step > tier]
    if not upcoming:
        return f"Sweat: {label} ({player.sweat}, maximum{from_gear})"
    limit, step = min(upcoming)
    return (f"Sweat: {label} ({player.sweat}/{limit} → "
            f"{SWEAT_LABELS[step]}{from_gear})")


def add_sweat(player:Player, kind:str) -> str:
    before = sweat_tier(player)
    muscle = muscle_tier(player.stats, player.body)
    player.sweat += (SWEAT_GAIN.get(kind, 1)
                     + SWEAT_BUILD_BONUS.get(player.body["build"], 0)
                     + SWEAT_MUSCLE_BONUS.get(muscle, 0)
                     + gear_sweat(player))
    after = sweat_tier(player)
    if after == before:
        return ""
    return SWEAT_TEXTS[after].format(name=player.name)

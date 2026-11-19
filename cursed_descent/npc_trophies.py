# Defeated named NPC enemies may drop a replica of one unique piece they wear.
import random
from typing import Any

from .config import TROPHY_CHANCE
from .content import ENEMIES, ITEMS
from .dungeon import stage_gold
from .items import Item
from .models import Player


def owns(player:Player, item_id:str) -> bool:
    held = list(player.inventory) + list(player.equipment.values())
    return any(item and str(item) == item_id for item in held)


def unique_worn(npc:Player) -> list[Any]:
    return [worn for worn in npc.equipment.values()
            if worn and ITEMS[str(worn)]["rarity"] == "epic"
            and f"{worn}_replica" in ITEMS]


def trophy_lines(session:Any, finder:Player) -> list[str]:
    lines: list[str] = []
    for enemy in session.enemies:
        key = ENEMIES.get(enemy.template_id, {}).get("npc")
        if not key or key in session.trophies:
            continue
        npc = next((person for person in session.repository.npc_players()
                    if person.npc == key), None)
        worn = unique_worn(npc) if npc else []
        if not worn or random.random() >= TROPHY_CHANCE:
            continue
        original = random.choice(worn)
        replica = f"{original}_replica"
        name = ITEMS[replica]["name"]
        if owns(finder, replica):
            gold = stage_gold(session.stage) * 2
            finder.gold += gold
            lines.append(f"🎁 {enemy.name} had another {name}, but "
                         f"{finder.name} already owns one. +{gold} gold.")
        elif len(finder.inventory) >= finder.bag_size:
            lines.append(f"🎁 {finder.name} spots a {name} on "
                         f"{enemy.name}, but the bag is full.")
            continue
        else:
            finder.inventory.append(
                Item(replica, creator=getattr(original, "creator", "") or
                     "shop"))
            lines.append(f"🎁 {finder.name} takes a replica of "
                         f"{enemy.name}'s gear: {name}!")
        session.trophies.add(key)
    return lines

import random
from typing import Any

from .content import ITEMS
from .exposure_texts import (
    BRA_WORDS, FULL_BODY_WORDS, LOOSE_WORDS, NO_REACTION, PRUDE_WORDS,
    REACTIONS,
)
from .models import Player


PARTS = ("breasts", "butt", "groin")
SLOT_COVERS = {"chest": ("breasts",), "crotch": ("groin", "butt"),
               "lingerie": ("groin",)}
MAX_DECENCY = 4


def item_covers(item_id:str) -> set[str]:
    item = ITEMS.get(item_id, {})
    slot = item.get("slot", "")
    if "covers" in item:
        covered = set(item["covers"])
    else:
        covered = set(SLOT_COVERS.get(slot, ()))
        name = item.get("name", "").casefold()
        if slot == "chest" and any(word in name for word in FULL_BODY_WORDS):
            covered = set(PARTS)
        if slot == "lingerie" and any(word in name for word in BRA_WORDS):
            covered.add("breasts")
    return covered - set(item.get("reveals", ()))


def covered_parts(player:Player) -> set[str]:
    covered: set[str] = set()
    for slot in SLOT_COVERS:
        worn = player.equipment.get(slot)
        if worn:
            item_id = str(worn["id"] if isinstance(worn, dict) else worn)
            covered |= item_covers(item_id)
    return covered


def exposed_parts(player:Player) -> list[str]:
    covered = covered_parts(player)
    return [part for part in PARTS if part not in covered]


def exposure_level(player:Player) -> str:
    bare = exposed_parts(player)
    if not bare:
        return ""
    return "bare" if len(bare) == len(PARTS) else "partial"


def shift_for(personality:str) -> int:
    text = personality.casefold()
    if any(word in text for word in PRUDE_WORDS):
        return 1
    if any(word in text for word in LOOSE_WORDS):
        return -1
    return 0


def decency_for(town:Any, spec:Any, personality:str="") -> int:
    base = spec.decency if spec is not None and spec.decency is not None \
        else town.decency
    if base == NO_REACTION:
        return NO_REACTION
    return min(max(base + shift_for(personality), 0), MAX_DECENCY)


def on_exposed(player:Player, level:str, parts:list[str], place:str,
               decency:int) -> None:
    """Hook for later effects (prices, entry, favour). Left empty."""


def reaction_line(player:Player, building:str, keeper:str,
                  personality:str="",
                  rng:random.Random | None=None) -> str:
    from .towns import town_of
    level = exposure_level(player)
    if not level:
        return ""
    town = town_of(player)
    spec = next((found for found in town.building_list()
                 if found.key == building), None)
    decency = decency_for(town, spec, personality)
    if decency == NO_REACTION:
        return ""
    parts = exposed_parts(player)
    on_exposed(player, level, parts, building, decency)
    pool = (spec.reaction if spec is not None and spec.reaction
            else f"d{decency}")
    rng = rng or random.Random()
    return rng.choice(REACTIONS[pool][level]).format(
        name=player.name, keeper=keeper)

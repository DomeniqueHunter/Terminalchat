from typing import Any

from .config import CAFE_LOCK, CAFE_RESPAWN_DAYS, DEATH_GOLD_LOSS, KEPT_GEAR_KEY
from .models import Player


def take(player:Player, repository:Any, kind:str, profile:dict[str, Any],
         day:int) -> int:
    lost = int(player.gold * DEATH_GOLD_LOSS)
    kept = dict(player.profile)
    kept.pop(KEPT_GEAR_KEY, None)
    gear = {"equipment": player.equipment, "inventory": player.inventory,
            "gold": player.gold - lost, "free_points": player.free_points}
    player.npc = kind
    player.equipment = {slot: None for slot in player.equipment}
    player.inventory = []
    player.gold = 0
    player.free_points = 0
    player.profile = {**profile, "kept": kept, KEPT_GEAR_KEY: gear}
    player.records[CAFE_LOCK] = 1
    player.records["respawn_day"] = day + CAFE_RESPAWN_DAYS
    repository.path(player.name).unlink(missing_ok=True)
    repository.save(player)
    return lost


def is_captive(player:Player) -> bool:
    return bool(player.npc and KEPT_GEAR_KEY in player.profile)


def free(player:Player, repository:Any, restore:str="") -> None:
    gear = player.profile.get(KEPT_GEAR_KEY)
    player.profile = dict(player.profile.get("kept", {}))
    if gear is not None:
        player.equipment = gear["equipment"]
        player.inventory = gear["inventory"]
        player.gold = gear["gold"]
        player.free_points = gear["free_points"]
    player.npc = restore
    player.records[CAFE_LOCK] = 0
    player.records.pop("respawn_day", None)
    repository.save(player)

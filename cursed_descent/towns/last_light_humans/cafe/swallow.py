from typing import Any

from ....config import CAFE_BERTHA_MAX, SWALLOW_BELLY, SWALLOW_GROWTH
from ....models import Player
from .guests import Guest


BELLY_FULL = ("Your belly is round and tight with {name} – {cm} cm of "
              "swallowed company. It will go down after a night's rest.")
BELLY_GONE = "The swelling in your belly has gone down overnight."


def capped(value:int, step:int, limit:int) -> int:
    return max(value, min(limit, value + step))


def grow_guest(guest:Guest, regulars:Any) -> None:
    kilos, cm = SWALLOW_GROWTH
    guest.weight = capped(guest.weight, kilos, CAFE_BERTHA_MAX[0])
    guest.butt = capped(guest.butt, cm, CAFE_BERTHA_MAX[1])
    if regulars is not None:
        regulars.set("cafe", guest.name, {"weight": guest.weight,
                                          "butt": guest.butt})


def grow_player(player:Player, victim:str) -> str:
    kilos, cm = SWALLOW_GROWTH
    player.body["weight"] = capped(player.body.get("weight", 70), kilos,
                                   CAFE_BERTHA_MAX[0])
    player.body["butt"] = capped(player.body.get("butt", 95), cm,
                                 CAFE_BERTHA_MAX[1])
    player.profile["swallows"] = player.profile.get("swallows", 0) + 1
    player.profile["swallow_belly"] = (
        player.profile.get("swallow_belly", 0) + SWALLOW_BELLY)
    return (f"{BELLY_FULL.format(name=victim, cm=player.profile['swallow_belly'])}"
            f" (+{kilos} kg, +{cm} cm of rear, for good.)")


def clear_belly(player:Player) -> str:
    if not player.profile.pop("swallow_belly", 0):
        return ""
    return BELLY_GONE

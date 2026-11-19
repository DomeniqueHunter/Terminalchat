import random

from ...config import (
    PASS_BRIBE_CHANCE, PASS_BRIBE_COST, PASS_FEE, PASS_TALK_CHANCE,
    PASS_TALK_STEP,
)
from ...models import Player
from ...towns import START_TOWN, TOWNS, Resident, mark_visited


HOWS = ("talk", "pay", "bribe", "sleep")
TEXTS = {
    "have": "You already hold a rail pass for {town}.",
    "talk_ok": "{name} talks to {keeper} about trains, timetables and "
               "the weather, and {keeper} finally warms up. 'Fine. A "
               "pass for {town}. Do not lose it.'",
    "talk_fail": "{keeper} listens with a flat face and stamps nothing. "
                 "'Come back when you have something better to say.'",
    "pay_ok": "{name} pays {price} gold. {keeper} counts it, nods and "
              "stamps a rail pass for {town}.",
    "bribe_ok": "{name} slips {price} gold under the counter. {keeper} "
                "looks away, and a pass for {town} appears in {name}'s "
                "hand.",
    "bribe_fail": "{keeper} pushes the coins back, then pockets them. "
                  "'Bribing a stationmaster? Outrageous.' No pass, and "
                  "{price} gold gone.",
    "poor": "A pass costs {price} gold. {name} only has {gold}.",
    "sleep": "{name} follows {keeper} into the back office. The door "
             "closes, the blinds come down and the timetable on the wall "
             "stops mattering for a good while. When {name} comes out "
             "again, a stamped rail pass for {town} is in a warm "
             "hand.",
    "usage": "Rail pass for {town}: [ticket talk] (free, may fail), "
             "[ticket pay] ({fee} gold), [ticket bribe] ({bribe} gold, "
             "may fail) or [ticket sleep] with {keeper}.",
}


def passes(player:Player) -> list[str]:
    owned = [key for key in player.profile.get("rail_pass", [])
             if key in TOWNS]
    return owned if START_TOWN in owned else [START_TOWN] + owned


def has_pass(player:Player, key:str) -> bool:
    return key in passes(player)


def grant_pass(player:Player, key:str) -> None:
    owned = list(player.profile.get("rail_pass", []))
    if key not in owned:
        owned.append(key)
    player.profile["rail_pass"] = owned
    mark_visited(player, key)


def keeper_of(key:str) -> Resident | None:
    return next((resident for resident in TOWNS[key].residents
                 if resident.building == "station"), None)


def keeper_name(key:str) -> str:
    keeper = keeper_of(key)
    return f"{keeper.first_name} {keeper.last_name}" if keeper else (
        "the stationmaster")


def usage(key:str) -> str:
    return TEXTS["usage"].format(
        town=TOWNS[key].name, fee=PASS_FEE, bribe=PASS_BRIBE_COST,
        keeper=keeper_name(key))


def try_pass(player:Player, key:str, how:str,
             rng:random.Random | None=None) -> tuple[bool, str]:
    rng = rng or random
    values = {"name": player.name, "town": TOWNS[key].name,
              "keeper": keeper_name(key), "gold": player.gold}
    if has_pass(player, key):
        return True, TEXTS["have"].format(**values)
    if how == "talk":
        fails = player.profile.setdefault("pass_fails", {})
        chance = PASS_TALK_CHANCE + PASS_TALK_STEP * fails.get(key, 0)
        if rng.random() < chance:
            grant_pass(player, key)
            return True, TEXTS["talk_ok"].format(**values)
        fails[key] = fails.get(key, 0) + 1
        return False, TEXTS["talk_fail"].format(**values)
    if how in ("pay", "bribe"):
        price = PASS_FEE if how == "pay" else PASS_BRIBE_COST
        values["price"] = price
        if player.gold < price:
            return False, TEXTS["poor"].format(**values)
        player.gold -= price
        if how == "bribe" and rng.random() >= PASS_BRIBE_CHANCE:
            return False, TEXTS["bribe_fail"].format(**values)
        grant_pass(player, key)
        return True, TEXTS[f"{how}_ok"].format(**values)
    if how == "sleep":
        grant_pass(player, key)
        return True, TEXTS["sleep"].format(**values)
    return False, usage(key)

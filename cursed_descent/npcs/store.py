from ..content import ITEMS
from ..items import item_state, restore_item
from ..models import Player


KEEPER_FATES = {"brewed": "astrid", "fashion": "velvet",
                "smothered": "bertha", "collapsed": "bertha", "engulfed": "bertha",
                "vored": "bertha", "anal_vored": "astrid",
                "smoked": "jorveig", "spit_roasted": "gul", "milked_dry": "odile",
                "bull_stud": "odile", "culled": "odile"}


def find_local(players:list[Player], text:str) -> Player | None:
    wanted = text.strip().casefold()
    if not wanted:
        return None
    for player in players:
        names = (player.npc.casefold(), player.name.casefold(),
                 player.first_name.casefold(), player.full_name.casefold())
        if wanted in names:
            return player
    for player in players:
        words = f"{player.first_name} {player.last_name}".casefold().split()
        if wanted in words:
            return player
    return None


def residents_of(players:list[Player], buildings:tuple[str, ...],
                 town:str="last_light") -> list[Player]:
    return [player for player in players
            if player.profile.get("kind") == "resident"
            and player.profile.get("town", "last_light") == town
            and player.profile.get("building") in buildings]


def credit_kill(npcs:list[Player], fate:str) -> Player | None:
    keeper = find_local(npcs, KEEPER_FATES.get(fate, ""))
    if keeper is not None:
        keeper.records["kills"] = keeper.records.get("kills", 0) + 1
    return keeper


def keeper_shoes(fate:str, victim:Player | None, garment:str) -> str:
    if fate == "brewed" and victim is not None:
        worn = victim.equipment.get("feet")
        return restore_item(str(worn), item_state(worn)) if worn else ""
    if fate == "fashion" and garment and ITEMS[garment]["slot"] == "feet":
        return garment
    return ""


def dress_keeper(npcs:list[Player], fate:str, victim:Player | None=None,
                 garment:str="") -> Player | None:
    keeper = find_local(npcs, KEEPER_FATES.get(fate, ""))
    shoes = keeper_shoes(fate, victim, garment)
    if keeper is None or not shoes:
        return None
    keeper.equipment["feet"] = shoes
    return keeper

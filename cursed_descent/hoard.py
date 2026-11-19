import random
from typing import Any

from .content import ITEMS
from .items import item_state, remove_item, restore_item
from .models import Player


HOARD_TEXTS = {
    "found": "🎒 {name} finds what {dead} left behind: {items}.",
    "full": "🎒 {name}'s bag is full – the rest stays behind.",
    "hint": "Something is left behind here: {dead}'s belongings.",
    "lost": "🎒 {killer} keeps {name}'s belongings: {items}.",
}


def lost_line(player:Player, killer:str,
              hoard:list[dict[str, Any]] | None) -> list[str]:
    if not hoard:
        return []
    items = ", ".join(ITEMS[piece["item"]]["name"] for piece in hoard)
    return [HOARD_TEXTS["lost"].format(killer=killer.capitalize(),
                                       name=player.name, items=items)]


def confiscate(player:Player, take_chance:float,
               rng:random.Random | None=None) -> list[dict[str, Any]]:
    rng = rng or random
    taken: list[dict[str, Any]] = []
    for item in list(player.inventory):
        if rng.random() < take_chance:
            taken.append({"item": str(item), "state": item_state(item)})
            remove_item(player.inventory, item)
    for slot, item in list(player.equipment.items()):
        if item and rng.random() < take_chance:
            taken.append({"item": str(item), "state": item_state(item)})
            player.equipment[slot] = None
    return taken


def open_hoards(remains:Any, fates:tuple[str, ...],
                run_id:str) -> list[dict[str, Any]]:
    return [entry for entry in remains.entries
            if entry["fate"] in fates and entry.get("hoard")
            and entry["run"] != run_id]


def hoard_note(remains:Any, fates:tuple[str, ...], run_id:str) -> str:
    entries = open_hoards(remains, fates, run_id)
    if not entries:
        return ""
    return HOARD_TEXTS["hint"].format(dead=entries[0]["name"])


def take_hoards(remains:Any, fates:tuple[str, ...], run_id:str,
                player:Player) -> list[str]:
    lines: list[str] = []
    for entry in open_hoards(remains, fates, run_id):
        names: list[str] = []
        for piece in list(entry["hoard"]):
            if len(player.inventory) >= player.bag_size:
                lines.append(HOARD_TEXTS["full"].format(name=player.name))
                break
            player.inventory.append(restore_item(piece["item"],
                                                 piece.get("state")))
            entry["hoard"].remove(piece)
            names.append(ITEMS[piece["item"]]["name"])
        if names:
            lines.insert(0, HOARD_TEXTS["found"].format(
                name=player.name, dead=entry["name"],
                items=", ".join(names)))
        if len(player.inventory) >= player.bag_size:
            break
    remains.save()
    return lines

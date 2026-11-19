from ..locations.shop.location import item_description
from ..models import Player
from ..scenes import DEFAULTS
from ..view import Button, Choice, Panel


TRADE_FIELD = "trade_item"
NEIGHBOUR_ACTIONS = (("Gift", "gift"), ("Barter", "barter"),
                     ("Coach", "coach"), ("Romance", "romance"))
SCENE_KEYS = ("position", "role", "amount", "where")


def item_choice(player:Player) -> Choice:
    options = tuple((str(number), f"{number}. "
                     f"{item_description(item_id).splitlines()[0]}")
                    for number, item_id in enumerate(player.inventory, 1))
    return Choice(TRADE_FIELD, "Item", options, "select")


def neighbours_panel(town, player:Player) -> Panel | None:
    if not town.residents:
        return None
    sections = tuple(Panel(resident.first_name, buttons=tuple(
        Button(label, f"!{word} {resident.key}")
        for label, word in NEIGHBOUR_ACTIONS))
        for resident in town.residents)
    return Panel("Neighbours", sections=sections,
                 choices=(item_choice(player),))


def trade_text(text:str, data:dict) -> str:
    words = text.split()
    if len(words) != 2:
        return text
    if words[0] in ("!gift", "!barter"):
        number = str(data.get(TRADE_FIELD, "")).strip()
        return f"{text} {number}" if number.isdigit() else ""
    if words[0] == "!romance":
        scene = [str(data.get(f"s_{key}", "")).strip() or DEFAULTS[key]
                 for key in SCENE_KEYS]
        return " ".join((text, *scene))
    return text


def guest_trade_row(name:str, here:bool) -> tuple[Button, ...]:
    first = name.split()[0]
    return (Button("Gift", f"!gift {first}", "", here),
            Button("Barter", f"!barter {first}", "", here))


from typing import Any

from ..controller import GameController
from ..houses import chest_of, hosted_by
from ..town_buildings.bank.ledger import limit_of
from ..locations.shop.location import item_description
from ..models import Player
from ..towns import town_of
from ..view import Button, Panel


GOLD_STEPS = (100, 1000)
KINDS = {
    "bank": {
        "title": "🏦 Bank", "place": "bank",
        "put": "!deposit {nr}", "take": "!withdraw {nr}",
        "put_gold": "!deposit gold {amount}",
        "take_gold": "!withdraw gold {amount}",
        "right": "Vault",
    },
    "home": {
        "title": "🏠 House chest", "place": "home",
        "put": "!home store {nr}", "take": "!home take {nr}",
        "put_gold": "!home store gold {amount}",
        "take_gold": "!home take gold {amount}",
        "right": "Chest",
    },
}


def account_of(controller:GameController, player:Player, kind:str) -> Any:
    if kind == "bank":
        return controller.town.bank.account(player)
    town = town_of(player)
    if hosted_by(player, town.key, controller.repository) is not None:
        return None
    return chest_of(player, town.key)


def available(controller:GameController, player:Player, kind:str) -> bool:
    if kind not in KINDS or controller.session.in_run(player.name):
        return False
    if controller.town.where(player) != KINDS[kind]["place"]:
        return False
    return account_of(controller, player, kind) is not None


def summary_panel(title:str, account:Any, kind:str,
                  lines:tuple[str, ...]=()) -> Panel:
    return Panel(title, (*lines, f"Gold: {account.gold} 💰",
                         f"Items: {len(account.items)}/{limit_of(account)} 🎒"),
                 (Button("Inventory", f"!stash {kind}"),))


def gold_buttons(spec:dict, key:str, gold:int, arrow:str) -> list[dict]:
    amounts = [*GOLD_STEPS, "all"]
    buttons = []
    for amount in amounts:
        label = "All" if amount == "all" else str(amount)
        label = f"{label} →" if arrow == "→" else f"← {label}"
        enabled = gold > 0 if amount == "all" else gold >= amount
        buttons.append({"label": label, "enabled": enabled,
                        "command": spec[key].format(amount=amount)})
    return buttons


def side(title:str, items:list[str], gold:int, capacity:int, spec:dict,
         item_key:str, gold_key:str, arrow:str, full:bool) -> dict:
    return {
        "title": title, "gold": gold, "count": len(items),
        "capacity": capacity, "arrow": arrow, "full": full,
        "items": [{"label": item_description(item_id),
                   "command": spec[item_key].format(nr=number)}
                  for number, item_id in enumerate(items, 1)],
        "gold_buttons": gold_buttons(spec, gold_key, gold, arrow),
    }


def overlay(controller:GameController, player:Player,
            kind:str) -> dict | None:
    if not available(controller, player, kind):
        return None
    spec = KINDS[kind]
    account = account_of(controller, player, kind)
    return {
        "kind": kind, "title": spec["title"],
        "left": side("Your bag", player.inventory, player.gold,
                     player.bag_size, spec, "put", "put_gold", "→",
                     len(account.items) >= limit_of(account)),
        "right": side(spec["right"], account.items, account.gold,
                      limit_of(account), spec, "take", "take_gold", "←",
                      len(player.inventory) >= player.bag_size),
    }

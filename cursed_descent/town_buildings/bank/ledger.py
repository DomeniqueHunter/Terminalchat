from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ...config import BANK_FILE_NAME, BANK_SLOTS
from ...content import ITEMS
from ...items import item_from_json, item_to_json
from ...locations.shop.location import item_description
from ...models import Message, Player
from ...storage import read_json, write_json


CLOSED = "The bank is shut while you are down in the dungeon."
USAGE = ("[deposit <nr>|gold <n>|gold all] and "
         "[withdraw <nr>|gold <n>|gold all]")


@dataclass
class Account:
    gold: int = 0
    items: list[str] = field(default_factory=list)


class Bank:
    def __init__(self, data_path:Path) -> None:
        self.path = data_path / BANK_FILE_NAME
        self.accounts: dict[str, Account] = {}
        for char_id, data in read_json(self.path, {}).items():
            self.accounts[char_id] = Account(
                data.get("gold", 0),
                [item_from_json(item) for item in data.get("items", [])])

    def account(self, player:Player) -> Account:
        return self.accounts.setdefault(player.id, Account())

    def save(self) -> None:
        write_json(self.path, {
            char_id: {"gold": account.gold,
                      "items": [item_to_json(item)
                                for item in account.items]}
            for char_id, account in self.accounts.items()
            if account.gold or account.items})


def limit_of(account:Any) -> int:
    return getattr(account, "capacity", 0) or BANK_SLOTS


def bank_menu(player:Player, account:Account, title:str="🏦 The Bank",
              usage:str=USAGE) -> list[Message]:
    lines = [f"{title} – {len(account.items)}/{limit_of(account)} slots",
             f"💰 Carried: {player.gold} gold   🔒 Stored: "
             f"{account.gold} gold"]
    for nr, item in enumerate(account.items, 1):
        lines.append(f"  [{nr}] {item_description(item)}")
    if not account.items:
        lines.append("  (no items stored)")
    lines.append(usage)
    return [Message("\n".join(lines), player.name)]


def parse_amount(text:str, available:int) -> int | None:
    if text == "all":
        return available
    if text.isdigit() and int(text) > 0:
        return int(text)
    return None


def move_gold(player:Player, account:Account, args:list[str],
              deposit:bool) -> list[Message]:
    source = player.gold if deposit else account.gold
    amount = parse_amount(args[1] if len(args) > 1 else "", source)
    if amount is None:
        return [Message(USAGE, player.name)]
    if amount > source or amount == 0:
        return [Message("Not enough gold for that.", player.name)]
    delta = -amount if deposit else amount
    player.gold += delta
    account.gold -= delta
    verb = "Deposited" if deposit else "Withdrew"
    return [Message(f"{verb} {amount} gold. 💰 Carried: {player.gold}   "
                    f"🔒 Stored: {account.gold}", player.name)]


def move_item(player:Player, account:Account, args:list[str],
              deposit:bool) -> list[Message]:
    source = player.inventory if deposit else account.items
    target = account.items if deposit else player.inventory
    limit = limit_of(account) if deposit else player.bag_size
    if not args or not args[0].isdigit():
        return [Message(USAGE, player.name)]
    index = int(args[0]) - 1
    if not 0 <= index < len(source):
        return [Message("No item with that number.", player.name)]
    if len(target) >= limit:
        place = "The vault is full." if deposit else "Your bag is full."
        return [Message(place, player.name)]
    item = source.pop(index)
    target.append(item)
    verb = "Stored" if deposit else "Took back"
    return [Message(f"{verb}: {ITEMS[item]['name']}.", player.name)]


def bank_move(player:Player, account:Account, args:list[str], deposit:bool,
              in_run:bool) -> list[Message]:
    if in_run:
        return [Message(CLOSED, player.name)]
    if args and args[0] == "gold":
        return move_gold(player, account, args, deposit)
    return move_item(player, account, args, deposit)

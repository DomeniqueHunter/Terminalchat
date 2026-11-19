from ..items import Item
from ..models import Message, Player
from ..needs import satisfy


from collections.abc import Callable

from .dishes import MENUS, TITLES, dish_id




def menu_lines(building:str) -> list[str]:
    lines = [f"Menu – [order {building} <nr|name>] eats it now, add "
             f"'take' to put it in your bag:"]
    for number, (key, (name, price, _)) in enumerate(
            MENUS[building].items(), 1):
        lines.append(f"  {number}. {name} – {price} gold")
    return lines


def find_dish(building:str, text:str) -> str:
    wanted = text.strip().casefold()
    keys = list(MENUS[building])
    if wanted.isdigit() and 1 <= int(wanted) <= len(keys):
        return keys[int(wanted) - 1]
    for key, (name, _, _) in MENUS[building].items():
        if wanted in (key, name.casefold()):
            return key
    return ""


TAKE_WORDS = {"take", "takeaway", "bag", "togo", "go"}


def order(player:Player, args:list[str], in_run:bool,
          on_eat:Callable[[str, str], list[Message]] | None=None
          ) -> list[Message]:
    building = args[0].casefold() if args else ""
    if building not in MENUS:
        return [Message("[order tavern <dish> [take]] or [order cafe "
                        "<dish> [take]].", player.name)]
    if in_run:
        return [Message(f"The {TITLES[building]} is shut while you are in "
                        f"the dungeon.", player.name)]
    words = args[1:]
    takeaway = bool(words) and words[-1].casefold() in TAKE_WORDS
    if takeaway:
        words = words[:-1]
    elif words and words[-1].casefold() == "eat":
        words = words[:-1]
    key = find_dish(building, " ".join(words))
    if not key:
        return [Message("\n".join(menu_lines(building)), player.name)]
    name, price, effects = MENUS[building][key]
    if player.gold < price:
        return [Message(f"{name} costs {price} gold.", player.name)]
    if takeaway:
        if len(player.inventory) >= player.bag_size:
            return [Message("Your bag is full.", player.name)]
        player.gold -= price
        player.inventory.append(Item(dish_id(building, key),
                                         creator=building))
        return [Message(f"🥡 {player.name} takes {name} to go for {price} "
                        f"gold. ([consume] it any time) 💰 {player.gold}",
                        player.name)]
    player.gold -= price
    changes = satisfy(player.needs, effects)
    detail = ", ".join(f"{need} {amount:+d}"
                       for need, amount in changes.items()) or "no effect"
    messages = [Message(f"🍽️ {player.name} eats {name} on the spot for "
                        f"{price} gold: {detail}. 💰 {player.gold}",
                        player.name)]
    return messages + (on_eat(building, key) if on_eat else [])

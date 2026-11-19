from ..content import ITEMS
from ..inventory import backpack_full, backpack_price
from ..locations.shop.location import (
    buy_price, item_description, sell_price,
)
from ..models import Player
from ..shop_system import ARMOR_TABS, Shop, tag_of
from ..view import Button, Panel, Row


def options_of(shop:Shop, category:str) -> list[str]:
    if category == "armor":
        return list(ARMOR_TABS)
    if category == "weapons":
        return shop.classes()
    return []


def item_rows(shop:Shop, player:Player, word:str, category:str,
              option:str, closed:bool) -> tuple[Row, ...]:
    numbers = shop.offers()
    rows = []
    for item_id in shop.view_items(category, option):
        price = buy_price(item_id, player)
        rows.append(Row(f"{item_description(item_id)}{tag_of(item_id)}",
                        (Button(f"Buy {price}",
                                f"!{word} {numbers.index(item_id) + 1}", "",
                                not closed and player.gold >= price),)))
    return tuple(rows)


def category_panel(shop:Shop, player:Player, word:str, category:str,
                   closed:bool) -> Panel:
    options = options_of(shop, category)
    if not options:
        return Panel(category.capitalize(), rows=item_rows(
            shop, player, word, category, "", closed))
    sections = [Panel("all", rows=item_rows(shop, player, word, category,
                                            "", closed))]
    sections += [Panel(name, rows=item_rows(shop, player, word, category,
                                            name, closed))
                 for name in options]
    return Panel(category.capitalize(), sections=tuple(sections),
                 tabbed=True)


def sell_panel(player:Player) -> Panel:
    groups: dict[str, list[int]] = {}
    for index, item_id in enumerate(player.inventory, 1):
        groups.setdefault(item_id, []).append(index)
    rows = []
    for item_id, indices in groups.items():
        stack = f"{len(indices)}× " if len(indices) > 1 else ""
        rows.append(Row(f"{stack}{ITEMS[item_id]['name']}", (
            Button(f"Sell {sell_price(item_id)}", f"!sell {indices[0]}"),)))
    return Panel("Sell from bag", () if rows else ("empty",), rows=tuple(rows))


def backpack_panel(player:Player) -> Panel:
    price = backpack_price(player)
    full = backpack_full(player)
    return Panel("Pack-maker", (f"Bag: {player.bag_size} slots "
                                f"(+{player.bag_extra})",), (
        Button("Maxed out" if full else f"Buy slot ({price} gold)",
               "!backpack buy", "", not full and player.gold >= price),))


def shop_sections(shop:Shop, player:Player, word:str, buy_word:str,
                  closed:bool) -> tuple[Panel, ...]:
    categories = Panel("Wares", sections=tuple(
        category_panel(shop, player, buy_word, name, closed)
        for name in shop.defn.categories), tabbed=True,
        buttons=(Button("Examine", f"!{word} examine"),
                 Button("Talk", f"!{word} talk")))
    return (categories,)

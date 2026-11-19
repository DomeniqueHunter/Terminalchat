from ....locations.shop.location import buy_price, item_description
from ....models import Player
from ....shop_system import tag_of
from ....view import Button, Panel, Row
from .content import GROUPS, KEY, SPECIAL, group_of
from .items import ITEMS

SIDES = {"ladies": "lady", "gents": "gent"}


def rows_of(player:Player, group:str, side:str, closed:bool) -> tuple[Row, ...]:
    rows = []
    for number, offer in enumerate(SPECIAL.offers, 1):
        if group_of(offer.item) != group:
            continue
        if side and ITEMS[offer.item].get("for", "both") not in (
                SIDES[side], "both"):
            continue
        price = buy_price(offer.item, player)
        rows.append(Row(f"{item_description(offer.item)}{tag_of(offer.item)}",
                        (Button(f"Buy {price}", f"!{KEY} {number}", "",
                                not closed and player.gold >= price),)))
    return tuple(rows)


def group_panel(player:Player, group:str, closed:bool) -> Panel:
    sections = [Panel("all", rows=rows_of(player, group, "", closed))]
    sections += [Panel(side, rows=rows_of(player, group, side, closed))
                 for side in SIDES]
    return Panel(group, sections=tuple(sections), tabbed=True)


def panel(services, player:Player) -> Panel:
    closed = services.in_run(player)
    wares = Panel("Wares", sections=tuple(
        group_panel(player, group, closed) for group in GROUPS), tabbed=True)
    return Panel(f"{SPECIAL.icon} {SPECIAL.title}",
                 (SPECIAL.blurb, f"💰 {player.name}: {player.gold} gold"),
                 sections=(wares,))

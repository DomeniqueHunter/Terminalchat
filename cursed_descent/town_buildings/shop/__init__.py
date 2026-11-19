from ..base import Building


def ui(services, player):
    from ...locations.shop.ui import panel
    return panel(services, player)


class Shop(Building):
    key = "shop"
    greeting = ("Browse the shelves or sell me your loot – [shop] shows "
                "what I have.")
    icon = "🛍"
    ui = ui
    title = "Shop"
    label = "Shop"
    blurb = "Supplies for the road down."
    order = 20

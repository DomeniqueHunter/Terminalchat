from ...models import Player
from ...towns import town_of
from ...towns.localize import localize_text
from ...view import Button, Panel
from ...town_buildings import shop_ui


def panel(services, player:Player) -> Panel:
    shop = services.session.shop.shops["velvet"]
    sections = (*shop_ui.shop_sections(shop, player, "shop", "buy", False),
                shop_ui.sell_panel(player), shop_ui.backpack_panel(player))
    return Panel("🛍 Shop", (f"💰 {player.name}: {player.gold} gold",), (
        Button(localize_text("Talk to <<npc.velvet_first>>", town_of(player)),
               "!shop"),), sections)

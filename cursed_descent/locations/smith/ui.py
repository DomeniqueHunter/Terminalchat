from ...models import Player
from ...towns import town_of
from ...towns.localize import localize_text
from ...view import Panel
from ...town_buildings import shop_ui


def panel(services, player:Player) -> Panel:
    shop = services.session.shop.shops["smith"]
    in_run = services.in_run(player)
    title = localize_text("⚒ <<npc.morgrin_first>>'s Forge", town_of(player))
    lines = (f"💰 {player.name}: {player.gold} gold",
             *(("Closed during a run.",) if in_run else ()))
    return Panel(title, lines, (), shop_ui.shop_sections(
        shop, player, "smith", "forge", in_run))

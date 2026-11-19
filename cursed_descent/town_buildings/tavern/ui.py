from ...models import Player
from ...towns import town_of
from ...towns.localize import localize_text
from ...view import Button, Panel
from ..work import ui as work_ui
from .content import OWNER, PLACE, TAVERN_CUT, TAVERN_ROOMS


def panel(services, player:Player) -> Panel:
    town = town_of(player)
    lines = (localize_text(PLACE, town),
             localize_text(f"Owner {OWNER} keeps "
                           f"{round(TAVERN_CUT * 100)}%", town))
    rooms = Panel("Sleep (rooms)", (), tuple(
        Button(f"{kind.capitalize()} room ({price} g)", f"!room {kind}", "",
               player.gold >= price) for kind, price in TAVERN_ROOMS.items()))
    from .pods import pod_panel
    shift = services.shifts.get(player.name)
    return Panel("🍺 Tavern", lines, (), work_ui.compact(
        pod_panel(player),
        work_ui.shift_panel(services, player, shift, "tavern"),
        work_ui.workers_panel(services, player, "tavern"),
        work_ui.jobs_panel("tavern", player),
        work_ui.orders_panel("tavern", player), rooms))

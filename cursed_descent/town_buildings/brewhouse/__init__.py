from dataclasses import replace

from ..counter import counter_command
from ..base import Building
from . import content
from .rules import (
    finish_hook, greeter, idle_hook, make_items, round_hook, setup,
    start_bath, start_service, start_vore, vat_command,
)


def shift_ui(services, player, shift):
    from .ui import vat_panel
    return vat_panel(shift)


class Brewhouse(Building):
    key = content.KEY
    title = content.TITLE
    label = "Brewhouse"
    blurb = content.BLURB
    owner = content.OWNER
    place = content.PLACE
    closed = content.CLOSED
    cut = content.CUT
    jobs = content.JOBS
    session_lines = content.SESSION_LINES
    counter = replace(content.SPECIAL,
                      starters={"bath": start_bath, "vore": start_vore,
                                "service": start_service})
    icon = "🍺"
    place_commands = (content.KEY,)
    items = make_items
    finish_hook = finish_hook
    round_hook = round_hook
    idle_hook = idle_hook
    setup = setup
    greeter = greeter
    shift_ui = shift_ui
    commands = {content.KEY: counter_command(content.KEY),
                "vat": vat_command}
    order = 100

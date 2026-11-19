from ..base import Building
from . import content


def ui(services, player):
    from ...locations.smith.ui import panel
    return panel(services, player)


class Smith(Building):
    key = "smith"
    greeting = content.OFFER
    icon = "⚒"
    ui = ui
    help = content.HELP
    title = "Smith"
    label = "Smith"
    blurb = "<<npc.morgrin_first>> forges weapons that crave souls."
    order = 30

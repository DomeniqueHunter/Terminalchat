from ...config import BROTHEL_CUT
from ..base import Building
from . import content
from .building import COMMANDS


def ui(services, player):
    from .ui import panel
    return panel(services, player)


class Brothel(Building):
    decency = 0
    reaction = "brothel"
    key = "brothel"
    owner = content.OWNER
    place = content.PLACE
    closed = content.CLOSED
    cut = BROTHEL_CUT
    greeting = content.OFFER
    icon = "🌹"
    commands = COMMANDS
    place_commands = ("brothel",)
    ui = ui
    help = content.HELP
    title = "Brothel"
    label = "Brothel"
    blurb = "The <<npc.rose_first>> Chamber, run by Madame <<npc.rose_first>>."
    order = 70

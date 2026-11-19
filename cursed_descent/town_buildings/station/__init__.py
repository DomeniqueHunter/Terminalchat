from ..base import Building
from .building import COMMANDS


def ui(services, player):
    from .ui import panel
    return panel(services, player)


class Station(Building):
    key = "station"
    commands = COMMANDS
    place_commands = ("station", "travel", "ticket")
    ui = ui
    title = "Station"
    label = "Station"
    blurb = "Trains to the other towns, for a fare."
    order = 10

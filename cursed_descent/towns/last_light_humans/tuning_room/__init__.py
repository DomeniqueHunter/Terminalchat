from ....town_buildings import Building
from . import content
from .rules import do_tuning_room


def ui(services, player):
    from .ui import panel
    return panel(services, player)


class TuningRoom(Building):
    decency = 1
    key = content.KEY
    title = content.TITLE
    blurb = content.BLURB
    greeting = content.OFFER
    icon = "🎛"
    commands = {content.KEY: do_tuning_room}
    place_commands = (content.KEY,)
    ui = ui
    help = content.HELP
    order = 110


BUILDING = TuningRoom()

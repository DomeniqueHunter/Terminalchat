from dataclasses import replace

from ....town_buildings.counter import counter_command
from ....town_buildings import Building
from . import content


def drink(services, player, offer):
    from .rules import drink as run
    return run(services, player, offer)


class EmberCask(Building):
    key = content.KEY
    title = content.TITLE
    blurb = content.BLURB
    owner = content.OWNER
    place = content.PLACE
    closed = content.CLOSED
    cut = content.CUT
    jobs = content.JOBS
    session_lines = content.SESSION_LINES
    counter = replace(content.SPECIAL, starters={"drink": drink})
    icon = "🍺"
    place_commands = (content.KEY,)
    commands = {content.KEY: counter_command(content.KEY)}
    order = 100


BUILDING = EmberCask()

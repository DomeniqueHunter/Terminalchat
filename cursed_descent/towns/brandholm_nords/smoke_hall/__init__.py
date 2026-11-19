from dataclasses import replace

from ....town_buildings.counter import counter_command
from ....town_buildings import Building
from . import content


def short(services, player, offer):
    from .rules import short as run
    return run(services, player, offer)


def box(services, player, offer):
    from .rules import box as run
    return run(services, player, offer)


class Smokehouse(Building):
    key = content.KEY
    title = content.TITLE
    blurb = content.BLURB
    owner = content.OWNER
    place = content.PLACE
    closed = content.CLOSED
    cut = content.CUT
    jobs = content.JOBS
    session_lines = content.SESSION_LINES
    counter = replace(content.SPECIAL, starters={"short": short, "box": box})
    icon = "🔥"
    place_commands = (content.KEY,)
    commands = {content.KEY: counter_command(content.KEY)}
    order = 102


BUILDING = Smokehouse()

from dataclasses import replace

from ....town_buildings.counter import counter_command
from ....town_buildings import Building
from . import content


def mask(services, player, offer):
    from .rules import mask as run
    return run(services, player, offer)


def sit(services, player, offer):
    from .rules import sit as run
    return run(services, player, offer)


class SteamHall(Building):
    key = content.KEY
    title = content.TITLE
    blurb = content.BLURB
    owner = content.OWNER
    place = content.PLACE
    closed = content.CLOSED
    cut = content.CUT
    jobs = content.JOBS
    session_lines = content.SESSION_LINES
    counter = replace(content.SPECIAL, starters={"mask": mask, "sit": sit})
    icon = "♨"
    place_commands = (content.KEY,)
    commands = {content.KEY: counter_command(content.KEY)}
    order = 101


BUILDING = SteamHall()

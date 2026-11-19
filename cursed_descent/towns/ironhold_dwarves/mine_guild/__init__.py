from ....town_buildings.counter import counter_command
from ....town_buildings import Building
from . import content
from .rules import round_hook


class MineGuild(Building):
    key = content.KEY
    title = content.TITLE
    blurb = content.BLURB
    owner = content.OWNER
    place = content.PLACE
    closed = content.CLOSED
    cut = content.CUT
    jobs = content.JOBS
    session_lines = content.SESSION_LINES
    counter = content.SPECIAL
    icon = "⛏"
    round_hook = round_hook
    place_commands = (content.KEY,)
    commands = {content.KEY: counter_command(content.KEY)}
    order = 85


BUILDING = MineGuild()

from dataclasses import replace

from ....town_buildings.counter import counter_command
from ....town_buildings import Building
from . import content


def lazy(name:str):
    def starter(services, player, offer):
        from . import rules
        return getattr(rules, name)(services, player, offer)
    return starter


def lock(services, player, command):
    from .rules import lock as run
    return run(services, player, command)


class CreamRoom(Building):
    key = content.KEY
    title = content.TITLE
    blurb = content.BLURB
    owner = content.OWNER
    place = content.PLACE
    closed = content.CLOSED
    cut = content.CUT
    jobs = content.JOBS
    session_lines = content.SESSION_LINES
    counter = replace(content.SPECIAL,
                      starters={"fill": lazy("fill"), "bless": lazy("bless")})
    icon = "🥛"
    place_commands = (content.KEY,)
    commands = {content.KEY: counter_command(content.KEY)}
    lock = lock
    order = 105


BUILDING = CreamRoom()

from dataclasses import replace

from ....town_buildings.counter import counter_command
from ....town_buildings import Building
from . import content


def lazy(name:str):
    def handler(player, offer, price, rng):
        from . import rules
        return getattr(rules, name)(player, offer, price, rng)
    return handler


class CarryingHouse(Building):
    key = content.KEY
    title = content.TITLE
    blurb = content.BLURB
    owner = content.OWNER
    place = content.PLACE
    closed = content.CLOSED
    cut = content.CUT
    jobs = content.JOBS
    session_lines = content.SESSION_LINES
    counter = replace(content.SPECIAL, handlers={"ride": lazy("ride"),
                                                 "hire": lazy("hire")})
    icon = "🧺"
    place_commands = (content.KEY,)
    commands = {content.KEY: counter_command(content.KEY)}
    order = 106


BUILDING = CarryingHouse()

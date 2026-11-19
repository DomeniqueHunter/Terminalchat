from dataclasses import replace

from ....town_buildings.counter import counter_command
from ....town_buildings import Building
from . import content


def lazy(name:str):
    def handler(player, offer, price, rng):
        from . import rules
        return getattr(rules, name)(player, offer, price, rng)
    return handler


class SnowRing(Building):
    key = content.KEY
    title = content.TITLE
    blurb = content.BLURB
    owner = content.OWNER
    place = content.PLACE
    closed = content.CLOSED
    cut = content.CUT
    jobs = content.JOBS
    session_lines = content.SESSION_LINES
    counter = replace(content.SPECIAL, handlers={"bet": lazy("bet"),
                                              "fight": lazy("fight")})
    icon = "🥊"
    place_commands = (content.KEY,)
    commands = {content.KEY: counter_command(content.KEY)}
    order = 103


BUILDING = SnowRing()

from dataclasses import replace

from ....town_buildings.counter import counter_command
from ....town_buildings import Building
from . import content


def lazy(name:str):
    def starter(services, player, offer):
        from . import rules
        return getattr(rules, name)(services, player, offer)
    return starter


def bath(player, offer, price, rng):
    from .rules import bath as run
    return run(player, offer, price, rng)


def lock(services, player, command):
    from .rules import lock as run
    return run(services, player, command)


class SoleHall(Building):
    key = content.KEY
    title = content.TITLE
    blurb = content.BLURB
    owner = content.OWNER
    place = content.PLACE
    closed = content.CLOSED
    counter = replace(
        content.SPECIAL, handlers={"bath": bath},
        starters={name: lazy(name) for name in ("sign", "serve", "free")})
    icon = "🦶"
    place_commands = (content.KEY,)
    commands = {content.KEY: counter_command(content.KEY)}
    lock = lock
    order = 104


BUILDING = SoleHall()

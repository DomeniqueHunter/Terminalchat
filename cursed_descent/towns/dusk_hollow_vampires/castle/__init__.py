from dataclasses import replace

from ....town_buildings.counter import counter_command
from ....town_buildings import Building
from . import content


HANDLERS = ('audience', 'banquet', 'gate')


def offer_self(services, player, offer):
    from .slaves import offer_self as run
    return run(services, player, offer)


def lazy(name:str):
    def handler(player, offer, price, rng):
        from . import rules
        return getattr(rules, name)(player, offer, price, rng)
    return handler


def kept_starter(name:str):
    def starter(services, player, offer):
        from . import kept
        return getattr(kept, name)(services, player, offer)
    return starter


def lock(services, player, command):
    from .kept import lock as run
    return run(services, player, command)


def setup(services):
    from .slaves import alive_residents
    alive_residents(services)


def info(services, player):
    from .kept import status_line
    from .slaves import household_lines
    lines = household_lines(services, player)
    kept = status_line(services, player)
    return (*lines, kept) if kept else lines


class Castle(Building):
    decency = 2
    key = content.KEY
    title = content.TITLE
    blurb = content.BLURB
    counter = replace(
        content.SPECIAL, handlers={name: lazy(name) for name in HANDLERS},
        starters={"offer_self": offer_self,
                  "kept_contract": kept_starter("sign"),
                  "kept_serve": kept_starter("serve"),
                  "kept_free": kept_starter("free")})
    icon = "🏰"
    place_commands = (content.KEY,)
    commands = {content.KEY: counter_command(content.KEY)}
    order = 90
    setup = setup
    lock = lock
    info = info


BUILDING = Castle()

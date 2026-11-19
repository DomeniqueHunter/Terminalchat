from dataclasses import replace

from ....town_buildings.counter import counter_command
from ....town_buildings import Building
from . import content


HANDLERS = ('guest', 'serve', 'bite', 'gossip', 'present')


def lazy(name:str):
    def handler(player, offer, price, rng):
        from . import rules
        return getattr(rules, name)(player, offer, price, rng)
    return handler


class Salon(Building):
    key = content.KEY
    title = content.TITLE
    blurb = content.BLURB
    counter = replace(
        content.SPECIAL, handlers={name: lazy(name) for name in HANDLERS})
    icon = "🥂"
    place_commands = (content.KEY,)
    commands = {content.KEY: counter_command(content.KEY)}
    order = 85


BUILDING = Salon()

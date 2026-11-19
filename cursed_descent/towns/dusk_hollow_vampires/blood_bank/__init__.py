from dataclasses import replace

from ....town_buildings.counter import counter_command
from ....town_buildings import Building
from . import content


HANDLERS = ('vial', 'talk')


def donate_today(services, player, offer):
    from .rules import donate_today as run
    return run(services, player, offer)


def lazy(name:str):
    def handler(player, offer, price, rng):
        from . import rules
        return getattr(rules, name)(player, offer, price, rng)
    return handler


class BloodBank(Building):
    key = content.KEY
    title = content.TITLE
    blurb = content.BLURB
    counter = replace(
        content.SPECIAL, handlers={name: lazy(name) for name in HANDLERS},
        starters={"donate": donate_today})
    icon = "🩸"
    place_commands = (content.KEY,)
    commands = {content.KEY: counter_command(content.KEY)}
    order = 80


BUILDING = BloodBank()

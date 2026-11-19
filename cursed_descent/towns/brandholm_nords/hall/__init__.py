from dataclasses import replace

from ....town_buildings.counter import counter_command
from ....town_buildings import Building
from . import content


def lazy(name:str):
    def starter(services, player, offer):
        from . import rules
        return getattr(rules, name)(services, player, offer)
    return starter


class Hall(Building):
    decency = 1
    key = content.KEY
    title = content.TITLE
    blurb = content.BLURB
    owner = content.OWNER
    place = content.PLACE
    closed = content.CLOSED
    icon = "🔥"
    counter = replace(content.SPECIAL, starters={
        "audience": lazy("audience"), "book": lazy("book"),
        "favour": lazy("favour")})
    place_commands = (content.KEY,)
    commands = {content.KEY: counter_command(content.KEY)}
    order = 20
    greeting = content.GREETING


BUILDING = Hall()

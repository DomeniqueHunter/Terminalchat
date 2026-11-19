from dataclasses import replace

from ....town_buildings.counter import counter_command
from ....town_buildings import Building
from . import content
from .rules import bet


class Arena(Building):
    decency = 0
    key = content.KEY
    title = content.TITLE
    blurb = content.BLURB
    counter = replace(content.SPECIAL, handlers={"bet": bet})
    icon = "🥊"
    place_commands = (content.KEY,)
    commands = {content.KEY: counter_command(content.KEY)}
    order = 85


BUILDING = Arena()

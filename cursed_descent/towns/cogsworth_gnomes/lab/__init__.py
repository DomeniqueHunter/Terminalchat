from dataclasses import replace

from ....town_buildings.counter import counter_command
from ....town_buildings import Building
from . import content
from .rules import experiment


class Lab(Building):
    key = content.KEY
    title = content.TITLE
    blurb = content.BLURB
    counter = replace(content.SPECIAL, handlers={"experiment": experiment})
    icon = "⚗"
    place_commands = (content.KEY,)
    commands = {content.KEY: counter_command(content.KEY)}
    order = 85


BUILDING = Lab()

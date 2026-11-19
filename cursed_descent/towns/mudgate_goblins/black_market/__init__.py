from ....town_buildings.counter import counter_command
from ....town_buildings import Building
from . import content


class BlackMarket(Building):
    decency = 0
    key = content.KEY
    title = content.TITLE
    blurb = content.BLURB
    counter = content.SPECIAL
    icon = "🕶"
    place_commands = (content.KEY,)
    commands = {content.KEY: counter_command(content.KEY)}
    order = 80


BUILDING = BlackMarket()

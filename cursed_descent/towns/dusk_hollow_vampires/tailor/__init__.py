from ....town_buildings import Building
from ....town_buildings.counter import counter_command
from . import content


def ui(services, player):
    from .ui import panel
    return panel(services, player)


class Tailor(Building):
    ui = ui

    decency = 0
    key = content.KEY
    title = content.TITLE
    blurb = content.BLURB
    counter = content.SPECIAL
    icon = "🧵"
    place_commands = (content.KEY,)
    commands = {content.KEY: counter_command(content.KEY)}
    order = 60
    greeting = ("Mistress Delphine Rook looks you up and down. 'Stand still. "
                "I measure twice and I judge once.' The wares are on the "
                "counter.")


BUILDING = Tailor()

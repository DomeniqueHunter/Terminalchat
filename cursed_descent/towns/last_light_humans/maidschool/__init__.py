from ....town_buildings import Building
from . import content
from .building import COMMANDS


def ui(services, player):
    from .ui import panel
    return panel(services, player)


def setup(services) -> None:
    from .school import SchoolLedger
    services.school = SchoolLedger(services.data_path)


def save(services) -> None:
    services.school.save()


class Maidschool(Building):
    key = "maidschool"
    greeting = content.OFFER
    icon = "🎓"
    commands = COMMANDS
    place_commands = ("maidschool",)
    ui = ui
    setup = setup
    save = save
    help = content.HELP
    title = "Maid School"
    blurb = "Headmistress Brunhild trains maids – and adventurers."
    order = 80


BUILDING = Maidschool()

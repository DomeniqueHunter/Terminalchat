from ....config import CAFE_CUT
from ....town_buildings import Building
from . import content
from .building import COMMANDS


def ui(services, player):
    from .ui import panel
    return panel(services, player)


def setup(services) -> None:
    from .ledger import CafeLedger
    services.cafe = CafeLedger(services.data_path)
    services.stools = []
    services.rides = {}
    services.complaints = {}
    services.claims = {}
    services.cafe_seen = {}
    services.ambient_due = {}


def save(services) -> None:
    services.cafe.save()


class Cafe(Building):
    decency = 0
    reaction = "cafe"
    key = "cafe"
    owner = content.OWNER
    place = content.PLACE
    closed = content.CLOSED
    cut = CAFE_CUT
    greeting = content.OFFER
    icon = "🍰"
    commands = COMMANDS
    place_commands = ("cafe",)
    ui = ui
    setup = setup
    save = save
    help = content.HELP
    title = "Café"
    blurb = "Madame Bertha serves cake to ladies. Men are furniture."
    session_lines = content.SESSION_LINES
    order = 90


BUILDING = Cafe()

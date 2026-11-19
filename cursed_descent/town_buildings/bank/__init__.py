from ..base import Building
from . import content
from .building import COMMANDS


def ui(services, player):
    from .ui import panel
    return panel(services, player)


def setup(services) -> None:
    from .ledger import Bank as Ledger
    services.bank = Ledger(services.data_path)


def save(services) -> None:
    services.bank.save()


class Bank(Building):
    key = "bank"
    greeting = content.OFFER
    icon = "🏦"
    commands = COMMANDS
    place_commands = ("bank", "deposit", "withdraw")
    ui = ui
    setup = setup
    save = save
    help = content.HELP
    title = "Bank"
    label = "Bank"
    blurb = "Gold and items stay safe here, whatever happens below."
    order = 50

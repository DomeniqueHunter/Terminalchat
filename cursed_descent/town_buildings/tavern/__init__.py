from ..base import Building
from . import content
from .building import COMMANDS


def ui(services, player):
    from .ui import panel
    return panel(services, player)


class Tavern(Building):
    decency = 2
    key = "tavern"
    owner = content.OWNER
    place = content.PLACE
    closed = content.CLOSED
    cut = content.TAVERN_CUT
    greeting = content.GREETING
    icon = "🍺"
    jobs = content.JOBS
    menu = content.MENU
    menu_title = content.MENU_TITLE
    dish_kg = content.DISH_KG
    commands = COMMANDS
    place_commands = ("tavern", "room", "sellpods")
    ui = ui
    title = "Tavern"
    label = "Tavern"
    blurb = "The Gilded Tankard: ale, noise and honest work."
    job_words = {"barrel": "milk", "dance": "dancer"}
    help = content.HELP
    order = 60

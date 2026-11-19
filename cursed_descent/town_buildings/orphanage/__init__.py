from ..base import Building
from . import content


def do_orphanage(services, player, args):
    from ...models import Message
    return [Message(content.HELP, player.name)]


def do_donate(services, player, args):
    from .rules import donate
    return donate(services, player, args)


def ui(services, player):
    from .ui import panel
    return panel(services, player)


class Orphanage(Building):
    key = content.KEY
    title = content.TITLE
    label = "Orphanage"
    blurb = content.BLURB
    greeting = content.OFFER
    icon = "🏮"
    commands = {content.KEY: do_orphanage, "donate": do_donate}
    place_commands = (content.KEY, "donate")
    ui = ui
    help = content.HELP
    order = 95

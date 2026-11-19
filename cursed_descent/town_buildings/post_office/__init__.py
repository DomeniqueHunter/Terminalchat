from ..base import Building
from . import content


def do_post_office(services, player, args):
    from .rules import do_post_office as run
    return run(services, player, args)


def do_mail(services, player, args):
    from .rules import do_mail as run
    return run(services, player, args)


def ui(services, player):
    from .ui import panel
    return panel(services, player)


def setup(services) -> None:
    from ...mail import MailLedger
    services.mail = MailLedger(services.data_path)


def save(services) -> None:
    services.mail.save()


class PostOffice(Building):
    key = content.KEY
    title = content.TITLE
    label = "Post Office"
    blurb = content.BLURB
    greeting = content.OFFER
    icon = "📮"
    commands = {content.KEY: do_post_office, "mail": do_mail}
    place_commands = (content.KEY,)
    ui = ui
    setup = setup
    save = save
    help = content.HELP
    order = 200

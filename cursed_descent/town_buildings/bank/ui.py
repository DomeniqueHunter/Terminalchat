from ...models import Player
from ...view import Panel
from ...web.stash import summary_panel


def panel(services, player:Player) -> Panel:
    return summary_panel("🏦 Bank", services.bank.account(player), "bank")

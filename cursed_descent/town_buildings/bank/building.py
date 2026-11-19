from ...models import Message


def do_bank(services, player, args):
    from .ledger import CLOSED, bank_menu
    if services.in_run(player):
        return [Message(CLOSED, player.name)]
    return bank_menu(player, services.bank.account(player))


def do_deposit(services, player, args):
    from .ledger import bank_move
    return bank_move(player, services.bank.account(player), args, True,
                     services.in_run(player))


def do_withdraw(services, player, args):
    from .ledger import bank_move
    return bank_move(player, services.bank.account(player), args, False,
                     services.in_run(player))


COMMANDS = {"bank": do_bank, "deposit": do_deposit,
            "withdraw": do_withdraw}

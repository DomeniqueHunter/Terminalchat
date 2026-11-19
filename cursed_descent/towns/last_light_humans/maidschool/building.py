import random
import time

from ....config import COMPANION_NAME
from ....models import Message
from .content import HANDOVER
from .search import look, next_maid, previous_maid, recruit
from .school import (
    CLOSED as SCHOOL_CLOSED, buy_back, buyback_price, enroll_warning,
    make_maid, school,
)


SEARCH_STEPS = {"look": look, "next": next_maid, "prev": previous_maid,
                "recruit": recruit}


def do_maidschool(services, player, args):
    if services.in_run(player):
        return [Message(SCHOOL_CLOSED, player.name)]
    sub = args[0].casefold() if args else ""
    if sub == "handover":
        return handover(services, player)
    if sub == "enroll":
        return enroll(services, player, args[1:])
    if sub == "buyback":
        return buyback(services, player, " ".join(args[1:]))
    if sub in SEARCH_STEPS:
        return SEARCH_STEPS[sub](services, player)
    messages = school(player, services.school.record(player), args, False)
    graduates = services.graduates()
    if sub in ("", "list") and graduates:
        lines = ["Graduates (buy back with [maidschool buyback "
                 "<name>]):"] + [
            f"  {grad.full_name} (Lv {grad.level}, "
            f"{buyback_price(grad)} gold)" for grad in graduates]
        messages.append(Message("\n".join(lines), player.name))
    return messages


def handover(services, player):
    session = services.session
    connie = session.member(COMPANION_NAME)
    if connie is None or session.member(player.name) is None:
        return [Message("Connie is not with your party.", player.name)]
    session.party.remove(connie)
    session.manual.discard(connie.name)
    session.autopilot.discard(connie.name)
    services.repository.release(connie)
    session.buster_ledger.bump("handed_over")
    return [Message(random.choice(HANDOVER).format(
        name=connie.name, giver=player.name), player.name)]


ARM_SECONDS = 30.0


def armed(services, name:str) -> bool:
    since = services.enroll_armed.get(name)
    if since is None or time.time() - since > ARM_SECONDS:
        services.enroll_armed.pop(name, None)
        return False
    return True


def enroll(services, player, args):
    if player.npc:
        return [Message("Only adventurers can enroll.", player.name)]
    if services.session.member(player.name) is not None:
        return [Message("Leave the lobby and party first.",
                        player.name)]
    if not args or args[0].casefold() != "confirm":
        services.enroll_armed[player.name] = time.time()
        return [enroll_warning(player)]
    if not armed(services, player.name):
        return [Message(f"Brunhild waits a moment too long. Start the "
                        f"enrolment again; the confirmation is valid for "
                        f"{int(ARM_SECONDS)} seconds.", player.name)]
    services.enroll_armed.pop(player.name, None)
    services.repository.bury(player, "maid: enrolled in the school")
    services.repository.path(player.name).unlink(missing_ok=True)
    make_maid(player)
    return [Message(f"Brunhild cuts the old life away with a single "
                    f"nod. {player.full_name} is now a maid of the "
                    f"school.", player.name)]


def buyback(services, buyer, text):
    graduate = services.repository.load(services.repository.resolve(text))
    if graduate is None or graduate.npc != "maid":
        return [Message("No such graduate. See [maidschool].",
                        buyer.name)]
    messages = buy_back(buyer, graduate)
    if not graduate.npc:
        services.repository.npc_path(graduate.name).unlink(missing_ok=True)
        services.repository.save(graduate)
    return messages


COMMANDS = {"maidschool": do_maidschool}

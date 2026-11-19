import random

from ..body import BUILDS
from ..config import GENDERS
from ..controller import GameController
from ..models import Message


STAT_PRESETS = ("5 1 4 0", "0 1 3 6", "0 2 3 5", "3 5 2 0", "3 2 3 2")
POOL = ("Lyra", "Kai", "Mira", "Brom", "Sel", "Tova", "Rook", "Ivy")
ACTIVE = ("combat", "chest", "remains", "event")
AUTO_RUN_LIMIT = 200
STATE_COMMANDS = {"combat": "!force", "chest": "!open", "remains": "!loot"}


def create_player(controller:GameController, name:str, gender:str,
                  stats:str, body:str="rest") -> list[Message]:
    messages: list[Message] = []
    for answer in ("!create", "ok", gender, "human", body, "ok", stats,
                   "yes"):
        messages += controller.handle(name, answer)
    return messages


def random_party(controller:GameController) -> list[Message]:
    existing = {name.casefold() for name in controller.repository.names()}
    fresh = [name for name in POOL if name.casefold() not in existing]
    messages: list[Message] = []
    for name in fresh[:4]:
        body = (f"build {random.choice(BUILDS)} "
                f"height {random.randint(135, 215)} "
                f"weight {random.randint(40, 130)} "
                f"bust {random.randint(0, 900)}")
        messages += create_player(controller, name, random.choice(GENDERS),
                                  random.choice(STAT_PRESETS), body)
    return messages


def quick_start(controller:GameController) -> list[Message]:
    players = sorted(controller.repository.names(), key=str.casefold)[:4]
    if not players:
        return [Message("Create players first.")]
    messages = controller.handle(players[0], "!lobby")
    for name in players[1:]:
        messages += controller.handle(name, "!join")
    messages += controller.handle(players[0], "!start")
    for name in sorted(controller.ready.pending):
        messages += controller.handle(name, "!ready")
    return messages


def everyone_hits(controller:GameController) -> list[Message]:
    session = controller.session
    if session.state != "combat":
        return [Message("No fight running.")]
    round_no = session.round_no
    messages: list[Message] = []
    for player in list(session.living()):
        if session.state != "combat" or session.round_no != round_no:
            break
        messages += controller.handle(player.name, "!hit")
    return messages


def auto_run(controller:GameController) -> list[Message]:
    session = controller.session
    if session.state not in ACTIVE:
        return [Message("Start a run first (Quick start).")]
    messages: list[Message] = []
    for _ in range(AUTO_RUN_LIMIT):
        if session.state not in ACTIVE:
            break
        sender = random.choice(session.living()).name
        if session.state == "event":
            text = f"!{random.choice(session.available_commands())}"
        else:
            text = STATE_COMMANDS[session.state]
        messages += controller.handle(sender, text)
    return messages


TOOLS = {"random_party": random_party, "quick_start": quick_start,
         "everyone_hits": everyone_hits, "auto_run": auto_run}

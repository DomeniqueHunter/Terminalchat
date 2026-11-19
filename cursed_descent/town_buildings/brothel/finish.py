import random
import time

from ...config import (
    BROTHEL_CUT, BROTHEL_DOM_FINISH, BROTHEL_WIPE_FACTOR, HOUSE_KO_SECONDS,
)
from ...models import Message, Player
from ..work.jobs import Shift, finish, session_pay
from .finish_content import (
    DOM_VORE, DOM_WIPE, LOOT, VORE, WIPE, WIPE_AFTER,
)
from .clients import client_can
from .practices import can_do


FINISHERS = {"swallow": "facesitting", "wipe": "foot"}
DOM_ACTS = ("facesitting", "foot")


def credit(player:Player, shift:Shift, pay:int) -> None:
    shift.earned += pay
    shift.served += 1
    if shift.endless:
        player.gold += pay - round(pay * BROTHEL_CUT)
    else:
        shift.left -= 1


def problem(player:Player, shift:Shift, word:str) -> str:
    act = FINISHERS[word]
    client = shift.client
    if shift.mode == "sub":
        return "You receive in this shift. Only the one who gives can do this."
    if client.player:
        return f"{client.name} is not yours to keep."
    if not can_do(player.gender, act, "give", player.body):
        return f"You cannot do {act} give with your body."
    if not client_can(client, act, "give"):
        return f"{client.name} cannot take the other side of {act}."
    return ""


def finish_client(player:Player, shift:Shift, word:str, rng:random.Random,
                  regulars) -> tuple[list[Message], int]:
    client = shift.client
    words = {"client": client.name}
    if regulars is not None:
        regulars.forget("brothel", client.name)
    if word == "swallow":
        pay = client.purse
        lines = [rng.choice(VORE).format(**words),
                 LOOT.format(client=client.name, gold=pay)]
    else:
        pay = round(session_pay(player, shift.job, rng) * BROTHEL_WIPE_FACTOR)
        lines = [rng.choice(WIPE).format(**words),
                 WIPE_AFTER.format(client=client.name), f"+{pay} gold"]
    credit(player, shift, pay)
    return [Message("\n".join(lines), player.name)], pay


def dom_finish(player:Player, shift:Shift, act:str, rng:random.Random,
               shifts:dict[str, Shift]) -> list[Message] | None:
    client = shift.client
    if (act not in DOM_ACTS or not (client.dominant or client.dominated)
            or rng.random() >= BROTHEL_DOM_FINISH):
        return None
    taken = shift.earned
    if shift.endless:
        player.gold = max(0, player.gold - (
            taken - round(taken * BROTHEL_CUT)))
    shift.earned = 0
    player.profile["ko_until"] = time.time() + HOUSE_KO_SECONDS
    pool = DOM_VORE if act == "facesitting" else DOM_WIPE
    text = rng.choice(pool).format(client=client.name)
    del shifts[player.name]
    return [Message(f"{text}\nEverything you earned this shift stays with "
                    f"{client.name}: -{taken} gold.", player.name)] + finish(
        player, shift)

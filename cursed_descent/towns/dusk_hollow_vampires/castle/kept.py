import random
from typing import Any

from ....formulas import apply_buff
from ....locations.common import pronouns
from ....models import Message, Player
from .content import INVITE_KEY
from .kept_content import (
    ALREADY, BLOCKED, BOUGHT_OUT, CANNOT_PAY, FINISHED, FREE_PRICE,
    GLOW_BUFF, HOURS, IN_RUN, KEPT_BLOCK, KEY, MASTERS, MAX_SERVES, NOT_KEPT,
    PAY, SERVE, SERVE_GOLD, SERVE_LIMIT, SERVE_PAY, SIGNED, STATUS,
)


def values(player:Player, state:dict, **extra) -> dict:
    they, them, their = pronouns(player.gender)
    master = MASTERS[state["master"]]
    return {"name": player.name, "they": they, "them": them,
            "their": their, "title": master.title, "master": master.name,
            **extra}


def left_text(state:dict, now:float) -> str:
    minutes = max(0, round((state["until"] - now) / 60))
    return f"{minutes // 60} h {minutes % 60:02d} min"


def state_of(player:Player) -> dict | None:
    return player.profile.get(KEY) or None


def finish(services:Any, player:Player) -> list[Message]:
    state = player.profile.pop(KEY)
    player.gold += PAY
    if GLOW_BUFF not in player.buffs:
        apply_buff(player, GLOW_BUFF)
    services.repository.save(player)
    return [Message(FINISHED.format(**values(player, state, pay=PAY)),
                    player.name)]


def settle(services:Any, player:Player) -> list[Message]:
    state = state_of(player)
    if state is None or services.now < state["until"]:
        return []
    return finish(services, player)


def sign(services:Any, player:Player, offer:Any) -> list[Message]:
    from .rules import locked
    if not player.profile.get(INVITE_KEY):
        return [Message(line, player.name)
                for line in locked(player, services.rng)]
    if services.in_run(player):
        return [Message(IN_RUN, player.name)]
    settled = settle(services, player)
    state = state_of(player)
    if state is not None:
        return settled + [Message(ALREADY.format(**values(
            player, state, left=left_text(state, services.now))),
            player.name)]
    state = {"master": offer.item, "until": services.now + HOURS * 3600,
             "serves": 0}
    player.profile[KEY] = state
    services.repository.save(player)
    master = MASTERS[offer.item]
    text = f"{master.sign}\n" + services.rng.choice(SIGNED).format(
        **values(player, state, hours=HOURS))
    return settled + [Message(text, player.name)]


def serve(services:Any, player:Player, offer:Any) -> list[Message]:
    settled = settle(services, player)
    state = state_of(player)
    if state is None:
        return settled + [Message(NOT_KEPT, player.name)]
    if state["serves"] >= MAX_SERVES:
        return [Message(SERVE_LIMIT.format(**values(player, state)),
                        player.name)]
    rng: random.Random = services.rng
    gold = rng.randint(*SERVE_GOLD)
    state["serves"] += 1
    player.gold += gold
    services.repository.save(player)
    master = MASTERS[state["master"]]
    text = "\n".join((
        master.serve.format(**values(player, state)),
        rng.choice(SERVE).format(**values(player, state)),
        SERVE_PAY.format(gold=gold, count=state["serves"],
                         limit=MAX_SERVES)))
    return [Message(text, player.name)]


def free(services:Any, player:Player, offer:Any) -> list[Message]:
    settled = settle(services, player)
    state = state_of(player)
    if state is None:
        return settled + [Message(NOT_KEPT, player.name)]
    if player.gold < FREE_PRICE:
        return [Message(CANNOT_PAY.format(**values(
            player, state, price=FREE_PRICE)), player.name)]
    player.gold -= FREE_PRICE
    player.profile.pop(KEY)
    services.repository.save(player)
    return [Message(BOUGHT_OUT.format(**values(
        player, state, price=FREE_PRICE)), player.name)]


def lock(services:Any, player:Player, command:str) -> list[Message]:
    if command not in BLOCKED:
        return []
    settled = settle(services, player)
    state = state_of(player)
    if state is None:
        return settled
    return [Message(KEPT_BLOCK.format(**values(
        player, state, left=left_text(state, services.now))), player.name)]


def status_line(services:Any, player:Player) -> str:
    state = state_of(player)
    if state is None:
        return ""
    return STATUS.format(**values(
        player, state, left=left_text(state, services.now),
        serves=state["serves"], limit=MAX_SERVES))

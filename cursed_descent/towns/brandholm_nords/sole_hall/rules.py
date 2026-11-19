import random

from ....formulas import apply_buff, max_hp
from ....models import Message, Player
from .content import (
    ALREADY, BATH, BLOCK, BLOCKED, BOUGHT_OUT, CANNOT_PAY, FINISHED,
    FREE_PRICE, GLOW, HOURS, IN_RUN, LIMIT, MAX_SERVES, NOT_SIGNED, PAY,
    REST, SERVE, SERVE_GOLD, SERVE_PAY, SIGNED, STATE_KEY,
    BATH_HEAL,
)


def left_text(state:dict, now:float) -> str:
    minutes = max(0, round((state["until"] - now) / 60))
    return f"{minutes // 60} h {minutes % 60:02d} min"


def state_of(player:Player) -> dict | None:
    return player.profile.get(STATE_KEY) or None


def settle(services, player:Player) -> list[Message]:
    state = state_of(player)
    if state is None or services.now < state["until"]:
        return []
    player.profile.pop(STATE_KEY)
    player.gold += PAY
    if GLOW not in player.buffs:
        apply_buff(player, GLOW)
    services.repository.save(player)
    return [Message(FINISHED.format(pay=PAY), player.name)]


def sign(services, player:Player, offer) -> list[Message]:
    if services.in_run(player):
        return [Message(IN_RUN, player.name)]
    settled = settle(services, player)
    state = state_of(player)
    if state is not None:
        return settled + [Message(ALREADY.format(
            left=left_text(state, services.now)), player.name)]
    player.profile[STATE_KEY] = {"until": services.now + HOURS * 3600,
                                 "serves": 0}
    services.repository.save(player)
    return settled + [Message(services.rng.choice(SIGNED), player.name)]


def serve(services, player:Player, offer) -> list[Message]:
    settled = settle(services, player)
    state = state_of(player)
    if state is None:
        return settled + [Message(NOT_SIGNED, player.name)]
    if state["serves"] >= MAX_SERVES:
        return [Message(LIMIT, player.name)]
    rng: random.Random = services.rng
    gold = rng.randint(*SERVE_GOLD)
    state["serves"] += 1
    player.gold += gold
    services.repository.save(player)
    return [Message("\n".join((
        rng.choice(SERVE),
        SERVE_PAY.format(gold=gold, count=state["serves"],
                         limit=MAX_SERVES))), player.name)]


def free(services, player:Player, offer) -> list[Message]:
    settled = settle(services, player)
    if state_of(player) is None:
        return settled + [Message(NOT_SIGNED, player.name)]
    if player.gold < FREE_PRICE:
        return [Message(CANNOT_PAY.format(price=FREE_PRICE), player.name)]
    player.gold -= FREE_PRICE
    player.profile.pop(STATE_KEY)
    services.repository.save(player)
    return [Message(BOUGHT_OUT.format(price=FREE_PRICE), player.name)]


def bath(player:Player, offer, price:int, rng:random.Random) -> list[str]:
    player.hp = min(max_hp(player),
                    player.hp + round(max_hp(player) * BATH_HEAL))
    if REST not in player.buffs:
        apply_buff(player, REST)
    return [BATH]


def lock(services, player:Player, command:str) -> list[Message]:
    settled = settle(services, player)
    if settled:
        return settled
    if command not in BLOCKED:
        return []
    state = state_of(player)
    if state is None:
        return settled
    return [Message(BLOCK.format(left=left_text(state, services.now)),
                    player.name)]

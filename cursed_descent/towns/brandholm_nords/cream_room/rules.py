import random

from ....formulas import apply_buff
from ....intimacy import fertility
from ....locations.common import pronouns
from ....models import Message, Player
from .content import (
    ALREADY, BABY, BLESS_CHANCE, BLESS_KEY, BLOCK, BLOCKED, FEE, FILL,
    FILL_KEY, FILL_MAX, FILL_PRICE, FINISHED, FULL_AT, FULL_FLAG,
    FULL_TEXT, HOURS, IN_RUN, NOT_FULL, SIGNED,
)


def left_text(state:dict, now:float) -> str:
    minutes = max(0, round((state["until"] - now) / 60))
    return f"{minutes // 60} h {minutes % 60:02d} min"


def level(services, player:Player) -> int:
    state = player.profile.get(FILL_KEY)
    if not state:
        return 0
    passed = max(0, services.world.day - state["day"])
    state["level"] = max(0, state["level"] - passed)
    state["day"] = services.world.day
    if state["level"] < FULL_AT:
        player.profile.pop(FULL_FLAG, None)
    return state["level"]


def settle(services, player:Player) -> list[Message]:
    state = player.profile.get(BLESS_KEY)
    if not state or services.now < state["until"]:
        return []
    player.profile.pop(BLESS_KEY)
    fee = min(FEE, player.gold)
    player.gold -= fee
    for buff in ("ember_blessed",):
        if buff not in player.buffs:
            apply_buff(player, buff)
    services.repository.save(player)
    return [Message(FINISHED.format(fee=fee), player.name)]


def fill(services, player:Player, offer) -> list[Message]:
    if player.gold < FILL_PRICE:
        return [Message(f"That costs {FILL_PRICE} gold.", player.name)]
    player.gold -= FILL_PRICE
    current = level(services, player)
    state = {"level": min(FILL_MAX, current + 1), "day": services.world.day}
    player.profile[FILL_KEY] = state
    lines = [services.rng.choice(FILL)]
    if "filled" not in player.buffs:
        apply_buff(player, "filled")
    if state["level"] >= FULL_AT:
        player.profile[FULL_FLAG] = True
        lines.append(FULL_TEXT)
    lines.append(f"💰 Gold: {player.gold}")
    services.repository.save(player)
    return [Message("\n".join(lines), player.name)]


def bless(services, player:Player, offer) -> list[Message]:
    if services.in_run(player):
        return [Message(IN_RUN, player.name)]
    settled = settle(services, player)
    state = player.profile.get(BLESS_KEY)
    if state:
        return settled + [Message(ALREADY.format(
            left=left_text(state, services.now)), player.name)]
    if level(services, player) < FULL_AT:
        return settled + [Message(NOT_FULL, player.name)]
    player.profile[BLESS_KEY] = {"until": services.now + HOURS * 3600}
    player.profile.pop(FILL_KEY, None)
    player.profile.pop(FULL_FLAG, None)
    lines = [SIGNED]
    rng: random.Random = services.rng
    if rng.random() < BLESS_CHANCE * fertility(player):
        player.pregnant = "party"
        player.profile["pregnant_by"] = "Sigrunn Brandsdottir"
        player.profile["pregnant_by_id"] = ""
        lines.append(f"👶 {BABY}")
    services.repository.save(player)
    return settled + [Message("\n".join(lines), player.name)]


def lock(services, player:Player, command:str) -> list[Message]:
    settled = settle(services, player)
    if settled:
        return settled
    if command not in BLOCKED:
        return []
    state = player.profile.get(BLESS_KEY)
    if not state:
        return settled
    return [Message(BLOCK.format(left=left_text(state, services.now)),
                    player.name)]

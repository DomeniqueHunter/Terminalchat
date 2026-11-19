import random

from ....formulas import apply_buff, max_hp
from .content import (
    BET_CHANCE, BET_LOSE, BET_WIN, FIGHT_BASE, FIGHT_LOSE, FIGHT_MAX,
    FIGHT_PAY, FIGHT_PER_STRENGTH, FIGHT_WIN, FIGHT_LOSS,
)


def bet(player, offer, price:int, rng:random.Random) -> list[str]:
    if rng.random() < BET_CHANCE:
        player.gold += price * 2
        return [BET_WIN.format(name=player.name, pay=price * 2)]
    return [BET_LOSE.format(price=price)]


def fight(player, offer, price:int, rng:random.Random) -> list[str]:
    chance = min(FIGHT_MAX, FIGHT_BASE + FIGHT_PER_STRENGTH * (
        player.stats.get("strength", 0)))
    if rng.random() < chance:
        player.gold += FIGHT_PAY
        if "ring_victor" not in player.buffs:
            apply_buff(player, "ring_victor")
        return [FIGHT_WIN.format(pay=FIGHT_PAY)]
    loss = min(player.hp - 1, max(1, round(max_hp(player) * FIGHT_LOSS)))
    player.hp -= max(0, loss)
    return [FIGHT_LOSE.format(loss=loss)]

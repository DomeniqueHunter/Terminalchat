import random

from ....formulas import apply_buff, max_hp
from .content import HIRE, HIRE_COST, HIRE_PAY, RIDE, RIDE_HEAL


def ride(player, offer, price:int, rng:random.Random) -> list[str]:
    gain = round(max_hp(player) * RIDE_HEAL)
    player.hp = min(max_hp(player), player.hp + gain)
    if "carried" not in player.buffs:
        apply_buff(player, "carried")
    return [rng.choice(RIDE), f"❤ +{gain} HP."]


def hire(player, offer, price:int, rng:random.Random) -> list[str]:
    loss = min(player.hp - 1, max(1, round(max_hp(player) * HIRE_COST)))
    player.hp -= max(0, loss)
    player.gold += HIRE_PAY
    return [rng.choice(HIRE), f"💰 +{HIRE_PAY} gold. ❤ −{loss} HP."]

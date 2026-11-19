import random

from .content import BET_WIN_CHANCE


def bet(player, offer, price:int, rng:random.Random) -> list[str]:
    if rng.random() < BET_WIN_CHANCE:
        player.gold += price * 2
        return [f"The red corner wins! {player.name} collects "
                f"{price * 2} gold."]
    return [f"The red corner goes down. {price} gold lost."]

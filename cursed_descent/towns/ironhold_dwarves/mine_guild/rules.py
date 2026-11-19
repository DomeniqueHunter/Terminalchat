import random

from .content import HURT_ROUND, HURT_SHARE


def round_hook(player, shift, rng:random.Random) -> list[str]:
    from ....town_buildings.offers import hurt
    if rng.random() >= HURT_ROUND:
        return []
    return [f"   ✦ A rock slides loose: -{hurt(player, HURT_SHARE)} HP."]

import random

from .content import EXPERIMENT_EXP_PER_LEVEL, EXPERIMENT_HURT_SHARE


def experiment(player, offer, price:int, rng:random.Random) -> list[str]:
    from ....dungeon import give_item, grant_exp
    from ....town_buildings.offers import hurt
    roll = rng.random()
    if roll < 0.4:
        lines = ["The machine hums, sparks and leaves "
                 f"{player.name} tingling all over."]
        lines += grant_exp(player, EXPERIMENT_EXP_PER_LEVEL * player.level)
    elif roll < 0.7:
        lines = ["A hatch pops open and spits out a gift.",
                 give_item(player, "potion_large")]
    elif roll < 0.9:
        lines = ["Smoke, a bang and a puff of soot. Nothing "
                 "happens, apart from the soot."]
    else:
        lines = [f"A valve bursts: -"
                 f"{hurt(player, EXPERIMENT_HURT_SHARE)} HP. The "
                 f"gnomes take notes."]
        lines += grant_exp(player, EXPERIMENT_EXP_PER_LEVEL)
    return lines

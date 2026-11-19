import random

from ....formulas import apply_buff, max_hp
from ....locations.common import pronouns
from ....models import Player
from .content import (
    AGAIN, DATA_KEY, DAY_KEY, DONATE, DONATE_PAY, DONATE_SHARE, FAINT,
    FAINT_CAP, FAINT_STEP, MIN_HP_SHARE, TALK, TOO_WEAK, VIAL_HEAL, VIAL,
)


def their(player:Player) -> str:
    return pronouns(player.gender)[2]


def donate(player:Player, offer, price:int, rng:random.Random,
           day:int=0) -> list[str]:
    values = {"name": player.name, "their": their(player), "pay": DONATE_PAY}
    if player.hp < max_hp(player) * MIN_HP_SHARE:
        return [rng.choice(TOO_WEAK).format(**values)]
    again = player.profile.get(DAY_KEY) == day
    player.profile[DAY_KEY] = day
    count = player.profile.get(DATA_KEY, 0) + 1
    player.profile[DATA_KEY] = count
    player.gold += DONATE_PAY
    lines = [rng.choice(DONATE).format(**values)]
    if again:
        loss = min(player.hp - 1,
                   max(1, round(max_hp(player) * DONATE_SHARE)))
        player.hp -= loss
        lines += [rng.choice(AGAIN).format(**values), f"❤ −{loss} HP."]
    if "blood_faint" not in player.buffs:
        apply_buff(player, "blood_faint")
    chance = min(FAINT_CAP, FAINT_STEP * (count - 1)) if again else 0.0
    if rng.random() < chance:
        player.hp = 1
        lines.append(rng.choice(FAINT).format(**values))
    return lines


def vial(player:Player, offer, price:int, rng:random.Random) -> list[str]:
    values = {"name": player.name, "their": their(player)}
    heal = round(max_hp(player) * VIAL_HEAL)
    player.hp = min(max_hp(player), player.hp + heal)
    player.profile[DATA_KEY] = 0
    if "blood_vigor" not in player.buffs:
        apply_buff(player, "blood_vigor")
    return [rng.choice(VIAL).format(**values), f"❤ +{heal} HP."]


def talk(player:Player, offer, price:int, rng:random.Random) -> list[str]:
    return [rng.choice(TALK)]


def donate_today(services, player:Player, offer) -> list:
    from ....models import Message
    lines = donate(player, offer, 0, services.rng, services.world.day)
    lines.append(f"💰 Gold: {player.gold}")
    services.repository.save(player)
    return [Message("\n".join(lines), player.name)]

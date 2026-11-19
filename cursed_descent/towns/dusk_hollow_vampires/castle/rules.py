import random

from ....formulas import apply_buff, max_hp
from ....locations.common import pronouns
from ....models import Player
from .content import (
    AUDIENCE_ODDS, BANQUET_HONOR, BANQUET_MAIN, BANQUET_ODDS,
    BANQUET_SHARE, DISMISSED, FAVOR, FAVOR_GOLD, GATE_TALK, GIFT, GIFT_GOLD,
    HURT_SHARE, INVITE_KEY, LEASH, LEASH_SHARE, NO_INVITE, RINGS,
)


def values(player:Player, **extra) -> dict:
    they, them, their = pronouns(player.gender)
    return {"name": player.name, "they": they, "them": them,
            "their": their, **extra}


def bleed(player:Player, share:float) -> int:
    loss = min(player.hp - 1, max(1, round(max_hp(player) * share)))
    player.hp -= max(0, loss)
    return max(0, loss)


def buff(player:Player, buff_id:str) -> None:
    if buff_id not in player.buffs:
        apply_buff(player, buff_id)


def locked(player:Player, rng:random.Random) -> list[str]:
    return [rng.choice(NO_INVITE).format(**values(player))]


def audience(player:Player, offer, price:int,
             rng:random.Random) -> list[str]:
    if not player.profile.get(INVITE_KEY):
        return locked(player, rng)
    roll = rng.random()
    if roll < AUDIENCE_ODDS[0]:
        player.gold += FAVOR_GOLD
        buff(player, "duchess_favor")
        return [rng.choice(FAVOR).format(**values(player, gold=FAVOR_GOLD))]
    if roll < AUDIENCE_ODDS[1]:
        player.gold += GIFT_GOLD
        return [rng.choice(GIFT).format(**values(player, gold=GIFT_GOLD))]
    if roll < AUDIENCE_ODDS[2]:
        loss = bleed(player, HURT_SHARE)
        return [rng.choice(DISMISSED).format(**values(player)),
                f"❤ −{loss} HP."]
    if player.gender == "Male":
        loss = bleed(player, LEASH_SHARE)
        buff(player, "castle_leash")
        return [rng.choice(LEASH).format(**values(player)),
                f"❤ −{loss} HP."]
    loss = bleed(player, LEASH_SHARE)
    buff(player, "castle_rings")
    return [rng.choice(RINGS).format(**values(player)), f"❤ −{loss} HP."]


def banquet(player:Player, offer, price:int,
            rng:random.Random) -> list[str]:
    if not player.profile.get(INVITE_KEY):
        return locked(player, rng)
    if rng.random() < BANQUET_ODDS:
        player.hp = max_hp(player)
        return [rng.choice(BANQUET_HONOR).format(**values(player)),
                "❤ Fully restored."]
    loss = bleed(player, BANQUET_SHARE)
    buff(player, "castle_bitten")
    return [rng.choice(BANQUET_MAIN).format(**values(player)),
            f"❤ −{loss} HP."]


def gate(player:Player, offer, price:int, rng:random.Random) -> list[str]:
    return [rng.choice(GATE_TALK)]

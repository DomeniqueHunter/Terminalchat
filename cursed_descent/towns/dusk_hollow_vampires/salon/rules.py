import random

from ....formulas import apply_buff, max_hp
from ....locations.common import pronouns
from ....models import Player
from ..castle.content import INVITE_KEY
from .content import (
    BITE, BITE_PAY, BITE_SHARE, FAVOR_KEY, GOSSIP, PRESENT_ALREADY,
    PRESENT_FAVOR, PRESENT_NO, PRESENT_YES, SERVE, SERVE_BITE,
    SERVE_BITE_CHANCE, SERVE_PAY, SMALL_SHARE, TEA, TEA_BITE,
    TEA_BITE_CHANCE,
)


def values(player:Player, **extra) -> dict:
    _, them, their = pronouns(player.gender)
    return {"name": player.name, "them": them, "their": their, **extra}


def favor(player:Player, step:int=1) -> None:
    player.profile[FAVOR_KEY] = player.profile.get(FAVOR_KEY, 0) + step


def bleed(player:Player, share:float) -> int:
    loss = min(player.hp - 1, max(1, round(max_hp(player) * share)))
    player.hp -= max(0, loss)
    return max(0, loss)


def buff(player:Player, buff_id:str) -> None:
    if buff_id not in player.buffs:
        apply_buff(player, buff_id)


def guest(player:Player, offer, price:int, rng:random.Random) -> list[str]:
    favor(player)
    buff(player, "salon_poise")
    lines = [rng.choice(TEA).format(**values(player))]
    if rng.random() < TEA_BITE_CHANCE:
        loss = bleed(player, SMALL_SHARE)
        lines += [rng.choice(TEA_BITE).format(**values(player)),
                  f"❤ −{loss} HP."]
    return lines


def serve(player:Player, offer, price:int, rng:random.Random) -> list[str]:
    favor(player)
    pay = rng.randint(*SERVE_PAY)
    player.gold += pay
    if rng.random() < SERVE_BITE_CHANCE:
        loss = bleed(player, SMALL_SHARE)
        return [rng.choice(SERVE_BITE).format(**values(player, pay=pay)),
                f"❤ −{loss} HP."]
    return [rng.choice(SERVE).format(**values(player, pay=pay))]


def bite(player:Player, offer, price:int, rng:random.Random) -> list[str]:
    favor(player)
    player.gold += BITE_PAY
    loss = bleed(player, BITE_SHARE)
    buff(player, "pale_kiss")
    return [rng.choice(BITE).format(**values(player, pay=BITE_PAY)),
            f"❤ −{loss} HP."]


def gossip(player:Player, offer, price:int, rng:random.Random) -> list[str]:
    return [rng.choice(GOSSIP)]


def present(player:Player, offer, price:int, rng:random.Random) -> list[str]:
    if player.profile.get(INVITE_KEY):
        player.gold += price
        return [rng.choice(PRESENT_ALREADY).format(price=price)]
    if player.profile.get(FAVOR_KEY, 0) < PRESENT_FAVOR:
        player.gold += price
        return [rng.choice(PRESENT_NO).format(**values(player, price=price))]
    player.profile[INVITE_KEY] = True
    return [rng.choice(PRESENT_YES).format(**values(player)),
            "📜 Invitation to the castle received."]

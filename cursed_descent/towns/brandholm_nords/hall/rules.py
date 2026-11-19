import random

from ....formulas import apply_buff
from ....models import Player
from . import content


def audience(services, player:Player, offer) -> list:
    from ....models import Message
    rng = services.rng
    lines = [rng.choice(content.AUDIENCE_BASE)]
    lines += [text for flag, text in content.AUDIENCE_FLAGS
              if player.profile.get(flag)]
    return [Message("\n".join(lines), player.name)]


def book(services, player:Player, offer) -> list:
    from ....models import Message
    return [Message("\n".join(content.BOOK), player.name)]


def favour(services, player:Player, offer) -> list:
    from ....models import Message
    if content.FAVOUR_BUFF in player.buffs:
        return [Message(content.HAS_FAVOUR, player.name)]
    if player.gold < offer.price:
        return [Message(f"That costs {offer.price} gold. {player.name} "
                        f"only has {player.gold}.", player.name)]
    player.gold -= offer.price
    apply_buff(player, content.FAVOUR_BUFF)
    text = random.Random(services.rng.random()).choice(content.FAVOUR)
    return [Message(f"{text}\n💰 Gold: {player.gold}", player.name)]

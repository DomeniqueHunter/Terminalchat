from typing import Any

from ..config import MAID_PRICE_FACTOR, NPC_HIRE_PRICE
from ..models import Player


def is_maid(player:Player) -> bool:
    return player.npc == "maid"


def owns_maid(repository:Any, player:Player, maid:Player) -> bool:
    owner = repository.load(maid.profile.get("owner", ""))
    if owner is None:
        return False
    return (owner.name == player.name
            or repository.account_for(owner) == repository.account_for(player))


def hire_price(player:Player) -> int:
    factor = MAID_PRICE_FACTOR if is_maid(player) else 1
    return NPC_HIRE_PRICE * player.level * factor


def spend_points(player:Player) -> None:
    focus = player.profile.get("focus")
    if not focus:
        return
    turn = 0
    while player.free_points > 0:
        player.stats[focus[turn % len(focus)]] += 1
        player.free_points -= 1
        turn += 1

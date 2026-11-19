from ....config import TUNING_PRICE
from ....models import Player
from ....orientation import likes_of
from ....view import Button, Panel
from .content import BLURB, COACHES, LIKES_TEXT
from .rules import options, waiting


def panel(services, player:Player) -> Panel:
    busy = waiting(services, player)
    free = services.is_admin(player.name)
    buttons = tuple(
        Button(f"{option.label} with {COACHES[option.coach]} "
               f"({'free' if free else f'{TUNING_PRICE} g'})",
               f"!tuning_room {option.coach}", "",
               not busy and (player.gold >= TUNING_PRICE or free)
               and likes_of(player) != option.likes)
        for option in options(player))
    lines = [BLURB, f"You like: {LIKES_TEXT[likes_of(player)]}.",
             f"💰 {player.name}: {player.gold} gold"]
    if busy:
        lines.append("You have already been trained today.")
    return Panel("🎛 The Tuning Room", tuple(lines), buttons)

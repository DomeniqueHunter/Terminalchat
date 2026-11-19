from dataclasses import dataclass

from ....config import TUNING_DAY_KEY, TUNING_PRICE
from ....models import Message, Player
from ....orientation import likes_of, traits_of
from .content import (
    ASK_FIRST, CLOSED, COACHES, KIND_LABELS, LIKES_TEXT, REFUSALS, SAME,
    SCENES, TOO_SOON, UNKNOWN,
)


@dataclass(frozen=True)
class Option:
    coach: str
    kind: str
    likes: str

    @property
    def label(self) -> str:
        return KIND_LABELS[self.kind]


def options(player:Player) -> list[Option]:
    traits = traits_of(player.gender)
    if not traits:
        return []
    found: list[Option] = []
    if len(traits) == 1:
        own = next(iter(traits))
        other = "vagina" if own == "penis" else "penis"
        found.append(Option("seraphine", "straight", other))
        if player.gender == "Male":
            found += [Option("taren", "fag", own), Option("camille", "fag", own)]
        elif player.gender == "Female":
            found.append(Option("ysolde", "lesbian", own))
        else:
            found.append(Option("camille", "homo", own))
    found.append(Option("ilaria", "bi", "both"))
    return found


def option_for(player:Player, coach:str) -> Option | None:
    return next((option for option in options(player)
                 if option.coach == coach), None)


def waiting(services, player:Player) -> bool:
    if services.is_admin(player.name):
        return False
    return player.profile.get(TUNING_DAY_KEY, -1) >= services.world.day


def menu(services, player:Player) -> list[Message]:
    lines = [f"🎛 The Tuning Room. You like: "
             f"{LIKES_TEXT[likes_of(player)]}.", ASK_FIRST]
    price = "free" if services.is_admin(player.name) else (
        f"{TUNING_PRICE} gold")
    for option in options(player):
        lines.append(f"  {COACHES[option.coach]}: {option.label} ({price})")
    if not options(player):
        lines.append("  Nobody has anything to teach you yet.")
    if waiting(services, player):
        lines.append("You have already been trained today.")
    return [Message("\n".join(lines), player.name)]


def train(services, player:Player, coach:str) -> list[Message]:
    option = option_for(player, coach)
    if option is None:
        return [Message(REFUSALS[coach], player.name)]
    if likes_of(player) == option.likes:
        return [Message(SAME, player.name)]
    if waiting(services, player):
        return [Message(TOO_SOON, player.name)]
    free = services.is_admin(player.name)
    if player.gold < TUNING_PRICE and not free:
        return [Message(f"{COACHES[coach]} names the price: {TUNING_PRICE} "
                        f"gold. You do not have it.", player.name)]
    if not free:
        player.gold -= TUNING_PRICE
        player.profile[TUNING_DAY_KEY] = services.world.day
    player.profile["orientation"] = option.likes
    scene = SCENES[(coach, option.kind)]
    return [Message(f"{text}", player.name) for text in scene] + [
        Message(f"✨ {option.label}: you now like {LIKES_TEXT[option.likes]}. "
                f"💰 {player.gold}", player.name)]


def do_tuning_room(services, player:Player, args:list[str]) -> list[Message]:
    if services.in_run(player):
        return [Message(CLOSED, player.name)]
    name = args[0].casefold() if args else ""
    if not name:
        return menu(services, player)
    if name not in COACHES:
        return [Message(UNKNOWN, player.name)]
    return train(services, player, name)

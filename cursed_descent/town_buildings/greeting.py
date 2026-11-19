import random

from ..models import Player
from ..races import race_of_town
from ..towns import town_of
from . import registry


OFFERS = {
    "shop": "Browse the shelves or sell me your loot – [shop] shows "
            "what I have.",
}
OFFERS.update({spec.key: spec.greeting
               for spec in registry.specs().values() if spec.greeting})
COUNTERS = tuple(spec.key for spec in registry.specs().values()
                 if spec.counter is not None)
GREETED = tuple(OFFERS) + COUNTERS
ICONS = {"shop": "🛍"}
ICONS.update({spec.key: spec.icon for spec in registry.specs().values()
              if spec.icon})


def greeting_for(player:Player, building:str,
                 rng:random.Random | None=None) -> str:
    rng = rng or random.Random()
    text = plain_greeting(player, building, rng)
    if not text:
        return text
    from ..exposure import reaction_line
    keeper = next((resident for resident in town_of(player).residents
                   if resident.building == building), None)
    reaction = reaction_line(
        player, building, keeper.first_name if keeper else "The keeper",
        keeper.personality if keeper else "", rng)
    gaze = gaze_line(player, keeper.first_name if keeper else "The keeper",
                     rng)
    return "\n".join(part for part in (text, reaction, gaze) if part)


def gaze_line(player:Player, keeper:str, rng:random.Random) -> str:
    town = town_of(player)
    if not town.gaze or player.gender != "Male":
        return ""
    return rng.choice(town.gaze).format(name=player.name, keeper=keeper)


def plain_greeting(player:Player, building:str,
                   rng:random.Random) -> str:
    town = town_of(player)
    spec = registry.get(building)
    special = spec.counter if spec is not None else None
    if spec is not None and spec.greeter is not None:
        return spec.greeter(player, rng)
    if special is not None:
        return (f"{special.icon} {special.keeper} ({special.title}) greets "
                f"{player.name}: {special.quote} Take a look at the "
                f"offers.")
    if building not in GREETED:
        return ""
    offers = race_of_town(town.key).offers
    return keeper_greeting(player, building, rng,
                           offers.get(building, OFFERS[building]))


def keeper_greeting(player:Player, building:str, rng:random.Random,
                    offer:str) -> str:
    keeper = next((resident for resident in town_of(player).residents
                   if resident.building == building), None)
    if keeper is None:
        return ""
    return (f"{ICONS[building]} {keeper.first_name} {keeper.last_name} "
            f"({keeper.role}) greets {player.name}: "
            f"{rng.choice(keeper.quotes)} {offer}")

from typing import Any

from ....config import DEFAULT_GENDER, PRONOUNS
from ....captivity import take
from ....models import Player


FURNITURE_QUOTES = ("...", "(The stool creaks quietly.)",
                    "(A faint, muffled sigh.)")


def stool_look(player:Player) -> str:
    height = player.body.get("height", 170)
    weight = player.body.get("weight", 70)
    their = PRONOUNS.get(player.gender, PRONOUNS[DEFAULT_GENDER])[2]
    return (f"{player.name}, {player.age} years, {height} cm and "
            f"{weight} kg, kneels under a padded board and is stitched "
            f"into it as a stool. {their.capitalize()} face "
            f"looks out from under the seat, flushed and quiet.")


def make_furniture(player:Player, repository:Any, day:int=0) -> int:
    look = stool_look(player)
    repository.bury(player, "furniture: turned into a stool of the house")
    return take(player, repository, "furniture", {
        "kind": "furniture", "role": "Stool of the Fat Ass Café",
        "look": look, "quotes": list(FURNITURE_QUOTES)}, day)

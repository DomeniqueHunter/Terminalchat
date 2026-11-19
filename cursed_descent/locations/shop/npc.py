import random

from ...body import size_class
from ...models import Player
from .content import SHOPKEEPER


def greeting(player:Player) -> str:
    body = player.body
    tags = [f"breasts:{body['breasts']}", f"build:{body['build']}",
            f"size:{size_class(body['height'])}"]
    special = [SHOPKEEPER["greet_body"][tag] for tag in tags
               if tag in SHOPKEEPER["greet_body"]]
    special += [SHOPKEEPER["greet_gear"][item_id]
                for item_id in player.equipment.values()
                if item_id in SHOPKEEPER["greet_gear"]]
    pool = SHOPKEEPER["greet"] + special * 2
    return random.choice(pool).format(name=player.name)

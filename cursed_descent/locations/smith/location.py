from ...config import SMITH_STOCK
from ...models import Player
from .content import SMITH_TALK, SMITH_TEXTS


def smith_extra(player:Player) -> list[str]:
    return [SMITH_TEXTS["hunger"]]


SMITH = {
    "id": "smith",
    "name": "<<npc.morgrin_first>>'s Forge",
    "description": (
        "<<npc.morgrin_first>>'s forge burns with green fire at the dungeon entrance. "
        "Racks of weapons line the soot-black walls, sorted by how hungry "
        "they are, and a few plain pieces of armour hang by the door. "
        "<<npc.morgrin_first>> sells weapons and metal armour only - lace is <<npc.velvet_first>>'s "
        "business."),
    "categories": ("weapons", "armor"),
    "stock": SMITH_STOCK,
    "always": "smith",
    "creator": "smith",
    "texts": {
        "greeting": SMITH_TEXTS["greeting"],
        "extra": smith_extra,
        "talk": SMITH_TALK,
        "buy": [SMITH_TEXTS["done"]],
        "sell": ["<<npc.morgrin_first>> weighs the {item} in his hand and grunts. 'It "
                 "will do. {price} gold.'"],
        "buys": ("weapons", "armor"),
        "broke": SMITH_TEXTS["poor"],
        "full": SMITH_TEXTS["full"],
        "which": "'Which one?' <<npc.morgrin_first>> grunts. '[buy <nr>] or [forge <nr>].'",
        "which_sell": "'Sell what?' <<npc.morgrin_first>> grunts. '[sell <nr>].'",
        "not_buying": "'I don't buy {item}. Weapons and armour only.'",
        "no_category": "'No {category} here,' <<npc.morgrin_first>> grunts.",
    },
}

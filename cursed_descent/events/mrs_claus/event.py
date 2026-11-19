import random
from typing import Any

from ...config import MRS_CLAUS_ESCORTS
from ...content import ENEMIES, ITEMS
from ...dungeon import build_enemy, give_item
from .content import EVENT_TEXTS
from .items import GIFT_WEIGHTS


class MrsClausMixin:
    session: Any
    event: dict[str, Any]

    def offer_mrs_claus(self, now:float) -> list[str]:
        session = self.session
        texts = EVENT_TEXTS["mrs_claus"]
        boss = build_enemy(1, "mrs_claus", ENEMIES["mrs_claus"],
                           session.stage)
        boss.boss = True
        kind = random.choice(list(MRS_CLAUS_ESCORTS))
        count = MRS_CLAUS_ESCORTS[kind]
        escorts = [build_enemy(index, kind, ENEMIES[kind], session.stage)
                   for index in range(2, count + 2)]
        intro = ["", texts["intro"], texts[kind].format(count=count)]
        return session.start_bonus_fight("mrs_claus", [boss] + escorts,
                                         intro, now)


def pick_gift() -> str:
    ids = list(GIFT_WEIGHTS)
    return random.choices(ids, weights=[GIFT_WEIGHTS[i] for i in ids])[0]


def claus_gifts(party:list[Any]) -> list[str]:
    texts = EVENT_TEXTS["mrs_claus"]
    lines: list[str] = []
    for player in party:
        item_id = pick_gift()
        lines.append(texts["gift"].format(
            name=player.name, item=ITEMS[item_id]["name"]))
        lines.append(give_item(player, item_id))
    return lines

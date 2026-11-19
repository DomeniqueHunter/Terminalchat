import random
from typing import Any

from ...config import LICH_MAX_ESCORTS
from ...content import ENEMIES
from ...dungeon import build_consort, build_enemy
from .content import EVENT_TEXTS


class LichMixin:
    session: Any
    event: dict[str, Any]

    def offer_lich(self, now:float) -> list[str]:
        session = self.session
        texts = EVENT_TEXTS["lich"]
        queen = build_enemy(1, "lich_queen", ENEMIES["lich_queen"],
                            session.stage)
        queen.boss = True
        pool = session.remains.consorts(session.run_id)
        escorts = random.sample(pool, min(len(pool), LICH_MAX_ESCORTS))
        enemies = [queen] + [build_consort(index, entry, session.stage)
                             for index, entry in enumerate(escorts, 2)]
        intro = ["", texts["intro"]]
        if escorts:
            names = ", ".join(entry["name"] for entry in escorts)
            intro.append(texts["escort"].format(names=names))
        intro += session.consort_recognition(escorts)
        return session.start_bonus_fight("lich", enemies, intro, now)

import random
from typing import Any

from ...config import HUT_SLEEP_AMBUSH_HEAL
from ...content import ENEMIES
from ...dungeon import build_enemy
from ...models import Message, Player
from .content import VENUE_TEXTS


class LodgeEventsMixin:
    session: Any
    event: dict[str, Any]

    def reginald_returns(self, player:Player, command:str,
                         now:float) -> list[Message]:
        from ...combat import ambush
        session = self.session
        texts = VENUE_TEXTS["hut"]
        enemy = build_enemy(1, "safari_hunter", ENEMIES["safari_hunter"],
                            session.stage)
        lines = ["", texts[f"return_{command}"].format(name=player.name)]
        if command == "sleep":
            self.heal_party(HUT_SLEEP_AMBUSH_HEAL)
            target = random.choice(session.living())
            result = ambush(enemy, target)
            lines += result.lines
            lines += session.record_deaths(result.fallen, session.stage - 1)
        self.save_party()
        self.reset()
        if not session.living():
            return [Message("\n".join(lines + session.end_run()))]
        return [Message("\n".join(session.start_bonus_fight(
            "hunter", [enemy], lines, now)))]

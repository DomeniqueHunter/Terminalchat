import random
from typing import Any

from ...config import HOARD_TAKE_CHANCE, WARDROBE_EAT_CHANCE
from ...dungeon import chest_loot, stage_gold
from ...hoard import confiscate, hoard_note, take_hoards
from ...models import Message, Player
from .content import VENUE_TEXTS


FATES = ("wardrobe",)


class WardrobeMixin:
    session: Any
    event: dict[str, Any]

    def offer_wardrobe(self) -> list[str]:
        texts = VENUE_TEXTS["wardrobe"]
        self.event["data"]["inside"] = True
        return ["", texts["intro"], texts["enter"],
                self.options_line(texts)]

    def enter_wardrobe(self) -> list[Message]:
        self.event["data"]["inside"] = True
        return self.continue_venue([VENUE_TEXTS["wardrobe"]["enter"]])

    def wardrobe_examine(self) -> list[Message]:
        note = hoard_note(self.session.remains, FATES, self.session.run_id)
        lines = [VENUE_TEXTS["wardrobe"]["examine"]] + ([note] if note
                                                       else [])
        return [Message("\n".join(lines))]

    def wardrobe_action(self, player:Player, command:str,
                        now:float) -> list[Message]:
        texts = VENUE_TEXTS["wardrobe"]
        session = self.session
        if random.random() < WARDROBE_EAT_CHANCE:
            from ...combat import fate_text
            text = fate_text(player, "wardrobe", None)
            lines = session.kill_outside(
                player, "wardrobe", text, "a living wardrobe", "mimics",
                hoard=confiscate(player, HOARD_TAKE_CHANCE))
            if not session.living():
                self.reset()
                return [Message("\n".join(lines + session.end_run()))]
            self.save_party()
            return self.finish(lines, now)
        lines = [texts["open_loot"].format(name=player.name)]
        lines += chest_loot(session.stage, player, stage_gold(session.stage))
        lines += take_hoards(session.remains, FATES, session.run_id, player)
        session.repository.save(player)
        return self.finish(lines, now)

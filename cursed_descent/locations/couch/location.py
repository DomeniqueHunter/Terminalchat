import random
from typing import Any

from ...config import (
    COUCH_EAT_CHANCE, COUCH_HEAL, COUCH_MIMIC_CHANCE, HOARD_TAKE_CHANCE,
)
from ...dungeon import spawn_mimic
from ...hoard import confiscate
from ...models import Message, Player
from .content import VENUE_TEXTS


class CouchMixin:
    session: Any
    event: dict[str, Any]

    def offer_couch(self) -> list[str]:
        texts = VENUE_TEXTS["couch"]
        self.event["data"]["mimic"] = random.random() < COUCH_MIMIC_CHANCE
        self.event["data"]["inside"] = True
        return ["", texts["intro"], texts["enter"],
                self.options_line(texts)]

    def enter_couch(self) -> list[Message]:
        self.event["data"]["inside"] = True
        return self.continue_venue([VENUE_TEXTS["couch"]["enter"]])

    def couch_action(self, player:Player, command:str,
                     now:float) -> list[Message]:
        texts = VENUE_TEXTS["couch"]
        mimic = self.event["data"]["mimic"]
        if command == "inspect":
            self.event["used"].add("inspect")
            key = "inspect_ok" if mimic else "inspect_safe"
            return self.continue_venue([texts[key].format(name=player.name)])
        if not mimic:
            self.heal_party(COUCH_HEAL)
            return self.finish([texts["safe"].format(
                name=player.name, percent=round(COUCH_HEAL * 100))], now)
        session = self.session
        if random.random() < COUCH_EAT_CHANCE:
            from ...combat import fate_text
            text = fate_text(player, "couch_mimic", None)
            lines = session.kill_outside(
                player, "couch_mimic", text, "a mimic couch", "mimics",
                hoard=confiscate(player, HOARD_TAKE_CHANCE))
            if not session.living():
                self.reset()
                return [Message("\n".join(lines + session.end_run()))]
            self.save_party()
            return self.finish(lines, now)
        self.reset()
        intro = ["", texts["fight"].format(name=player.name)]
        return [Message("\n".join(session.start_bonus_fight(
            "mimic", spawn_mimic(session.stage), intro, now)))]

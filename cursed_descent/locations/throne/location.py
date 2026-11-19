import random
from typing import Any

from ...config import HOARD_TAKE_CHANCE, THRONE_TAKE_CHANCE
from ...content import ADEPT_BUFFS
from ...formulas import apply_buff, set_bonus_text
from ...hoard import confiscate, hoard_note, open_hoards, take_hoards
from ...models import Message, Player
from .content import VENUE_TEXTS


FATES = ("throne",)


class ThroneMixin:
    session: Any
    event: dict[str, Any]

    def offer_throne(self) -> list[str]:
        texts = VENUE_TEXTS["throne"]
        self.event["data"]["inside"] = True
        return ["", texts["intro"], texts["enter"],
                self.options_line(texts)]

    def enter_throne(self) -> list[Message]:
        self.event["data"]["inside"] = True
        return self.continue_venue([VENUE_TEXTS["throne"]["enter"]])

    def throne_options(self) -> list[str]:
        session = self.session
        options = ["claim"]
        if open_hoards(session.remains, FATES, session.run_id):
            options.append("take")
        return options + ["depart"]

    def throne_examine(self) -> list[Message]:
        note = hoard_note(self.session.remains, FATES, self.session.run_id)
        lines = [VENUE_TEXTS["throne"]["examine"]] + ([note] if note
                                                     else [])
        return [Message("\n".join(lines))]

    def throne_action(self, player:Player, command:str,
                      now:float) -> list[Message] | None:
        if self.outside():
            return None
        texts = VENUE_TEXTS["throne"]
        session = self.session
        if command == "take":
            lines = take_hoards(session.remains, FATES, session.run_id,
                                player) or [texts["none"]]
            session.repository.save(player)
            return self.continue_venue(lines)
        if command != "claim":
            return None
        if random.random() < THRONE_TAKE_CHANCE:
            from ...combat import fate_text
            text = fate_text(player, "throne", None)
            lines = session.kill_outside(
                player, "throne", text, "the Corruption Throne",
                "corruption",
                hoard=confiscate(player, HOARD_TAKE_CHANCE))
            if not session.living():
                self.reset()
                return [Message("\n".join(lines + session.end_run()))]
            self.save_party()
            return self.finish(lines, now)
        buff_id = random.choice(list(ADEPT_BUFFS))
        buff = ADEPT_BUFFS[buff_id]
        apply_buff(player, buff_id)
        lines = [texts["sit"].format(name=player.name),
                 buff["text"].format(name=player.name),
                 f"✨ {player.name}: {set_bonus_text(buff)} until death."]
        session.repository.save(player)
        return self.finish(lines, now)

import random
from typing import Any

from ...config import (
    ADEPT_BOOT_ERROR, ADEPT_GALLERY_SIZE, ADEPT_STATUE_CHANCE,
    ADEPT_SWEAT_ERROR, ROUND_TIMEOUT_SECONDS,
)
from ...content import ITEMS
from ...dungeon import give_item, roll_item
from ...formulas import apply_buff, set_bonus_text
from ...locations.common import cycle_stage
from ...models import Message, Player
from ...sweat import sweat_tier
from ..common import options_text, their
from .content import (
    ADEPT_BUFFS, ADEPT_FLUSTER, ADEPT_STATUE_TEXTS, EVENT_TEXTS,
    GALLERY_LABELS,
)


ADEPT_OPTIONS = ("volunteer", "depart")


def sweaty_boots(player:Player) -> bool:
    item_id = player.equipment.get("feet")
    if not item_id or sweat_tier(player) < 1:
        return False
    item = ITEMS[item_id]
    return "leather" in f"{item['name']} {item.get('note', '')}".casefold()


def adept_distraction(player:Player) -> tuple[float, list[str]]:
    texts = EVENT_TEXTS["adept"]
    tier = sweat_tier(player)
    chance = tier * ADEPT_SWEAT_ERROR
    notes = [texts["sweat"].format(name=player.name)] if tier else []
    if sweaty_boots(player):
        chance += ADEPT_BOOT_ERROR
        notes.append(texts["boots"].format(name=player.name))
    return chance, notes


class AdeptMixin:
    session: Any
    event: dict[str, Any]

    def offer_adept(self) -> list[str]:
        texts = EVENT_TEXTS["adept"]
        self.event["phase"] = "adept"
        self.event["data"]["buffed"] = set()
        self.event["data"]["inside"] = True
        options = self.strip_timer(texts["options"]).format(
            options=options_text(self.available()),
            seconds=int(ROUND_TIMEOUT_SECONDS))
        return ["", texts["intro"], texts["enter"],
                *self.statue_gallery(), options]

    def enter_adept(self) -> list[Message]:
        self.event["data"]["inside"] = True
        return self.continue_event([EVENT_TEXTS["adept"]["enter"]]
                                   + self.statue_gallery())

    def statue_gallery(self) -> list[str]:
        texts = EVENT_TEXTS["adept"]
        current = cycle_stage(self.session.stage)
        statues = [entry for entry in self.session.remains.entries
                   if entry["fate"] == "adept_statue"
                   and cycle_stage(entry["stage"]) == current]
        if not statues:
            return []
        shown = statues[-ADEPT_GALLERY_SIZE:]
        names = ", ".join(
            f"{entry['name']} ({GALLERY_LABELS.get(entry.get('detail'), '?')})"
            for entry in shown)
        lines = [texts["gallery"].format(count=len(statues), names=names)]
        party = {player.name for player in self.session.party}
        for name in sorted(party & {entry["name"] for entry in statues}):
            lines.append(texts["gallery_own"].format(name=name))
        return lines

    def adept_action(self, player:Player, command:str,
                     now:float) -> list[Message]:
        texts = EVENT_TEXTS["adept"]
        if command == "depart":
            self.save_party()
            return self.finish([texts["depart"]], now)
        buffed = self.event["data"]["buffed"]
        if player.name in buffed:
            return [Message(texts["again"], player.name)]
        buffed.add(player.name)
        distraction, notes = adept_distraction(player)
        if random.random() < ADEPT_STATUE_CHANCE + distraction:
            return self.adept_statue(player, now, notes)
        buff_id = random.choice(list(ADEPT_BUFFS))
        buff = ADEPT_BUFFS[buff_id]
        apply_buff(player, buff_id)
        effect = set_bonus_text(buff)
        lines = notes + [texts["cast"].format(name=player.name),
                         buff["text"].format(name=player.name),
                         texts["lasts"].format(name=player.name,
                                               effect=effect)]
        if buff_id in ADEPT_FLUSTER:
            lines.append(ADEPT_FLUSTER[buff_id].format(name=player.name))
            gift = roll_item(self.session.stage, equipment_chance=0.0)
            lines.append(give_item(player, gift))
        if all(member.name in buffed for member in self.session.living()):
            self.save_party()
            return self.finish(lines, now)
        return self.continue_event(lines)

    def adept_statue(self, player:Player, now:float,
                     notes:list[str] | None=None) -> list[Message]:
        session = self.session
        morph = random.choice([key for key in ADEPT_STATUE_TEXTS
                               if key != "sorry"])
        apply_buff(player, morph)
        text = ADEPT_STATUE_TEXTS[morph].format(name=player.name,
                                                their=their(player))
        lines = (notes or []) + [
            EVENT_TEXTS["adept"]["cast"].format(name=player.name)]
        lines += session.kill_outside(player, "adept_statue", text,
                                      "a young mage adept", "mages", morph)
        lines.append(ADEPT_STATUE_TEXTS["sorry"])
        if not session.living():
            self.reset()
            return [Message("\n".join(lines + session.end_run()))]
        if all(member.name in self.event["data"]["buffed"]
               for member in session.living()):
            self.save_party()
            return self.finish(lines, now)
        return self.continue_event(lines)

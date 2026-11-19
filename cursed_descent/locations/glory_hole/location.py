import random
from typing import Any

from ...config import GLORY_BOON_CHANCE, GLORY_RELIEF_CHANCE, HUNG_GENDERS
from ...content import BUFFS, ITEMS
from ...dungeon import give_item, roll_item
from ...formulas import apply_buff, set_bonus_text
from ...models import Message, Player
from .content import BOON_TEXTS, RELIEF_TEXTS, VENUE_TEXTS


def known_mouth(remains:Any, run_id:str) -> str:
    names = [entry["name"] for entry in remains.entries
             if entry["fate"] == "glory_hole" and entry["run"] != run_id]
    return names[-1] if names else ""


class GloryHoleMixin:
    session: Any
    event: dict[str, Any]

    def glory_users(self) -> list[Player]:
        used = self.event["used"]
        return [member for member in self.session.living()
                if member.gender in HUNG_GENDERS
                and f"glory:{member.name}" not in used]

    def offer_glory_hole(self) -> list[str]:
        texts = VENUE_TEXTS["glory_hole"]
        mouth = known_mouth(self.session.remains, self.session.run_id)
        self.event["data"]["inside"] = True
        self.event["data"]["mouth"] = mouth
        lines = ["", texts["intro"]]
        if mouth:
            lines.append(texts["known"].format(dead=mouth))
        if not self.glory_users():
            lines.append(texts["none"])
        return lines + [self.options_line(texts)]

    def glory_hole_options(self) -> list[str]:
        return (["thrust"] if self.glory_users() else []) + ["depart"]

    def glory_hole_examine(self) -> list[Message]:
        texts = VENUE_TEXTS["glory_hole"]
        mouth = self.event["data"].get("mouth", "")
        if mouth:
            return [Message(texts["examine_known"].format(dead=mouth))]
        return [Message(texts["examine"])]

    def glory_hole_action(self, player:Player, command:str,
                          now:float) -> list[Message] | None:
        if command != "thrust":
            return None
        texts = VENUE_TEXTS["glory_hole"]
        session = self.session
        key = f"glory:{player.name}"
        if player.gender not in HUNG_GENDERS:
            return [Message(texts["unfit"].format(name=player.name),
                            player.name)]
        if key in self.event["used"]:
            return [Message(texts["spent"].format(name=player.name),
                            player.name)]
        self.event["used"].add(key)
        roll = random.random()
        if roll < GLORY_RELIEF_CHANCE:
            lines = [random.choice(RELIEF_TEXTS).format(name=player.name)]
            lines += self.glory_buff(player, "glory_relief")
        elif roll < GLORY_RELIEF_CHANCE + GLORY_BOON_CHANCE:
            item_id = roll_item(session.stage)
            lines = [random.choice(BOON_TEXTS).format(
                name=player.name, item=ITEMS[item_id]["name"])]
            lines += self.glory_buff(player, "glory_boon")
            lines.append(give_item(player, item_id))
        else:
            return self.glory_swallow(player, now)
        session.repository.save(player)
        return self.continue_venue(lines)

    def glory_buff(self, player:Player, buff_id:str) -> list[str]:
        apply_buff(player, buff_id)
        return [VENUE_TEXTS["glory_hole"]["relief_line"].format(
            name=player.name, bonus=set_bonus_text(BUFFS[buff_id]))]

    def glory_swallow(self, player:Player, now:float) -> list[Message]:
        from ...combat import fate_text
        session = self.session
        text = fate_text(player, "glory_hole", None)
        lines = session.kill_outside(player, "glory_hole", text,
                                     "the Glory Hole", "corruption")
        if not session.living():
            self.reset()
            return [Message("\n".join(lines + session.end_run()))]
        self.save_party()
        return self.continue_venue(lines)

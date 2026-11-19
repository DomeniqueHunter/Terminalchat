import random
from typing import Any

from ...config import (
    HUNG_GENDERS, PRIVY_ATTEND_PAY, PRIVY_FATES, PRIVY_FIXTURE_CHANCE,
    PRIVY_FIXTURE_PAY, PRIVY_FIXTURE_SAFE, PRIVY_TIP, PRIVY_TOLL,
    PRIVY_URINAL,
)
from ...content import BUFFS
from ...formulas import apply_buff, set_bonus_text
from ...models import Message, Player
from .content import (
    ATTEND_SCENES, FIXTURE_SCENES, GOSSIP, GRAFFITI, KNOCK_SCENES, SECRETS,
    STALL_SCENES, URINAL_SCENES, VENUE_TEXTS,
)


FATE = "fixture"


class PrivyMixin:
    session: Any
    event: dict[str, Any]

    def offer_privy(self) -> list[str]:
        texts = VENUE_TEXTS["privy"]
        self.event["data"]["inside"] = False
        return ["", texts["intro"], texts["door"], self.options_line(texts)]

    def enter_privy(self) -> list[Message]:
        self.event["data"]["inside"] = True
        return self.continue_venue([VENUE_TEXTS["privy"]["enter"]])

    def privy_options(self) -> list[str]:
        hung = any(member.gender in HUNG_GENDERS
                   for member in self.session.living())
        return (["stall"] + (["urinal"] if hung else [])
                + ["wash", "read", "knock", "ask", "tip", "stint attend",
                   "stint fixture", "grumble", "depart"])

    def privy_entries(self) -> list[dict[str, Any]]:
        return [entry for entry in self.session.remains.entries
                if entry["fate"] in PRIVY_FATES]

    def privy_examine(self) -> list[Message]:
        texts = VENUE_TEXTS["privy"]
        if self.outside():
            return [Message(texts["look_outside"])]
        lines = [texts["look"]]
        shown: list[str] = []
        for entry in reversed(self.privy_entries()):
            if entry["name"] not in shown and len(shown) < 4:
                shown.append(entry["name"])
        if shown:
            lines.append(texts["look_fixtures"])
            lines += [texts["look_fixture"].format(nr=nr, name=name)
                      for nr, name in enumerate(shown, 1)]
        else:
            lines.append(texts["look_no_fixtures"])
        return [Message("\n".join(lines))]

    def privy_once(self, player:Player, word:str) -> bool:
        key = f"{word}:{player.name}"
        if key in self.event["used"]:
            return False
        self.event["used"].add(key)
        return True

    def privy_action(self, player:Player, command:str,
                     now:float) -> list[Message] | None:
        word = command.split()[0]
        if word == "stint":
            parts = command.split()
            return self.privy_stint(player, parts[1] if len(parts) > 1
                                    else "")
        handlers = {"stall": self.privy_stall, "wash": self.privy_wash,
                    "urinal": self.privy_urinal,
                    "grumble": self.privy_grumble,
                    "read": self.privy_read, "knock": self.privy_knock,
                    "ask": self.privy_ask, "tip": self.privy_tip}
        if word not in handlers:
            return None
        return handlers[word](player)

    def privy_stall(self, player:Player) -> list[Message]:
        texts = VENUE_TEXTS["privy"]
        values = {"name": player.name, "price": PRIVY_TOLL,
                  "gold": player.gold}
        if f"stall:{player.name}" in self.event["used"]:
            return [Message(texts["stall_used"], player.name)]
        if player.gold < PRIVY_TOLL:
            return [Message(texts["stall_poor"].format(**values),
                            player.name)]
        self.event["used"].add(f"stall:{player.name}")
        player.gold -= PRIVY_TOLL
        apply_buff(player, "privy_relieved")
        self.session.repository.save(player)
        return self.continue_venue([
            texts["stall"].format(**values),
            random.choice(STALL_SCENES).format(name=player.name),
            texts["relieved"].format(
                name=player.name,
                bonus=set_bonus_text(BUFFS["privy_relieved"]))])

    def privy_wash(self, player:Player) -> list[Message]:
        texts = VENUE_TEXTS["privy"]
        if not self.privy_once(player, "wash"):
            return [Message(texts["wash_used"].format(name=player.name),
                            player.name)]
        player.sweat = 0
        apply_buff(player, "privy_fresh")
        self.session.repository.save(player)
        return self.continue_venue([texts["wash"].format(
            name=player.name, bonus=set_bonus_text(BUFFS["privy_fresh"]))])

    def privy_read(self, player:Player) -> list[Message]:
        return self.continue_venue([random.choice(GRAFFITI)])

    def privy_knock(self, player:Player) -> list[Message]:
        texts = VENUE_TEXTS["privy"]
        if not self.privy_once(player, "knock"):
            return [Message(texts["knock_used"].format(name=player.name),
                            player.name)]
        scene = random.choice(KNOCK_SCENES)
        lines = [scene.format(name=player.name)]
        if "velvet cloak" in scene:
            player.gold += 7
            self.session.repository.save(player)
            lines.append(texts["knock_coin"].format(gold=7))
        return self.continue_venue(lines)

    def privy_ask(self, player:Player) -> list[Message]:
        texts = VENUE_TEXTS["privy"]
        if not self.privy_once(player, "ask"):
            return [Message(texts["ask_used"], player.name)]
        return self.continue_venue([random.choice(GOSSIP)])

    def privy_tip(self, player:Player) -> list[Message]:
        texts = VENUE_TEXTS["privy"]
        values = {"name": player.name, "price": PRIVY_TIP,
                  "gold": player.gold}
        if "tipped" in self.event["used"]:
            return [Message(texts["tip_used"], player.name)]
        if player.gold < PRIVY_TIP:
            return [Message(texts["tip_poor"].format(**values),
                            player.name)]
        self.event["used"].add("tipped")
        player.gold -= PRIVY_TIP
        self.session.repository.save(player)
        return self.continue_venue([texts["tip"].format(**values),
                                    random.choice(SECRETS)])

    def privy_urinal(self, player:Player) -> list[Message]:
        texts = VENUE_TEXTS["privy"]
        values = {"name": player.name, "price": PRIVY_URINAL,
                  "gold": player.gold}
        if player.gender not in HUNG_GENDERS:
            return [Message(texts["urinal_no"].format(**values),
                            player.name)]
        if f"urinal:{player.name}" in self.event["used"]:
            return [Message(texts["urinal_used"], player.name)]
        if player.gold < PRIVY_URINAL:
            return [Message(texts["urinal_poor"].format(**values),
                            player.name)]
        self.event["used"].add(f"urinal:{player.name}")
        player.gold -= PRIVY_URINAL
        apply_buff(player, "privy_relieved")
        self.session.repository.save(player)
        return self.continue_venue([
            texts["urinal"].format(**values),
            random.choice(URINAL_SCENES).format(name=player.name),
            texts["relieved"].format(
                name=player.name,
                bonus=set_bonus_text(BUFFS["privy_relieved"]))])

    def privy_stint(self, player:Player, job:str) -> list[Message]:
        texts = VENUE_TEXTS["privy"]
        if job == "attend":
            if f"attend:{player.name}" in self.event["used"]:
                return [Message(texts["stint_used"], player.name)]
            self.event["used"].add(f"attend:{player.name}")
            player.gold += PRIVY_ATTEND_PAY
            self.session.repository.save(player)
            return self.continue_venue([
                random.choice(ATTEND_SCENES).format(name=player.name),
                texts["stint_attend"].format(name=player.name,
                                             gold=PRIVY_ATTEND_PAY)])
        if job != "fixture":
            return [Message("Shifts: [stint attend] or [stint fixture].",
                            player.name)]
        shifts = self.event["data"].setdefault("shifts", {})
        done = shifts.get(player.name, 0)
        shifts[player.name] = done + 1
        player.gold += PRIVY_FIXTURE_PAY
        lines = [random.choice(FIXTURE_SCENES).format(
            name=player.name, their=self.privy_their(player))]
        risky = done >= PRIVY_FIXTURE_SAFE
        lines.append(texts["stint_fixture"].format(
            name=player.name, gold=PRIVY_FIXTURE_PAY,
            warning=texts["stint_warn"].format(name=player.name)
            if risky else ""))
        if risky and random.random() < PRIVY_FIXTURE_CHANCE:
            return self.privy_end(player, lines)
        self.session.repository.save(player)
        return self.continue_venue(lines)

    def privy_their(self, player:Player) -> str:
        from ...events.common import their
        return their(player)

    def privy_grumble(self, player:Player) -> list[Message]:
        texts = VENUE_TEXTS["privy"]
        warned = self.event["data"].setdefault("warned", [])
        if player.name not in warned:
            warned.append(player.name)
            return self.continue_venue(
                [texts["grumble_warn"].format(name=player.name)])
        return self.privy_end(player, [])

    def privy_end(self, player:Player, lines:list[str]) -> list[Message]:
        from ...combat import fate_text
        session = self.session
        text = fate_text(player, FATE, None)
        lines += session.kill_outside(player, FATE, text, "Hedwig",
                                      "privy", "privy")
        if not session.living():
            self.reset()
            return [Message("\n".join(lines + session.end_run()))]
        self.save_party()
        return self.continue_venue(lines)

import random
from typing import Any

from ...config import (
    CHARM_BASE, CHARM_MAX, CHARM_PER_ALLURE, OGRE_EAT_HEAL, OGRE_FATES,
    OGRE_PREGNANCY_CHANCE, OGRE_TALK_EXP, ROUND_TIMEOUT_SECONDS,
)
from ...content import OFFSPRING_TEXTS
from ...dungeon import give_item, roll_item
from ...formulas import allure
from ...models import Message, Player
from ..common import their
from .content import EVENT_TEXTS


OGRE_DINNER = ("charm", "eat", "talk", "sleep", "depart")


class OgreMixin:
    session: Any
    event: dict[str, Any]

    def ogre_victim(self) -> dict[str, Any] | None:
        session = self.session
        names = {player.name for player in session.party}
        eaten = [entry for entry in session.remains.entries
                 if entry["tribe"] == "ogres"
                 and entry["fate"] in OGRE_FATES
                 and entry["run"] != session.run_id]
        known = [entry for entry in eaten if entry["name"] in names]
        pool = known or eaten
        return random.choice(pool) if pool else None

    def offer_ogre(self, victim:dict[str, Any] | None) -> list[str]:
        texts = EVENT_TEXTS["ogre_feast"]
        names = {player.name for player in self.session.party}
        self.event["phase"] = "invite"
        if victim is None:
            name, key = texts["nobody"], "intro_plain"
        elif victim["name"] in names:
            name, key = victim["name"], "intro"
        else:
            name, key = victim["name"], "intro_stranger"
        self.event["data"]["victim"] = name
        return ["", texts[key].format(victim=name),
                texts["invite"].format(seconds=int(ROUND_TIMEOUT_SECONDS))]

    def ogre_action(self, player:Player, command:str,
                    now:float) -> list[Message]:
        texts = EVENT_TEXTS["ogre_feast"]
        victim = self.event["data"]["victim"]
        stage = self.session.stage
        if command == "decline":
            return self.finish([texts["decline"]], now)
        if command == "accept":
            self.event["phase"] = "dinner"
            return self.continue_event([texts["accept"]])
        if command == "depart":
            self.save_party()
            return self.finish([texts["depart"]], now)
        self.event["used"].add(command)
        values = {"name": player.name, "their": their(player),
                  "victim": victim}
        if command == "sleep":
            self.rest_party()
            lines = [texts["sleep"].format(**values)]
            if (not player.pregnant
                    and random.random() < OGRE_PREGNANCY_CHANCE):
                player.pregnant = "ogre"
                player.profile["pregnant_by"] = "an ogre"
                lines.append(OFFSPRING_TEXTS["pregnant"].format(**values))
            self.save_party()
            return self.finish(lines, now)
        if command == "charm":
            chance = min(CHARM_BASE + allure(player) * CHARM_PER_ALLURE,
                         CHARM_MAX)
            if random.random() < chance:
                gift = roll_item(stage + 15, equipment_chance=1.0)
                lines = [texts["charm_ok"].format(**values),
                         give_item(player, gift)]
            else:
                lines = [texts["charm_fail"].format(**values)]
        elif command == "eat":
            self.heal_party(OGRE_EAT_HEAL)
            key = "eat_own" if player.name == victim else "eat"
            lines = [texts[key].format(percent=round(OGRE_EAT_HEAL * 100),
                                       **values)]
        else:
            amount = stage * OGRE_TALK_EXP
            lines = [texts["talk"].format(exp=amount, **values)]
            lines += self.grant_party_exp(amount)
        return self.continue_event(lines)

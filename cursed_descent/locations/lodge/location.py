import random
from typing import Any

from ...config import (
    BONUS_DROPS, HUT_COOK_RISK, HUT_EAT_HEAL, HUT_EAT_RELIEF, HUT_EAT_RISK, HUT_REST_HEAL,
    HUT_REST_RISK, HUT_SEARCH_GOLD, HUT_SEARCH_GOLD_STEP, HUT_SEARCH_RISK,
    HUT_SLEEP_RISK, HUT_STAGES, SCENT_HUNTER_RISK,
)
from ...dungeon import give_item
from ...models import Message, Player
from ...needs import satisfy
from ..butcher.location import cook_meat
from ...scent import party_scent
from ..common import cycle_stage, listing, nearest
from .content import HUNTER_HUTS, LODGE_DISPLAYS, VENUE_TEXTS
from .events import LodgeEventsMixin


def hut_at(stage:int) -> str:
    tier = nearest(list(HUT_STAGES.values()), stage)
    return next(hut for hut, value in HUT_STAGES.items() if value == tier)


def lodge_detail(text:str, stage:int) -> str:
    lowered = text.casefold()
    display = next((key for key, _ in LODGE_DISPLAYS if key in lowered),
                   "wall")
    return f"{hut_at(stage)}|{display}"


class LodgeMixin(LodgeEventsMixin):
    session: Any
    event: dict[str, Any]

    def offer_hut(self) -> list[str]:
        texts = VENUE_TEXTS["hut"]
        hut = hut_at(self.session.stage)
        self.event["data"].update(hut=hut, inside=False)
        return ["", HUNTER_HUTS.get(hut, HUNTER_HUTS["lodge"])["intro"],
                texts["outside"], self.options_line(texts)]

    def enter_hut(self) -> list[Message]:
        texts = VENUE_TEXTS["hut"]
        self.event["data"]["inside"] = True
        return self.continue_venue([texts["enter"]] + self.hut_lines())

    def hut_lines(self) -> list[str]:
        texts = VENUE_TEXTS["hut"]
        inside = self.located("lodge")
        if not inside:
            return [texts["empty"]]
        displays = dict(LODGE_DISPLAYS)

        def display(entry:dict[str, Any]) -> str:
            key = entry.get("detail", "lodge|wall").split("|")[-1]
            return displays.get(key, "a trophy on the wall")

        lines = listing(inside, texts["display"], texts["more"],
                        display=display)
        return lines + self.own_lines(inside, texts["own"])

    def hut_search(self, player:Player, now:float) -> list[Message]:
        texts = VENUE_TEXTS["hut"]
        self.event["used"].add("search")
        scent = party_scent(self.session.party)
        risk = HUT_SEARCH_RISK + scent * SCENT_HUNTER_RISK
        if random.random() < risk:
            return self.reginald_returns(player, "search", now)
        roll = random.choice(("gold", "gold", "item", "journal"))
        if roll == "item":
            item_id = random.choice(BONUS_DROPS["hunter"])
            lines = [texts["search_item"].format(name=player.name),
                     give_item(player, item_id)]
        elif roll == "journal":
            lines = [texts["search_journal"].format(name=player.name)]
            lines += [texts["journal_line"].format(
                hut=HUNTER_HUTS[key]["name"], stage=stage)
                for key, stage in HUT_STAGES.items()]
        else:
            gold = HUT_SEARCH_GOLD + self.session.stage * HUT_SEARCH_GOLD_STEP
            player.gold += gold
            lines = [texts["search_gold"].format(name=player.name, gold=gold)]
        self.session.repository.save(player)
        return self.continue_venue(lines)

    def hut_cook(self, player:Player, now:float) -> list[Message]:
        texts = VENUE_TEXTS["hut"]
        self.event["used"].add("cook")
        scent = party_scent(self.session.party)
        risk = HUT_COOK_RISK + scent * SCENT_HUNTER_RISK
        if random.random() < risk:
            lines = self.reginald_returns(player, "cook", now)
            if scent:
                lines[0].text = texts["scent"] + "\n" + lines[0].text
            return lines
        cooked: list[str] = []
        for member in self.session.living():
            cooked += cook_meat(member)
            self.session.repository.save(member)
        return self.continue_venue([texts["cook"].format(
            name=player.name, food=", ".join(cooked))])

    def hut_eat(self, player:Player, now:float) -> list[Message]:
        texts = VENUE_TEXTS["hut"]
        self.event["used"].add("eat")
        scent = party_scent(self.session.party)
        risk = HUT_EAT_RISK + scent * SCENT_HUNTER_RISK
        if random.random() < risk:
            lines = self.reginald_returns(player, "eat", now)
            if scent:
                lines[0].text = texts["scent"] + "\n" + lines[0].text
            return lines
        self.heal_party(HUT_EAT_HEAL)
        for member in self.session.living():
            satisfy(member.needs, HUT_EAT_RELIEF)
        return self.continue_venue([texts["eat"].format(
            name=player.name, percent=round(HUT_EAT_HEAL * 100))])

    def hut_rest(self, player:Player, command:str,
                 now:float) -> list[Message]:
        texts = VENUE_TEXTS["hut"]
        self.event["used"].add(command)
        risk = HUT_SLEEP_RISK if command == "sleep" else HUT_REST_RISK
        scent = party_scent(self.session.party)
        risk += scent * SCENT_HUNTER_RISK
        if random.random() < risk:
            lines = self.reginald_returns(player, command, now)
            if scent:
                lines[0].text = (texts["scent"] + "\n" + lines[0].text)
            return lines
        if command == "sleep":
            self.rest_party()
            return self.continue_venue([texts["sleep"].format(
                name=player.name)])
        self.heal_party(HUT_REST_HEAL)
        for member in self.session.living():
            member.sweat //= 2
        return self.continue_venue([texts["rest"].format(
            name=player.name, percent=round(HUT_REST_HEAL * 100))])

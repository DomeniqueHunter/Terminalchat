import random
from typing import Any

from ...config import (
    CAMP_AMBUSH_COLD, CAMP_AMBUSH_FIRE, CAMP_GATHER_CHANCE,
    CAMP_GATHER_HURT, CAMP_GATHER_LOSS, CAMP_GATHER_MAX, CAMP_LIGHT_BASE,
    CAMP_LIGHT_MAX, CAMP_LIGHT_STEP, CAMP_REST_HEAL_COLD,
    CAMP_REST_HEAL_FIRE, CAMP_SLEEP_COLD,
)
from ...dungeon import give_item
from ...formulas import max_hp
from ...items import remove_item
from ...models import Message, Player
from ...needs import satisfy
from ...party_talk import banter
from ..butcher.location import cook_meat
from .content import VENUE_TEXTS


WOOD = "firewood"


def wood_holder(members:list[Player]) -> Player | None:
    for member in members:
        if WOOD in member.inventory:
            return member
    return None


def light_chance(members:list[Player]) -> float:
    best = max((member.stats["agility"] + member.stats["intelligence"]
                for member in members), default=0)
    return min(CAMP_LIGHT_BASE + best * CAMP_LIGHT_STEP, CAMP_LIGHT_MAX)


class BivouacMixin:
    session: Any
    event: dict[str, Any]

    def offer_bivouac(self) -> list[str]:
        texts = VENUE_TEXTS["bivouac"]
        self.event["data"]["lit"] = False
        self.event["data"]["gathered"] = []
        return ["", texts["intro"], self.options_line(texts)]

    def bivouac_options(self) -> list[str]:
        data = self.event["data"]
        living = self.session.living()
        options: list[str] = []
        if data["lit"]:
            if self.party_has_raw_meat():
                options.append("cook")
            if "talk" not in self.event["used"]:
                options.append("talk")
        else:
            if any(member.name not in data["gathered"]
                   for member in living):
                options.append("gather")
            if wood_holder(living) is not None:
                options.append("light")
        return options + ["rest", "depart"]

    def bivouac_action(self, player:Player, command:str,
                       now:float) -> list[Message]:
        if command == "gather":
            return self.bivouac_gather(player)
        if command == "light":
            return self.bivouac_light(player)
        if command == "cook":
            return self.bivouac_cook(player)
        if command == "talk":
            return self.bivouac_talk(player)
        return self.bivouac_rest(player, now)

    def bivouac_gather(self, player:Player) -> list[Message]:
        texts = VENUE_TEXTS["bivouac"]
        data = self.event["data"]
        values = {"name": player.name}
        if player.name in data["gathered"]:
            return [Message(texts["gather_done"].format(**values),
                            player.name)]
        if len(player.inventory) >= player.bag_size:
            return [Message(texts["gather_full"].format(**values),
                            player.name)]
        data["gathered"].append(player.name)
        if random.random() > CAMP_GATHER_CHANCE:
            return self.continue_venue(
                [texts["gather_none"].format(**values)])
        count = random.randint(1, CAMP_GATHER_MAX)
        count = min(count, player.bag_size - len(player.inventory))
        lines: list[str] = []
        for _ in range(count):
            lines.append(give_item(player, WOOD))
        key = "gather_ok"
        if random.random() < CAMP_GATHER_HURT:
            loss = min(player.hp - 1,
                       max(1, round(max_hp(player) * CAMP_GATHER_LOSS)))
            player.hp -= loss
            values["loss"] = loss
            key = "gather_hurt"
        values["count"] = count
        self.session.repository.save(player)
        return self.continue_venue([texts[key].format(**values)] + lines)

    def bivouac_light(self, player:Player) -> list[Message]:
        texts = VENUE_TEXTS["bivouac"]
        data = self.event["data"]
        holder = wood_holder(self.session.living())
        if holder is None:
            return [Message(texts["no_wood"], player.name)]
        if data["lit"]:
            return [Message(texts["lit"], player.name)]
        remove_item(holder.inventory, WOOD)
        self.session.repository.save(holder)
        if random.random() < light_chance(self.session.living()):
            data["lit"] = True
            return self.continue_venue([texts["light_ok"].format(
                name=player.name)])
        return self.continue_venue([texts["light_fail"].format(
            name=player.name)])

    def bivouac_cook(self, player:Player) -> list[Message]:
        texts = VENUE_TEXTS["bivouac"]
        cooked: list[str] = []
        for member in self.session.living():
            cooked += cook_meat(member)
            self.session.repository.save(member)
        return self.continue_venue([texts["cook"].format(
            name=player.name, food=", ".join(cooked))])

    def bivouac_talk(self, player:Player) -> list[Message]:
        texts = VENUE_TEXTS["bivouac"]
        self.event["used"].add("talk")
        others = [member for member in self.session.living()
                  if member is not player]
        if not others:
            return self.continue_venue([texts["talk_solo"].format(
                name=player.name)])
        lines: list[str] = []
        for other in others:
            lines += [message.text for message in banter(
                player, other, "", random.Random())]
            self.session.repository.save(other)
        self.session.repository.save(player)
        return self.continue_venue(lines)

    def bivouac_rest(self, player:Player, now:float) -> list[Message]:
        texts = VENUE_TEXTS["bivouac"]
        lit = self.event["data"]["lit"]
        chance = CAMP_AMBUSH_FIRE if lit else CAMP_AMBUSH_COLD
        if random.random() < chance:
            return self.finish([texts["ambush_fire" if lit
                                       else "ambush_cold"]], now)
        heal = CAMP_REST_HEAL_FIRE if lit else CAMP_REST_HEAL_COLD
        self.heal_party(heal)
        for member in self.session.living():
            member.sweat //= 2
            satisfy(member.needs,
                    {"sleep": -100 if lit else CAMP_SLEEP_COLD})
        self.save_party()
        return self.finish([texts["rest_fire" if lit else "rest_cold"]
                            .format(percent=round(heal * 100))], now)

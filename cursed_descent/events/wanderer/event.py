import random
from typing import Any

from ...config import (
    DEFAULT_GENDER, HUNG_GENDERS, HUNG_TRAITS, MILK_BUSTS, PRONOUNS,
    ROUND_TIMEOUT_SECONDS, WANDERER_EXP, WANDERER_GOLD_BASE,
    WANDERER_GOLD_PER_STAGE, WANDERER_HEAL, WANDERER_LOVE_REROLLS,
    WANDERER_MILK_GOLD, WANDERER_MILK_PER_STAGE, WANDERER_NURSE_HEAL,
    WANDERER_RARE_BONUS, WANDERER_THANKS_EXP, WANDERER_THEFT_CHANCE,
    WANDERER_THEFT_SHARE,
)
from ...content import ITEMS
from ...dungeon import find_inventory_item, give_item, grant_exp, roll_item
from ...formulas import max_hp, max_mana
from ...items import remove_item
from ...locations.butcher.location import cook_meat
from ...models import Message, Player
from ..common import options_text
from .content import EVENT_TEXTS, WANDERERS, WANDERER_THANKS, WEAR_TEXTS


THIRSTY_OPTIONS = ("milk", "nurse")


WANDERER_OPTIONS = ("sit", "give", "sleep", "depart")


def wear_lines(item:dict[str, Any], wanderer:str) -> list[str]:
    values = {"wanderer": wanderer, "item": item["name"]}
    lines: list[str] = []
    pool = WEAR_TEXTS.get(item["slot"])
    if pool:
        lines.append(random.choice(pool).format(**values))
    victim = item.get("made_from")
    if victim:
        label = item["name"].split()[-1].lower()
        lines.append(random.choice(WEAR_TEXTS["couture"]).format(
            victim=victim, label=label, **values))
    return lines


def well_hung(player:Player) -> bool:
    traits = set(player.enhancements) | set(player.buffs)
    return (player.gender in HUNG_GENDERS
            and bool(traits & set(HUNG_TRAITS)))


class WandererMixin:
    session: Any
    event: dict[str, Any]

    def offer_wanderer(self) -> list[str]:
        texts = EVENT_TEXTS["wanderer"]
        stage = self.session.stage
        gold = WANDERER_GOLD_BASE + stage * WANDERER_GOLD_PER_STAGE
        name, description, likes, *rest = random.choice(WANDERERS)
        thirsty = bool(rest and rest[0])
        self.event["phase"] = "camp"
        self.event["data"].update(wanderer=name, gold=gold, likes=likes,
                                  thirsty=thirsty)
        lines = ["", texts["intro"].format(wanderer=name,
                                           description=description,
                                           gold=gold)]
        if thirsty:
            lines.append(texts["thirsty"].format(wanderer=name))
        lines += self.offer_sweaty(name)
        return lines + [texts["options"].format(
            options=options_text(self.available()),
            seconds=int(ROUND_TIMEOUT_SECONDS))]

    def party_has_raw_meat(self) -> bool:
        return any(ITEMS[item_id].get("raw_meat")
                   for member in self.session.living()
                   for item_id in member.inventory)

    def cook_action(self, player:Player) -> list[Message]:
        texts = EVENT_TEXTS["wanderer"]
        data = self.event["data"]
        cooked: list[str] = []
        for member in self.session.living():
            cooked += cook_meat(member)
            self.session.repository.save(member)
        lines = [texts["cook"].format(name=player.name,
                                      wanderer=data["wanderer"],
                                      food=", ".join(cooked))]
        return self.continue_event(lines)

    def thirst_action(self, player:Player, command:str) -> list[Message]:
        texts = EVENT_TEXTS["wanderer"]
        data = self.event["data"]
        _, them, their_word = PRONOUNS.get(player.gender,
                                           PRONOUNS[DEFAULT_GENDER])
        stage = self.session.stage
        gold = WANDERER_MILK_GOLD + stage * WANDERER_MILK_PER_STAGE
        values = {"name": player.name, "wanderer": data["wanderer"],
                  "them": them, "their": their_word, "gold": gold}
        busty = player.body.get(
            "breasts_real", player.body["breasts"]) in MILK_BUSTS
        if not busty and not well_hung(player):
            return [Message(texts["dry"].format(**values), player.name)]
        self.event["used"].add(command)
        player.gold += gold
        key = command if busty else f"{command}_hung"
        lines = [texts[key].format(**values)]
        if command == "milk":
            bottle = "milk_bottle" if busty else "moonshine"
            lines.append(give_item(player, bottle))
        elif command == "nurse":
            self.heal_party(WANDERER_NURSE_HEAL)
            lines.append(f"The party, oddly moved, heals "
                         f"{round(WANDERER_NURSE_HEAL * 100)}% HP.")
        self.session.repository.save(player)
        return self.continue_event(lines)

    def thanks_action(self, player:Player, command:str) -> list[Message]:
        data = self.event["data"]
        offer = data["offer"]
        values = {"name": player.name, "wanderer": data["wanderer"],
                  "target": offer["player"]}
        if player.name != offer["player"]:
            return [Message(WANDERER_THANKS["not_you"].format(**values),
                            player.name)]
        del data["offer"]
        if command == "decline":
            return self.continue_event([WANDERER_THANKS["decline"].format(
                **values)])
        amount = self.session.stage * WANDERER_THANKS_EXP
        player.hp = max_hp(player)
        player.mana = max_mana(player)
        lines = [WANDERER_THANKS[offer["slot"]]["accept"].format(**values),
                 WANDERER_THANKS["reward"].format(exp=amount, **values)]
        lines += grant_exp(player, amount)
        self.session.repository.save(player)
        return self.continue_event(lines)

    def take_offering(self, player:Player,
                      reference:str) -> tuple[str | None, bool]:
        slot = reference.casefold()
        if slot in player.equipment:
            item_id = player.equipment[slot]
            if item_id is None:
                return None, False
            player.equipment[slot] = None
            player.hp = min(player.hp, max_hp(player))
            player.mana = min(player.mana, max_mana(player))
            return item_id, True
        item_id = find_inventory_item(player, reference)
        if item_id is None:
            return None, False
        remove_item(player.inventory, item_id)
        return item_id, False

    def give_item(self, player:Player, reference:str) -> list[Message]:
        texts = EVENT_TEXTS["wanderer"]
        data = self.event["data"]
        item_id, worn = self.take_offering(player, reference)
        values = {"name": player.name, "wanderer": data["wanderer"]}
        if item_id is None:
            return [Message(texts["no_item"].format(**values), player.name)]
        item = ITEMS[item_id]
        tags = {item["slot"]}
        if item.get("allure"):
            tags.add("allure")
        if worn:
            tags.add("worn")
        score = len(tags & set(data["likes"]))
        values["item"] = item["name"]
        self.event["used"].add("give")
        stage = self.session.stage
        if item["rarity"] in ("epic", "cursed", "couture"):
            stage += WANDERER_RARE_BONUS
        lines = [texts["worn"].format(**values)] if worn else []
        if score == 0:
            lines.append(texts["item_meh"].format(**values))
            gift = roll_item(stage, equipment_chance=0.0)
        elif score == 1:
            lines.append(texts["item_like"].format(**values))
            gift = roll_item(stage + 10, equipment_chance=0.6)
        else:
            lines.append(texts["item_love"].format(**values))
            gift = roll_item(stage + 20 + score * 3, equipment_chance=0.9)
            for _ in range(WANDERER_LOVE_REROLLS):
                if ITEMS[gift]["rarity"] != "common":
                    break
                gift = roll_item(stage + 20 + score * 3,
                                 equipment_chance=0.9)
        lines += wear_lines(item, data["wanderer"])
        lines.append(give_item(player, gift))
        if item["slot"] in WANDERER_THANKS:
            data["offer"] = {"player": player.name, "slot": item["slot"]}
            lines.append(WANDERER_THANKS[item["slot"]]["offer"].format(
                **values))
        self.session.repository.save(player)
        return self.continue_event(lines)

    def wanderer_action(self, player:Player, command:str,
                        now:float) -> list[Message]:
        texts = EVENT_TEXTS["wanderer"]
        data = self.event["data"]
        values = {"name": player.name, "wanderer": data["wanderer"],
                  "gold": data["gold"]}
        stage = self.session.stage
        if command == "depart":
            self.save_party()
            return self.finish([texts["depart"].format(**values)], now)
        if command == "give" and player.gold < data["gold"]:
            return [Message(texts["broke"].format(have=player.gold,
                                                  **values), player.name)]
        self.event["used"].add(command)
        if command == "sleep":
            self.rest_party()
            lines = [texts["sleep"].format(**values)]
            if random.random() < WANDERER_THEFT_CHANCE and player.gold:
                stolen = max(1, round(player.gold * WANDERER_THEFT_SHARE))
                player.gold -= stolen
                lines.append(texts["theft"].format(stolen=stolen, **values))
            self.save_party()
            return self.finish(lines, now)
        if command == "give":
            player.gold -= data["gold"]
            gift = roll_item(stage + 10, equipment_chance=0.6)
            lines = [texts["give"].format(**values), give_item(player, gift)]
        else:
            self.heal_party(WANDERER_HEAL)
            amount = stage * WANDERER_EXP
            lines = [texts["sit"].format(percent=round(WANDERER_HEAL * 100),
                                         exp=amount, **values)]
            lines += self.grant_party_exp(amount)
        return self.continue_event(lines)

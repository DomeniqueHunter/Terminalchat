import random
from types import SimpleNamespace
from typing import Any

from ...items import Item
from ...body import apply_body_mods, fake_amount
from ...content import ITEMS
from ...formulas import max_hp, max_mana
from ...intimacy import conception
from ...models import Message, Player
from ...needs_runtime import rest_needs
from ..shop.location import base_price
from ...settings import get
from .content import (
    AFTER, ENCHANT_BONUS, ENCHANT_PRICE, IMPLANT_SHARE, LIFT, MAGE_ID,
    MOAN_EARLY, MOAN_MID, MOAN_PEAK, MOCK, PART_WORDS,
    POTION_MARKUP, POTIONS, REAL_PRICE, REAL_SEX_PRICE, SCENE, SLEEP_PRICE,
    SUPER_BONUS, SUPER_PRICE, VENUE_TEXTS,
)
from . import enchantments as items


def implant_parts(player:Player) -> list[str]:
    body = player.body
    return [part for part in PART_WORDS
            if body.get(part, 0) > 0
            and fake_amount(body, part) / body[part] > IMPLANT_SHARE]


def sex_lines(player:Player) -> list[str]:
    name = player.name
    return [random.choice(LIFT).format(name=name),
            random.choice(SCENE).format(name=name),
            random.choice(MOAN_EARLY).format(name=name),
            random.choice(MOAN_MID).format(name=name),
            random.choice(MOAN_PEAK).format(name=name)]



def after_sex(player:Player) -> list[str]:
    mage = SimpleNamespace(gender="Male", name=get("mage_tower")["owner"], id=MAGE_ID)
    return [random.choice(AFTER)] + conception(mage, player, random, 1.0)


class MageTowerMixin:
    session: Any
    event: dict[str, Any]

    def offer_mage_tower(self) -> list[str]:
        texts = VENUE_TEXTS["mage_tower"]
        self.event["data"]["inside"] = False
        return ["", texts["intro"], texts["door"], self.options_line(texts)]

    def enter_mage_tower(self) -> list[Message]:
        self.event["data"]["inside"] = True
        texts = VENUE_TEXTS["mage_tower"]
        lines = [texts["enter"]]
        mocked = False
        for member in self.session.living():
            for part in implant_parts(member):
                lines.append(random.choice(MOCK[part]).format(
                    name=member.name))
                mocked = True
        if mocked:
            lines.append(texts["offer"].format(price=REAL_PRICE))
        return self.continue_venue(lines)

    def mage_tower_options(self) -> list[str]:
        options = ["upgrade", "super", "potion"]
        if any(implant_parts(member) for member in self.session.living()):
            options += ["real", "realsex"]
        if "sleep" not in self.event["used"]:
            options.append("sleep")
        return options + ["depart"]

    def mage_tower_action(self, player:Player, command:str,
                          now:float) -> list[Message] | None:
        if self.outside():
            return None
        base, _, reference = command.partition(" ")
        if base in ("upgrade", "super"):
            return self.mage_upgrade(player, base, reference.strip())
        if base in ("real", "realsex"):
            return self.mage_real(player, base, reference.strip())
        if base == "potion":
            return self.mage_potion(player, reference.strip())
        if base == "sleep":
            return self.mage_sleep(player)
        return None

    def mage_upgrade(self, player:Player, way:str,
                     reference:str) -> list[Message]:
        texts = VENUE_TEXTS["mage_tower"]
        if "enchant" in self.event["used"]:
            return [Message(texts["once"].format(name=player.name),
                            player.name)]
        choices = items.eligible(player)
        if not choices:
            return [Message(texts["empty"].format(name=player.name),
                            player.name)]
        if not reference.isdigit() or not 1 <= int(reference) <= len(
                choices):
            return [Message(texts["empty"].format(name=player.name),
                            player.name)]
        old_id = choices[int(reference) - 1][1]
        enchant = way == "upgrade"
        cost = ENCHANT_PRICE if enchant else SUPER_PRICE
        values = {"name": player.name, "price": cost,
                  "item": ITEMS[old_id]["name"]}
        if player.gold < cost:
            return [Message(texts["poor"].format(**values), player.name)]
        player.gold -= cost
        self.event["used"].add("enchant")
        lines: list[str] = []
        effect = items.pick_effect(random) if enchant else ""
        if not enchant:
            lines += sex_lines(player)
        new_id, detail = items.create(
            player, old_id, ENCHANT_BONUS if enchant else SUPER_BONUS,
            effect, random)
        values["new"] = ITEMS[new_id]["name"]
        lines.append(texts["enchant" if enchant else "super"].format(
            **values))
        if effect:
            lines.append(texts[f"effect_{effect}"].format(
                name=player.name, **{k: v for k, v in detail.items()
                                     if k != "effect"}))
        if not enchant:
            lines += after_sex(player)
        self.session.repository.save(player)
        return self.continue_venue(lines)

    def mage_real(self, player:Player, way:str,
                  part:str) -> list[Message]:
        texts = VENUE_TEXTS["mage_tower"]
        if part not in implant_parts(player):
            return [Message(texts["real_none"].format(name=player.name),
                            player.name)]
        sex = way == "realsex"
        cost = REAL_SEX_PRICE if sex else REAL_PRICE
        if player.gold < cost:
            return [Message(texts["poor"].format(
                name=player.name, price=cost), player.name)]
        player.gold -= cost
        fake = dict(player.body.get("fake", {}))
        fake.pop(part, None)
        player.body_mods.update({"fake": fake})
        apply_body_mods(player.body, player.body_mods)
        lines = ([texts["real_sex_intro"]] + sex_lines(player)
                 if sex else [])
        lines.append(texts["real"].format(name=player.name,
                                          part=PART_WORDS[part]))
        if sex:
            lines += after_sex(player)
        self.session.repository.save(player)
        return self.continue_venue(lines)

    def mage_potion(self, player:Player, reference:str) -> list[Message]:
        texts = VENUE_TEXTS["mage_tower"]
        if not reference.isdigit() or not 1 <= int(reference) <= len(
                POTIONS):
            return self.continue_venue([])
        item_id = POTIONS[int(reference) - 1]
        cost = base_price(item_id) * POTION_MARKUP
        values = {"name": player.name, "item": ITEMS[item_id]["name"],
                  "price": cost}
        if player.gold < cost:
            return [Message(texts["poor"].format(**values), player.name)]
        if len(player.inventory) >= player.bag_size:
            return [Message(texts["full"].format(**values), player.name)]
        player.gold -= cost
        player.inventory.append(Item(item_id, creator="mage tower"))
        self.session.repository.save(player)
        return self.continue_venue([texts["potion"].format(**values)])

    def mage_sleep(self, player:Player) -> list[Message]:
        texts = VENUE_TEXTS["mage_tower"]
        if "sleep" in self.event["used"]:
            return [Message(texts["slept"], player.name)]
        if player.gold < SLEEP_PRICE:
            return [Message(texts["sleep_poor"].format(
                name=player.name, price=SLEEP_PRICE), player.name)]
        player.gold -= SLEEP_PRICE
        self.event["used"].add("sleep")
        for member in self.session.living():
            member.hp = max_hp(member)
            member.mana = max_mana(member)
            rest_needs(member)
            self.session.repository.save(member)
        return self.continue_venue([texts["sleep"]])

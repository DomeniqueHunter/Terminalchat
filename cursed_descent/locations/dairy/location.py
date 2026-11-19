import random
from typing import Any

from ...config import (
    DAIRY_COW_AGE, DAIRY_CULL_AFTER, DAIRY_CULL_CHANCE, DAIRY_FATES,
    DAIRY_HEIR_CHANCE, DAIRY_JOBS, DAIRY_LEVEL_BONUS, DAIRY_LEVEL_STEP,
    DAIRY_PRODUCT_CHANCE, DAIRY_PRODUCT_JOB, DAIRY_SHELF_NAMED,
    DAIRY_STAGE_PAY, DAIRY_STAMINA_BASE, DAIRY_STAMINA_PER_VIT,
    DAIRY_STAMINA_SWING, HUNG_GENDERS, MILK_BUSTS, PRONOUNS, DEFAULT_GENDER,
)
from ...content import BUFFS, ITEMS
from ...dungeon import give_item
from ...formulas import apply_buff, set_bonus_text
from ...models import Message, Player
from ..butcher.location import meat_profile
from .content import BREED_NAMES, PRODUCTS, SERVE_TEXTS, VENUE_TEXTS


MENU = ("dairy_milk", "dairy_cream", "dairy_cheese", "dairy_butter",
        "dairy_tonic")
JOB_FATES = {"cow": "milked_dry", "bull": "bull_stud"}
SHIFT_KEY = "dairy_shifts"


def product_id(entry:dict[str, Any]) -> str:
    slug = "".join(char for char in entry["name"].casefold()
                   if char.isalnum())
    return f"dairy_p_{slug}_{entry['fate']}_{entry.get('stage', 0)}"


def product_kind(entry:dict[str, Any]) -> str:
    kinds = BREED_NAMES[entry["fate"]]
    seed = entry["name"] + str(entry.get("stage", 0))
    return kinds[sum(ord(char) for char in seed) % len(kinds)]


def dairy_entries(entries:list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [entry for entry in entries
            if entry["fate"] in DAIRY_FATES]


def register_product(entry:dict[str, Any]) -> str:
    kind = product_kind(entry)
    spec = PRODUCTS[kind]
    base = ITEMS[spec["base"]]
    victim = entry.get("victim", {})
    factor = 1.5 + victim.get("level", 1) // DAIRY_LEVEL_STEP * (
        DAIRY_LEVEL_BONUS)
    item = {"name": spec["name"].format(name=entry["name"]),
            "slot": "consumable", "rarity": "rare",
            "price": round(base["price"] * factor), "no_loot": True,
            "note": spec["note"].format(name=entry["name"])}
    for stat in ("heal", "mana"):
        if base.get(stat):
            item[stat] = round(base[stat] * factor)
    if base.get("needs"):
        item["needs"] = dict(base["needs"])
    item_id = product_id(entry)
    ITEMS[item_id] = item
    return item_id


def register_all_dairy(entries:list[dict[str, Any]]) -> None:
    for entry in dairy_entries(entries):
        register_product(entry)


def stamina_of(player:Player) -> int:
    return DAIRY_STAMINA_BASE + player.stats["vitality"] * (
        DAIRY_STAMINA_PER_VIT)


def can_cow(player:Player) -> bool:
    real = player.body.get("breasts_real", player.body["breasts"])
    return real in MILK_BUSTS


def can_bull(player:Player) -> bool:
    return player.gender in HUNG_GENDERS


def values_of(player:Player) -> dict[str, str]:
    they, them, their = PRONOUNS.get(player.gender, PRONOUNS[DEFAULT_GENDER])
    return {"name": player.name, "they": they, "them": them,
            "their": their, "Their": their.capitalize()}


class DairyMixin:
    session: Any
    event: dict[str, Any]

    def dairy_entries(self) -> list[dict[str, Any]]:
        return dairy_entries(self.session.remains.entries)

    def dairy_named(self) -> list[str]:
        ids: list[str] = []
        seen: set[str] = set()
        for entry in reversed(self.dairy_entries()):
            if entry["name"] in seen:
                continue
            seen.add(entry["name"])
            item_id = product_id(entry)
            if item_id not in ITEMS:
                register_product(entry)
            ids.append(item_id)
            if len(ids) >= DAIRY_SHELF_NAMED:
                break
        return [item_id for item_id in ids
                if item_id not in self.event["used"]]

    def dairy_stock(self) -> list[str]:
        return list(MENU) + self.dairy_named()

    def offer_dairy(self) -> list[str]:
        texts = VENUE_TEXTS["dairy"]
        self.event["data"]["inside"] = False
        return ["", texts["intro"], texts["door"], self.options_line(texts)]

    def enter_dairy(self) -> list[Message]:
        texts = VENUE_TEXTS["dairy"]
        self.event["data"]["inside"] = True
        return self.continue_venue([texts["enter"], texts["mother"]])

    def dairy_options(self) -> list[str]:
        buys = [f"buy {nr}" for nr, _, _ in self.venue_stock()]
        serves = [f"stint {job}" for job in DAIRY_JOBS]
        return buys + serves + ["tour", "sellself", "depart"]

    def dairy_examine(self) -> list[Message]:
        texts = VENUE_TEXTS["dairy"]
        if self.outside():
            return [Message(texts["look_outside"])]
        entries = self.dairy_entries()
        lines = [texts["look"]]
        if entries:
            lines.append(texts["look_herd"])
            shown: set[str] = set()
            for entry in reversed(entries):
                if entry["name"] in shown or len(shown) >= 4:
                    continue
                shown.add(entry["name"])
                key = {"milked_dry": "look_cow", "bull_stud": "look_bull",
                       "culled": "look_cull"}[entry["fate"]]
                victim = entry.get("victim", {})
                desc = (f"{victim.get('build', 'Average').lower()} build, "
                        f"{victim.get('breasts', 'Medium').lower()} bust")
                lines.append(texts[key].format(
                    nr=len(shown), name=entry["name"], desc=desc))
        else:
            lines.append(texts["look_empty"])
        lines.append(texts["mother"])
        return [Message("\n".join(lines))]

    def dairy_action(self, player:Player, command:str,
                     now:float) -> list[Message] | None:
        word = command.split()[0]
        if word == "tour":
            return self.dairy_tour(player)
        if word == "stint":
            parts = command.split()
            return self.dairy_serve(player, parts[1] if len(parts) > 1
                                    else "")
        if word == "sellself":
            return self.dairy_sell_self(player)
        return None

    def dairy_tour(self, player:Player) -> list[Message]:
        texts = VENUE_TEXTS["dairy"]
        step = self.event["data"].get("tour", 0)
        if step > len(texts["tour"]):
            return [Message(texts["tour_used"].format(name=player.name),
                            player.name)]
        self.event["data"]["tour"] = step + 1
        if step == len(texts["tour"]):
            return self.continue_venue([texts["tour_end"]])
        lines = [texts["tour_start"]] if step == 0 else []
        return self.continue_venue(lines + [texts["tour"][step]])

    def dairy_age(self, player:Player) -> list[str]:
        if player.age >= DAIRY_COW_AGE[0]:
            return []
        player.age = random.randint(*DAIRY_COW_AGE)
        return [VENUE_TEXTS["dairy"]["aging"].format(name=player.name,
                                                     age=player.age)]

    def dairy_serve(self, player:Player, job:str) -> list[Message]:
        texts = VENUE_TEXTS["dairy"]
        if job not in DAIRY_JOBS:
            return [Message(texts["serve_busy"].format(name=player.name),
                            player.name)]
        key = f"serve:{player.name}"
        if key in self.event["used"]:
            return [Message(texts["serve_busy"].format(name=player.name),
                            player.name)]
        if job == "cow" and not can_cow(player):
            return [Message(texts["serve_no_cow"].format(name=player.name),
                            player.name)]
        if job == "bull" and not can_bull(player):
            return [Message(texts["serve_no_bull"].format(name=player.name),
                            player.name)]
        self.event["used"].add(key)
        lines = self.dairy_age(player) if job == "cow" else []
        spec = DAIRY_JOBS[job]
        values = values_of(player)
        lines.append(SERVE_TEXTS[job]["start"].format(**values))
        stamina = stamina_of(player)
        maximum = stamina
        pay = round(spec["pay"] * (1 + self.session.stage * DAIRY_STAGE_PAY))
        earned = 0
        for turn in range(1, spec["rounds"] + 1):
            earned += pay
            lines.append(random.choice(SERVE_TEXTS[job]["turn"]).format(
                **values))
            if spec["drain"]:
                stamina -= spec["drain"] + random.randint(
                    *DAIRY_STAMINA_SWING)
            lines.append(texts["round"].format(
                name=player.name, turn=turn, turns=spec["rounds"],
                stamina=max(0, stamina), maximum=maximum, gold=earned))
            if stamina <= 0:
                player.gold += earned // 2
                return self.dairy_collapse(player, job, lines)
        shifts = player.records.get(SHIFT_KEY, 0) + 1
        player.records[SHIFT_KEY] = shifts
        if (job in JOB_FATES and shifts > DAIRY_CULL_AFTER
                and random.random() < DAIRY_CULL_CHANCE):
            lines.append(texts["cull"].format(name=player.name))
            return self.dairy_end(player, "culled", lines)
        player.gold += earned
        buff = spec["buff"]
        apply_buff(player, buff)
        bonus = set_bonus_text(BUFFS[buff])
        lines.append(texts["done"].format(their=values["their"],
                                          bonus=bonus, name=player.name))
        lines += self.dairy_reward(player, job)
        self.session.repository.save(player)
        return self.continue_venue(lines)

    def dairy_reward(self, player:Player, job:str) -> list[str]:
        texts = VENUE_TEXTS["dairy"]
        lines: list[str] = []
        if random.random() < DAIRY_PRODUCT_CHANCE:
            lines += [texts["product"],
                      give_item(player, DAIRY_PRODUCT_JOB[job])]
        if (job == "cow" and not player.records.get("dairy_heir")
                and random.random() < DAIRY_HEIR_CHANCE):
            player.records["dairy_heir"] = True
            apply_buff(player, "dairy_heir")
            lines.append(texts["heir"].format(
                name=player.name,
                bonus=set_bonus_text(BUFFS["dairy_heir"])))
        return lines

    def dairy_collapse(self, player:Player, job:str,
                       lines:list[str]) -> list[Message]:
        texts = VENUE_TEXTS["dairy"]
        if job in JOB_FATES:
            return self.dairy_end(player, JOB_FATES[job], lines)
        player.hp = 1
        lines.append(texts["faint"].format(**values_of(player)))
        self.session.repository.save(player)
        return self.continue_venue(lines)

    def dairy_end(self, player:Player, fate:str,
                  lines:list[str]) -> list[Message]:
        from ...combat import fate_text
        session = self.session
        text = fate_text(player, fate, None)
        lines += session.kill_outside(
            player, fate, text, "<<npc.odile_first>>", "dairy", "dairy")
        register_all_dairy(session.remains.entries[-1:])
        return self.dairy_after(lines)

    def dairy_after(self, lines:list[str]) -> list[Message]:
        session = self.session
        if not session.living():
            self.reset()
            return [Message("\n".join(lines + session.end_run()))]
        self.save_party()
        return self.continue_venue(lines)

    def dairy_sell_self(self, player:Player) -> list[Message]:
        from ...events.common import self_price
        texts = VENUE_TEXTS["dairy"]
        options = [job for job, ok in (("cow", can_cow(player)),
                                       ("bull", can_bull(player))) if ok]
        if not options:
            return [Message(texts["sellself_no"].format(name=player.name),
                            player.name)]
        job = random.choice(options)
        values = values_of(player)
        gold = self_price(player)
        player.gold += gold
        lines = [texts["sellself"].format(gold=gold, **values)]
        if job == "cow":
            lines += self.dairy_age(player)
        return self.dairy_end(player, JOB_FATES[job], lines)

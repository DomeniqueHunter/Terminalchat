import random
import uuid
from pathlib import Path
from typing import Any

from ...clock import timestamp
from ...body import DEFAULT_BALLS, shape_of
from ...config import (
    ASTRID_VISIT_CHANCE, ASTRID_VISIT_PRICE, ASTRID_VISIT_TAKE,
    BURDEN_BUILDS, BURDEN_MIN_BALLS, BURDEN_PAIN, BURDEN_PAY,
    BURDEN_STAMINA_BASE, BURDEN_STAMINA_LOSS, BURDEN_STAMINA_VIT_STEP,
    CUM_COW_CHANCE, CUM_COW_MIN_BALLS, CUM_EQUINE_YIELD, CUM_YIELD_BY_BALLS,
    FARM_FILE_NAME, FARM_KEEP_BASE, FARM_KEEP_JOB, FARM_KEEP_MAX,
    FARM_KEEP_STEP, FARM_PRODUCT_BUST, FARM_PRODUCT_FACTOR,
    FARM_PRODUCT_LEVEL_BONUS, FARM_PRODUCT_LEVEL_STEP, FARM_SHIFT_PAY,
    FARM_SHIFT_STAGE_PAY, FARM_SHIFT_TURNS, FARM_STALLION_PAY,
    FARM_STALLION_PRODUCT, HUNG_GENDERS, MILK_BUSTS, RENT_JOBS,
    SCENT_FARM_INTEREST,
)
from ...content import ITEMS
from ...formulas import max_hp
from ...models import Message, Player
from ...storage import read_json, write_json
from ...sweat import sweat_tier
from ..common import listing, unique_names
from .content import (
    BURDEN_TIRED, BURDEN_TURNS, CUM_SCENTS, FARM_JOBS, FARM_PRODUCTS, FARM_PRODUCT_NOTES,
    BURDEN_ENDS, END_BATCHES, END_KILLERS, FARM_BAD_ENDS,
    FARM_SHIFT_TEXTS, HEN_AIDS, HEN_LAYING, VENUE_TEXTS,
)
from .events import FarmEventsMixin, pronoun_values
from .npc import FarmNpcMixin


def keep_chance(shift:dict[str, Any], player:Player) -> float:
    chance = (FARM_KEEP_BASE + FARM_KEEP_STEP * shift["turn"]
              + shift["interest"]
              + sweat_tier(player) * SCENT_FARM_INTEREST
              ) * FARM_KEEP_JOB[shift["job"]]
    return min(chance, FARM_KEEP_MAX)


def product_id(source:str, entry_id:str) -> str:
    return f"farm_{source}_{entry_id}"


def register_product(item_id:str, name:str, job:str, source:str,
                     victim:dict[str, Any]) -> None:
    stallion = victim.get("shape") == "Equine" and job == "plough"
    stud = victim.get("shape") == "Equine" and job == "cum"
    product = FARM_PRODUCTS["stallion" if stallion else job] if (
        stallion or job in FARM_PRODUCTS) else FARM_PRODUCTS["field"]
    base = ITEMS[product["base"]]
    factor = FARM_PRODUCT_FACTOR[source]
    if stallion or stud:
        factor += FARM_STALLION_PRODUCT
    factor += victim.get("level", 1) // FARM_PRODUCT_LEVEL_STEP * (
        FARM_PRODUCT_LEVEL_BONUS)
    if job == "milk":
        factor += FARM_PRODUCT_BUST.get(victim.get("breasts", ""), 0.0)
    item = {"name": product["name"].format(name=name),
            "slot": "consumable",
            "rarity": "rare" if source == "kept" else "common",
            "price": round(base["price"] * factor), "no_loot": True,
            "note": FARM_PRODUCT_NOTES[source].format(name=name)}
    for stat in ("heal", "mana"):
        if base.get(stat):
            item[stat] = round(base[stat] * factor)
    ITEMS[item_id] = item


def register_all_products(remains:list[dict[str, Any]],
                          batches:list[dict[str, Any]]) -> None:
    for entry in remains:
        if entry["fate"] == "farmed":
            register_product(product_id("kept", entry["id"]), entry["name"],
                             entry.get("detail", "field"), "kept",
                             entry.get("victim", {}))
    for batch in batches:
        register_product(product_id("shift", batch["id"]), batch["name"],
                         batch["job"], "shift", batch["victim"])


class FarmLedger:
    def __init__(self, data_path:Path) -> None:
        self.path = data_path / FARM_FILE_NAME
        self.entries: list[dict[str, Any]] = read_json(self.path, [])

    def save(self) -> None:
        write_json(self.path, self.entries)

    def add(self, player:Player, job:str, location:int, count:int,
            victim:dict[str, Any]) -> str:
        batch_id = uuid.uuid4().hex
        self.entries.append({
            "id": batch_id, "name": player.name, "job": job,
            "location": location, "left": count, "victim": victim,
            "date": timestamp(),
        })
        register_product(product_id("shift", batch_id), player.name, job,
                         "shift", victim)
        self.save()
        return product_id("shift", batch_id)

    def take(self, item_id:str) -> None:
        for entry in self.entries:
            if product_id("shift", entry["id"]) == item_id:
                entry["left"] -= 1
        self.entries = [entry for entry in self.entries if entry["left"] > 0]
        self.save()


def balls_size(player:Player) -> float:
    return player.body.get("balls", DEFAULT_BALLS)


def cum_factor(player:Player) -> float:
    size = balls_size(player)
    points = CUM_YIELD_BY_BALLS
    if size <= points[0][0]:
        factor = points[0][1]
    elif size >= points[-1][0]:
        factor = points[-1][1]
    else:
        factor = points[-1][1]
        for (low, low_value), (high, high_value) in zip(points, points[1:]):
            if low <= size <= high:
                share = (size - low) / (high - low)
                factor = low_value + share * (high_value - low_value)
                break
    if shape_of(player.gender, player.body) == "Equine":
        factor *= CUM_EQUINE_YIELD
    return factor


def cum_scent(player:Player) -> str:
    shape = "Equine" if shape_of(player.gender, player.body) == "Equine" \
        else ""
    values = pronoun_values(player)
    return CUM_SCENTS[shape][sweat_tier(player)].format(**values)


def burden_fit(player:Player) -> bool:
    return (player.gender in HUNG_GENDERS
            and balls_size(player) >= BURDEN_MIN_BALLS
            and player.body["build"] in BURDEN_BUILDS)


def burden_stamina(player:Player) -> int:
    return (BURDEN_STAMINA_BASE
            + player.stats["vitality"] // BURDEN_STAMINA_VIT_STEP)


def farm_end(job:str, key:str, burden:bool) -> str:
    options = (BURDEN_ENDS.get(key) if burden
               else FARM_BAD_ENDS.get((job, key)))
    return random.choice(options) if options else "farmed"


def farm_job(player:Player) -> str:
    text = player.last_fate_text.casefold()
    if "coop" in text:
        return "hen"
    if "milk cow" in text:
        return "milk"
    if "plough" in text:
        return "plough"
    if (player.gender in HUNG_GENDERS
            and balls_size(player) >= CUM_COW_MIN_BALLS
            and random.random() < CUM_COW_CHANCE):
        return "cum"
    if shape_of(player.gender, player.body) == "Equine":
        return random.choice(["plough", "carriage"])
    real = player.body.get("breasts_real", player.body["breasts"])
    if real in MILK_BUSTS:
        return "milk"
    if player.body["build"] in ("Muscular", "Heavy", "Toned"):
        return "plough"
    return random.choice(["field", "mule"])


class FarmMixin(FarmEventsMixin, FarmNpcMixin):
    session: Any
    event: dict[str, Any]

    def shifts(self) -> dict[str, dict[str, Any]]:
        return self.event.setdefault("data", {}).setdefault("shifts", {})

    def rent_options(self) -> list[str]:
        return [f"work {role}" for role in RENT_JOBS]

    def shift_options(self) -> list[str]:
        return ["work", "quit"] if self.shifts() else []

    def rent(self, player:Player, role:str) -> list[str]:
        texts = FARM_SHIFT_TEXTS
        values = pronoun_values(player)
        rented = self.event["data"].setdefault("rented", set())
        if player.name in rented:
            return [texts["again"].format(**values)]
        job = RENT_JOBS[role]
        stallion = shape_of(player.gender, player.body) == "Equine"
        if job == "milk" and player.body.get(
                "breasts_real", player.body["breasts"]) not in MILK_BUSTS:
            return [texts["no_cow"].format(**values)]
        if job == "cum" and player.gender not in HUNG_GENDERS:
            return [texts["no_cum"].format(**values)]
        burden = job in BURDEN_STAMINA_LOSS and burden_fit(player)
        if job == "carriage" and not stallion and not burden:
            return [texts["no_carriage"].format(**values)]
        turns = random.randint(*FARM_SHIFT_TURNS)
        pay = round(FARM_SHIFT_PAY[job]
                    * (1 + self.session.stage * FARM_SHIFT_STAGE_PAY))
        extra: list[str] = []
        if stallion and job in ("plough", "carriage"):
            pay = round(pay * FARM_STALLION_PAY)
            extra.append(texts["stallion"].format(**values))
        if burden:
            pay = round(pay * BURDEN_PAY)
        rented.add(player.name)
        shift = {"job": job, "turns": turns, "turn": 0, "pay": pay,
                 "earned": 0, "interest": 0.0}
        if burden:
            shift.update({"burden": True,
                          "stamina": burden_stamina(player),
                          "stamina_max": burden_stamina(player)})
        self.shifts()[player.name] = shift
        start = ("start_burden_" if burden else "start_") + job
        lines = extra + [texts["start"].format(turns=turns, role=role,
                                               pay=pay, **values),
                         texts[start].format(**values)]
        if job == "hen":
            aid = random.choice(list(HEN_AIDS))
            shift["aid"] = aid
            lines.append(random.choice(HEN_AIDS[aid]).format(**values))
        return lines

    def kept_on_farm(self, player:Player, job:str, key:str,
                     burden:bool=False) -> list[str]:
        from ...combat import fate_text
        fate = farm_end(job, key, burden)
        values = pronoun_values(player)
        if fate == "farmed":
            text = FARM_SHIFT_TEXTS[key].format(job=FARM_JOBS[job], **values)
        else:
            text = fate_text(player, fate, None)
        del self.shifts()[player.name]
        player.last_fate = fate
        player.last_fate_text = text
        killer = END_KILLERS.get(fate, "Old Trotter")
        lines = self.session.kill_outside(player, fate, text, killer,
                                          "pigmen", job)
        if fate in END_BATCHES:
            from ..butcher.location import meat_profile
            kind, count = END_BATCHES[fate]
            self.session.farm_ledger.add(player, kind, self.session.stage,
                                         count, meat_profile(player))
        return lines

    def work_turn(self, player:Player) -> list[str]:
        shift = self.shifts()[player.name]
        shift["turn"] += 1
        shift["earned"] += shift["pay"]
        lines = [FARM_SHIFT_TEXTS["turn"].format(
            name=player.name, turn=shift["turn"], turns=shift["turns"]),
            self.shift_event(player, shift)]
        if shift.get("burden"):
            lines += self.burden_turn(player, shift)
            if shift["stamina"] <= 0 and player.hp > 0:
                return lines + self.kept_on_farm(player, shift["job"],
                                                 "burden_collapse", True)
        if shift["job"] == "cum":
            lines.append(cum_scent(player))
        if shift["job"] == "hen":
            shift["eggs"] = shift.get("eggs", 0) + 1
            lines.append(random.choice(HEN_LAYING).format(
                **pronoun_values(player)))
        if player.hp <= 0:
            return lines + self.kept_on_farm(
                player, shift["job"], "collapse", bool(shift.get("burden")))
        if random.random() < keep_chance(shift, player):
            return lines + self.kept_on_farm(
                player, shift["job"], "kept", bool(shift.get("burden")))
        if shift["turn"] >= shift["turns"]:
            player.gold += shift["earned"]
            del self.shifts()[player.name]
            done = FARM_SHIFT_TEXTS["done"].format(gold=shift["earned"],
                                                   **pronoun_values(player))
            return lines + [done] + self.store_batch(player, shift,
                                                     shift["turns"])
        return lines + [FARM_SHIFT_TEXTS["status"].format(
            earned=shift["earned"],
            chance=round(keep_chance(shift, player) * 100))]

    def burden_turn(self, player:Player,
                    shift:dict[str, Any]) -> list[str]:
        hp = max(1, round(max_hp(player) * BURDEN_PAIN))
        player.hp = max(0, player.hp - hp)
        shift["stamina"] -= BURDEN_STAMINA_LOSS[shift["job"]]
        values = pronoun_values(player)
        lines = [random.choice(BURDEN_TURNS[shift["job"]]).format(
            hp=hp, **values)]
        if 0 < shift["stamina"] <= shift["stamina_max"] // 3:
            lines.append(BURDEN_TIRED[shift["job"]].format(**values))
        lines.append(FARM_SHIFT_TEXTS["burden_status"].format(
            stamina=max(0, shift["stamina"]),
            maximum=shift["stamina_max"]))
        return lines

    def quit_shift(self, player:Player) -> list[str]:
        shift = self.shifts().pop(player.name)
        gold = shift["earned"] // 2
        player.gold += gold
        text = FARM_SHIFT_TEXTS["quit"].format(gold=gold,
                                               **pronoun_values(player))
        return [text] + self.store_batch(player, shift, shift["turn"] // 2)

    def store_batch(self, player:Player, shift:dict[str, Any],
                    count:int) -> list[str]:
        if shift["job"] == "hen":
            count += shift.get("eggs", 0) // 2
        if shift["job"] == "cum":
            count = max(1, round(count * cum_factor(player))) if count else 0
        if count <= 0:
            return []
        from ..butcher.location import meat_profile
        item_id = self.session.farm_ledger.add(
            player, shift["job"], self.session.stage, count,
            meat_profile(player))
        return [FARM_SHIFT_TEXTS["batch"].format(
            count=count, item=ITEMS[item_id]["name"])]

    def farm_products(self) -> list[str]:
        from ..common import cycle_stage
        current = cycle_stage(self.session.stage)
        kept: dict[str, str] = {}
        for entry in self.located("farmed"):
            item_id = product_id("kept", entry["id"])
            if item_id not in ITEMS:
                register_product(item_id, entry["name"],
                                 entry.get("detail", "field"), "kept",
                                 entry.get("victim", {}))
            kept[entry["name"]] = item_id
        batches = [product_id("shift", entry["id"])
                   for entry in self.session.farm_ledger.entries
                   if cycle_stage(entry["location"]) == current]
        return [item_id for item_id in list(kept.values()) + batches
                if item_id in ITEMS]

    def finish_shifts(self) -> list[str]:
        lines: list[str] = []
        for name in list(self.shifts()):
            player = self.session.member(name)
            while player and name in self.shifts() and player.alive:
                lines += self.work_turn(player)
        return lines

    def shift_action(self, player:Player, command:str,
                     now:float) -> list[Message]:
        values = pronoun_values(player)
        if player.name not in self.shifts():
            return [Message(FARM_SHIFT_TEXTS["idle"].format(**values),
                            player.name)]
        if command == "quit":
            lines = self.quit_shift(player)
        else:
            lines = self.work_turn(player)
        self.session.repository.save(player)
        if not self.session.living():
            self.reset()
            return [Message("\n".join(lines + self.session.end_run()))]
        return self.continue_venue(lines)

    def shift_blocked(self, player:Player) -> list[Message]:
        names = ", ".join(self.shifts())
        return [Message(FARM_SHIFT_TEXTS["busy"].format(names=names),
                        player.name)]

    def offer_farm(self) -> list[str]:
        texts = VENUE_TEXTS["farm"]
        self.event["data"]["inside"] = False
        return ["", texts["intro"], texts["door"], self.options_line(texts)]

    def astrid_visit(self) -> list[str]:
        ledger = self.session.farm_ledger
        living = self.session.living()
        own = {member.name for member in self.session.party}
        batches = [entry for entry in ledger.entries
                   if entry.get("job") in ("cum", "milk")
                   and entry["left"] > 0 and entry["name"] not in own]
        if not batches or not living or random.random() >= (
                ASTRID_VISIT_CHANCE):
            return []
        taken = 0
        for entry in batches:
            count = min(entry["left"], ASTRID_VISIT_TAKE)
            entry["left"] -= count
            taken += count
        names = ", ".join(sorted({entry["name"] for entry in batches}))
        ledger.entries = [entry for entry in ledger.entries
                          if entry["left"] > 0]
        ledger.save()
        gold = taken * ASTRID_VISIT_PRICE
        payer = living[0]
        payer.gold += gold
        self.session.repository.save(payer)
        return [VENUE_TEXTS["farm"]["astrid"].format(
            count=taken, names=names, gold=gold, name=payer.name)]

    def enter_farm(self) -> list[Message]:
        texts = VENUE_TEXTS["farm"]
        self.event["data"]["inside"] = True
        entries = self.located("farmed")
        unique = unique_names(entries)
        lines = [texts["enter"]]
        if not unique:
            lines.append(texts["nobody"])
        lines += listing(unique, texts["worker"], texts["more"],
                         job=lambda entry: FARM_JOBS.get(
                             entry.get("detail", ""), FARM_JOBS["field"]))
        lines += self.own_lines(unique, texts["own"])
        lines += self.astrid_visit()
        return self.continue_venue(lines)

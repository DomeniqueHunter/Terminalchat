import random
import uuid
from pathlib import Path
from typing import Any

from ...body import muscle_tier, shape_of
from ...clock import timestamp
from ...config import (
    HUNG_GENDERS, SWEATERY_BOTTLE_LITERS, SWEATERY_CYCLES,
    SWEATERY_FEATURE_LIMITS, SWEATERY_FILE_NAME,
    SWEATERY_HEAT_DAMAGE, SWEATERY_LABOUR_EXP, SWEATERY_MUSCLE_BONUS,
    SWEATERY_OPERATORS, SWEATERY_PRODUCT_TIER, SWEATERY_ROAST_BASE,
    SWEATERY_ROAST_HEAL, SWEATERY_ROAST_STEP, SWEATERY_SQUEAL_CHANCE,
    SWEATERY_STAGE_PAY, SWEATERY_STATIONS, SWEATERY_TIER_BONUS,
)
from ...content import ITEMS
from ...dungeon import grant_exp
from ...formulas import max_hp
from ...models import Message, Player
from ...storage import read_json, write_json
from ...sweat import sweat_tier
from ..butcher.location import meat_grade, meat_score
from ..common import listing, pronouns, unique_names
from .content import (
    SWEATERY_FEATURES, SWEATERY_GEAR_NOTE, SWEATERY_HURT,
    SWEATERY_OPERATORS as OPERATOR_TEXTS, SWEATERY_PRODUCT_NOTE,
    SWEATERY_STATION_TEXTS, SWEATERY_TASTES, VENUE_TEXTS,
)

LEATHER_WORDS = ("leather", "wolfhide", "wyrmhide", "fur")
LOCKER_KEY = "sweatery_locker"
BOOT_SLOT = "feet"


def product_id(entry_id:str) -> str:
    return f"sweat_{entry_id}"


def roast_id(entry_id:str) -> str:
    return f"roast_{entry_id}"


def dominant_feature(player:Player) -> str:
    body = player.body
    shape = shape_of(player.gender, body)
    if shape in ("Equine", "Canine", "Draconic"):
        return shape
    hung = player.gender in HUNG_GENDERS
    values = {"breasts": body.get("bust", 0) - body.get("fake", {}).get(
        "bust", 0),
        "muscle": body.get("muscle", 0), "butt": body.get("butt", 0)}
    if hung:
        values["balls"] = body.get("balls", 0)
        values["endowment"] = body.get("endowment", 0)
    best, best_score = "plain", 0.0
    for feature, value in values.items():
        low, high = SWEATERY_FEATURE_LIMITS[feature]
        if value < low:
            continue
        score = (value - low) / (high - low)
        if score >= best_score:
            best, best_score = feature, score
    return best


def sweat_identity(player:Player, station:str,
                   operator:str) -> tuple[str, str]:
    plural = OPERATOR_TEXTS[operator]["plural"]
    smell, taste = SWEATERY_FEATURES[dominant_feature(player)]
    smell = smell.format(plural=plural)
    boots = player.equipment.get("feet")
    if boots and any(word in ITEMS[boots]["name"].casefold()
                     for word in LEATHER_WORDS):
        smell += SWEATERY_GEAR_NOTE.format(their=pronouns(player.gender)[2])
    base = SWEATERY_TASTES[station]
    return smell, f"{base}, {taste}" if taste else base


def sweat_liters(player:Player, station:str, operator:str) -> float:
    tier = muscle_tier(player.stats, player.body)
    value = SWEATERY_STATIONS[station]["liters"]
    value *= 1 + SWEATERY_MUSCLE_BONUS[tier]
    value *= 1 + sweat_tier(player) * SWEATERY_TIER_BONUS
    value *= SWEATERY_OPERATORS[operator]["yield"]
    return round(value * random.uniform(0.85, 1.15), 2)


def register_product(entry:dict[str, Any]) -> None:
    station = SWEATERY_STATIONS[entry["station"]]
    base = ITEMS[station["base"]]
    factor = 1 + entry["tier"] * SWEATERY_PRODUCT_TIER
    label = SWEATERY_STATION_TEXTS[entry["station"]]["name"]
    title = (f"Jar of {entry['name']}'s Boot Sweat" if entry.get("boots")
             else f"{entry['name']}'s {label} Sweat")
    item = {"name": title, "slot": "consumable",
            "rarity": "rare" if entry["tier"] >= 2 else "common",
            "price": round(base["price"] * factor), "no_loot": True,
            "note": SWEATERY_PRODUCT_NOTE.format(
                name=entry["name"], station=label,
                liters=f"{entry['liters']:.2f}", smell=entry["smell"],
                taste=entry["taste"])}
    for stat in ("heal", "mana"):
        if base.get(stat):
            item[stat] = round(base[stat] * factor)
    ITEMS[product_id(entry["id"])] = item


def register_roast(entry:dict[str, Any]) -> None:
    rarity, factor = meat_grade(meat_score(entry.get("victim", {})))
    ITEMS[roast_id(entry["id"])] = {
        "name": f"Roast {entry['name']}", "slot": "consumable",
        "rarity": rarity, "price": round(40 * factor), "no_loot": True,
        "heal": round(SWEATERY_ROAST_HEAL * factor),
        "note": "still hissing from the heater plate"}


def register_all(entries:list[dict[str, Any]],
                 remains:list[dict[str, Any]]) -> None:
    for entry in entries:
        register_product(entry)
    for entry in remains:
        if entry["fate"] == "heated":
            register_roast(entry)


class SweateryLedger:
    def __init__(self, data_path:Path) -> None:
        self.path = data_path / SWEATERY_FILE_NAME
        self.entries: list[dict[str, Any]] = read_json(self.path, [])

    def save(self) -> None:
        write_json(self.path, self.entries)

    def add(self, player:Player, station:str, liters:float, count:int,
            operator:str, boots:str="") -> str:
        smell, taste = sweat_identity(player, station, operator)
        entry = {"id": uuid.uuid4().hex, "name": player.name,
                 "station": station, "tier": sweat_tier(player),
                 "liters": liters, "left": count, "smell": smell,
                 "taste": taste, "date": timestamp()}
        if boots:
            entry["boots"] = boots
        self.entries.append(entry)
        register_product(entry)
        self.save()
        return product_id(entry["id"])

    def take(self, item_id:str) -> None:
        for entry in self.entries:
            if product_id(entry["id"]) == item_id:
                entry["left"] -= 1
        self.entries = [entry for entry in self.entries if entry["left"] > 0]
        self.save()


class SweateryMixin:
    session: Any
    event: dict[str, Any]

    def sweat_shifts(self) -> dict[str, dict[str, Any]]:
        return self.event.setdefault("data", {}).setdefault("sweat", {})

    def sweat_operator(self) -> str:
        return self.event["data"].get("operator", "goblin")

    def sweat_texts(self) -> dict[str, Any]:
        return OPERATOR_TEXTS[self.sweat_operator()]

    def sweatery_look(self) -> dict[str, str]:
        texts = self.sweat_texts()
        return {"owner": "", "outside": texts["look_outside"],
                "inside": texts["look_inside"]}

    def sweatery_options(self) -> list[str]:
        shifts = self.sweat_shifts()
        free = [member for member in self.session.living()
                if member.name not in shifts]
        options = [f"sweat {station}" for station in SWEATERY_STATIONS
                   ] if free else []
        if shifts:
            return options + ["work", "quit"] + [
                f"buy {nr}" for nr, _, _ in self.venue_stock()]
        return options + [f"buy {nr}" for nr, _, _ in self.venue_stock()
                          ] + ["depart"]

    def sweatery_stock(self) -> list[str]:
        products = [product_id(entry["id"])
                    for entry in self.session.sweatery_ledger.entries]
        roasts = []
        for entry in self.located("heated"):
            if roast_id(entry["id"]) not in ITEMS:
                register_roast(entry)
            roasts.append(roast_id(entry["id"]))
        return [item_id for item_id in products + roasts
                if item_id in ITEMS and item_id not in self.event["used"]]

    def sweatery_bought(self, item_id:str) -> None:
        if item_id.startswith("sweat_"):
            self.session.sweatery_ledger.take(item_id)
        else:
            self.event["used"].add(item_id)

    def sweat_status(self) -> list[str]:
        return [f"{name}: {SWEATERY_STATION_TEXTS[shift['station']]['name']}"
                f", cycle {shift['cycle']}/{SWEATERY_CYCLES}"
                f", {shift['liters']:.2f} l"
                for name, shift in self.sweat_shifts().items()]

    def offer_sweatery(self) -> list[str]:
        self.event["data"]["operator"] = random.choice(
            list(OPERATOR_TEXTS))
        self.event["data"]["inside"] = False
        texts = self.sweat_texts()
        return ["", texts["intro"], texts["door"],
                self.options_line(VENUE_TEXTS["sweatery"])]

    def enter_sweatery(self) -> list[Message]:
        texts = VENUE_TEXTS["sweatery"]
        self.event["data"]["inside"] = True
        entries = self.located("heated")
        unique = unique_names(entries)
        lines = [self.sweat_texts()["enter"]]
        for member in self.session.party:
            if member.profile.get(LOCKER_KEY):
                self.sweat_restore(member)
                self.session.repository.save(member)
        if not unique:
            lines.append(texts["nobody"])
        lines += listing(unique, texts["roasted"], texts["more"])
        lines += self.own_lines(unique, texts["own"])
        return self.continue_venue(lines)

    def sweatery_action(self, player:Player, command:str,
                        now:float) -> list[Message] | None:
        parts = command.split()
        texts = VENUE_TEXTS["sweatery"]
        shifts = self.sweat_shifts()
        values = {"name": player.name, "boss": self.sweat_texts()["boss"]}
        if parts[0] == "depart" and shifts:
            return [Message(texts["blocked"].format(**values), player.name)]
        if parts[0] == "sweat":
            station = parts[1] if len(parts) > 1 else ""
            if station not in SWEATERY_STATIONS:
                return [Message("Stations: " + " | ".join(
                    f"[sweat {name}]" for name in SWEATERY_STATIONS),
                    player.name)]
            if player.name in shifts:
                return [Message(texts["busy"].format(**values),
                                player.name)]
            return self.sweat_start(player, station)
        if parts[0] in ("work", "quit"):
            if player.name not in shifts:
                return [Message(texts["idle"].format(**values),
                                player.name)]
            lines = (self.sweat_quit(player) if parts[0] == "quit"
                     else self.sweat_cycle(player))
            return self.sweat_after(player, lines)
        return None

    def sweat_after(self, player:Player, lines:list[str]) -> list[Message]:
        self.session.repository.save(player)
        if not self.session.living():
            self.reset()
            return [Message("\n".join(lines + self.session.end_run()))]
        return self.continue_venue(lines)

    def sweat_restore(self, player:Player) -> None:
        locker = player.profile.pop(LOCKER_KEY, {})
        for slot, item_id in locker.items():
            if player.equipment.get(slot) is None:
                player.equipment[slot] = item_id
            else:
                player.inventory.append(item_id)

    def sweat_undress(self, player:Player) -> None:
        self.sweat_restore(player)
        locker = {slot: item_id for slot, item_id in player.equipment.items()
                  if item_id and slot != BOOT_SLOT}
        for slot in locker:
            player.equipment[slot] = None
        player.profile[LOCKER_KEY] = locker

    def sweat_start(self, player:Player, station:str) -> list[Message]:
        their = pronouns(player.gender)[2]
        texts = SWEATERY_STATION_TEXTS[station]
        self.sweat_undress(player)
        self.sweat_shifts()[player.name] = {
            "station": station, "cycle": 0, "liters": 0.0}
        lines = [self.sweat_texts()["strip"].format(name=player.name,
                                                    their=their),
                 texts["start"].format(name=player.name, their=their)]
        return self.sweat_after(player, lines + self.sweat_cycle(player))

    def sweat_cycle(self, player:Player) -> list[str]:
        shift = self.sweat_shifts()[player.name]
        operator = self.sweat_operator()
        their = pronouns(player.gender)[2]
        station = shift["station"]
        shift["cycle"] += 1
        liters = sweat_liters(player, station, operator)
        shift["liters"] = round(shift["liters"] + liters, 2)
        values = {"name": player.name, "their": their,
                  "liters": f"{liters:.2f}"}
        lines = [random.choice(
            SWEATERY_STATION_TEXTS[station]["cycle"]).format(**values),
            VENUE_TEXTS["sweatery"]["turn"].format(
                name=player.name, cycle=shift["cycle"],
                cycles=SWEATERY_CYCLES)]
        spec = SWEATERY_STATIONS[station]
        if spec["damage"]:
            player.hp -= round(max_hp(player) * SWEATERY_HEAT_DAMAGE
                               * spec["damage"])
            hurt = SWEATERY_STATION_TEXTS[station].get("hurt", SWEATERY_HURT)
            lines.append(random.choice(hurt).format(**values))
            if random.random() < SWEATERY_SQUEAL_CHANCE:
                lines.append(random.choice(
                    self.sweat_texts()["squeal"]).format(**values))
            chance = (SWEATERY_ROAST_BASE
                      + SWEATERY_ROAST_STEP * shift["cycle"]
                      ) * SWEATERY_OPERATORS[operator]["roast"] * spec[
                          "roast"]
            if player.hp <= 0 or random.random() < chance:
                return lines + self.sweat_roast(player)
        if shift["cycle"] >= SWEATERY_CYCLES:
            return lines + self.sweat_finish(player, shift)
        return lines

    def sweat_pay(self, shift:dict[str, Any]) -> int:
        rate = SWEATERY_OPERATORS[self.sweat_operator()]["pay"]
        return round(shift["liters"] * rate
                     * (1 + self.session.stage * SWEATERY_STAGE_PAY))

    def sweat_finish(self, player:Player, shift:dict[str, Any]) -> list[str]:
        del self.sweat_shifts()[player.name]
        station = shift["station"]
        lines = self.sweat_dress(player)
        gold = self.sweat_pay(shift)
        player.gold += gold
        texts = VENUE_TEXTS["sweatery"]
        lines.append(texts["done"].format(name=player.name, gold=gold,
                                          liters=f"{shift['liters']:.2f}"))
        gain = SWEATERY_STATION_TEXTS[station]["gain"]
        stat = SWEATERY_STATIONS[station]["stat"]
        if stat:
            player.stats[stat] += 1
        if gain:
            lines.append(gain.format(name=player.name))
        if station == "labour":
            lines += grant_exp(player, SWEATERY_LABOUR_EXP)
        return lines + self.sweat_store(player, shift, shift["cycle"]
                                        ) + self.sweat_boots(player, shift)

    def sweat_dress(self, player:Player) -> list[str]:
        had = bool(player.profile.get(LOCKER_KEY))
        self.sweat_restore(player)
        if not had:
            return []
        return [VENUE_TEXTS["sweatery"]["dress"].format(
            name=player.name, their=pronouns(player.gender)[2])]

    def sweat_boots(self, player:Player, shift:dict[str, Any]) -> list[str]:
        boots = player.equipment.get(BOOT_SLOT)
        if not boots or shift["cycle"] < 1:
            return []
        operator = self.sweat_operator()
        item_id = self.session.sweatery_ledger.add(
            player, shift["station"], round(SWEATERY_BOTTLE_LITERS, 2), 1,
            operator, boots=ITEMS[boots]["name"])
        return [self.sweat_texts()["boots"].format(
            name=player.name, boots=ITEMS[boots]["name"]),
            VENUE_TEXTS["sweatery"]["batch"].format(
                count=1, item=ITEMS[item_id]["name"])]

    def sweat_quit(self, player:Player) -> list[str]:
        shift = self.sweat_shifts().pop(player.name)
        gold = self.sweat_pay(shift) // 2
        player.gold += gold
        lines = self.sweat_dress(player)
        lines.append(VENUE_TEXTS["sweatery"]["quit"].format(
            name=player.name, gold=gold, liters=f"{shift['liters']:.2f}"))
        return lines + self.sweat_store(player, shift, shift["cycle"] // 2
                                        ) + self.sweat_boots(player, shift)

    def sweat_store(self, player:Player, shift:dict[str, Any],
                    count:int) -> list[str]:
        if count <= 0:
            return []
        operator = self.sweat_operator()
        liters = round(SWEATERY_BOTTLE_LITERS * random.uniform(0.9, 1.1)
                       * SWEATERY_OPERATORS[operator]["yield"], 2)
        item_id = self.session.sweatery_ledger.add(
            player, shift["station"], liters, count, operator)
        label = SWEATERY_STATION_TEXTS[shift["station"]]["name"]
        return [self.sweat_texts()["label"].format(
            name=player.name, station=label, liters=f"{liters:.2f}"),
            VENUE_TEXTS["sweatery"]["batch"].format(
                count=count, item=ITEMS[item_id]["name"])]

    def sweat_roast(self, player:Player) -> list[str]:
        from ...combat import fate_text
        texts = self.sweat_texts()
        operator = self.sweat_operator()
        del self.sweat_shifts()[player.name]
        self.sweat_restore(player)
        text = fate_text(player, "heated", None)
        player.last_fate = "heated"
        player.last_fate_text = text
        lines = [texts["roast"].format(name=player.name)]
        lines += self.session.kill_outside(
            player, "heated", text, texts["boss"], texts["plural"],
            operator)
        return lines

    def finish_sweat_shifts(self) -> list[str]:
        lines: list[str] = []
        for name in list(self.sweat_shifts()):
            player = self.session.member(name)
            while player and name in self.sweat_shifts() and player.alive:
                lines += self.sweat_cycle(player)
        return lines

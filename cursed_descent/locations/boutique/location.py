import random
import re
import uuid
from pathlib import Path
from typing import Any

from ...clock import timestamp
from ...body import DEFAULT_ENDOWMENT, muscle_tier, shape_of
from ...combat import fate_text
from ...config import (
    BOUTIQUE_ALLURE_BONUS, BOUTIQUE_ARMOR_FACTOR, BOUTIQUE_ARMOR_STEP,
    BOUTIQUE_DAMAGE_BASE, BOUTIQUE_DAMAGE_SLOTS, BOUTIQUE_DAMAGE_STEP,
    BOUTIQUE_HUNTED, BOUTIQUE_MAIN_BASE, BOUTIQUE_MAIN_MAX,
    BOUTIQUE_MAIN_STEP, BOUTIQUE_MATERIALS, BOUTIQUE_PRICE_BASE,
    BOUTIQUE_PRICE_PER_LEVEL, BOUTIQUE_SECOND_BASE, BOUTIQUE_SECOND_MAX,
    BOUTIQUE_SECOND_STEP, BOUTIQUE_STOCK, BOUTIQUE_SWEAT_PRICE,
    CODPIECE_CHANCE, CODPIECE_CM_STEP, CODPIECE_MIN_CM, CODPIECE_PREFIX,
    COLLECTION_OWN_PIECES, COLLECTION_SIZE, ROUND_TIMEOUT_SECONDS, SHAPE_MATERIALS, STAT_NAMES, SWEATY_WANDERER_TIER,
    SWEAT_CURED_TIER, SWEAT_MUSK_TIER,
)
from ...content import ITEMS, ITEM_SETS
from ...dungeon import find_inventory_item
from ...events.common import options_text, self_price, their
from ...items import remove_item, Item
from ...models import Message, Player
from ...storage import read_json, write_json
from ...sweat import sweat_tier
from ..shop.location import base_price, buy_price, item_summary, sell_price
from ...settings import get
from .content import BOUTIQUE_FALLBACK, BOUTIQUE_GARMENTS, EVENT_TEXTS
from .npc import BoutiqueNpcMixin


SETTINGS = get("boutique")


def stock_lines(groups:list[tuple[int, str, int]]) -> list[str]:
    texts = EVENT_TEXTS["boutique"]
    return [texts["stock"].format(
        nr=nr, item=f"{count}× {item_summary(item_id)}" if count > 1
        else item_summary(item_id), price=base_price(item_id))
        for nr, item_id, count in groups]


FLAT_CHESTS = ("None", "Flat")


BUST_ALLURE = {"Medium": 1, "Large": 2, "Huge": 3, "Massive": 4}


def pick_garment(player:Player) -> str:
    text = player.last_fate_text.casefold()
    for kind, garment in BOUTIQUE_GARMENTS.items():
        if any(re.search(rf"\b{re.escape(word)}\b", text)
               for word in garment["keywords"]):
            return kind
    kinds = list(BOUTIQUE_FALLBACK)
    shape = shape_of(player.gender, player.body)
    big = player.body.get("endowment", DEFAULT_ENDOWMENT) >= CODPIECE_MIN_CM
    if shape and (shape != "Human" or big) and (
            random.random() < CODPIECE_CHANCE):
        return "codpiece"
    if player.body["breasts"] in FLAT_CHESTS:
        kinds = [kind for kind in kinds if kind != "bra"]
    return random.choice(kinds)


def snapshot(player:Player) -> dict[str, Any]:
    return {"name": player.name, "level": player.level,
            "gender": player.gender, "stats": dict(player.stats),
            "body": dict(player.body), "sweat": sweat_tier(player)}


def victim_material(victim:dict[str, Any]) -> str:
    shape = shape_of(victim.get("gender", ""), victim["body"])
    if shape in SHAPE_MATERIALS:
        return SHAPE_MATERIALS[shape]
    return muscle_tier(victim["stats"], victim["body"])


def collection_id(name:str) -> str:
    return f"couture:{name}"


def register_collection(victim:dict[str, Any]) -> None:
    ranked = sorted(STAT_NAMES, key=lambda stat: victim["stats"][stat],
                    reverse=True)
    tier = muscle_tier(victim["stats"], victim["body"])
    level = victim["level"]
    third = {"melee": 0.10, "armor": 6} if tier == "leather" else (
        {"allure": 8, "crit": 0.05} if tier == "silk"
        else {"armor": 3, "allure": 4})
    ITEM_SETS[collection_id(victim["name"])] = {
        "name": f"{victim['name']} Collection",
        "size": COLLECTION_SIZE,
        "owner": victim["name"],
        "bonuses": {
            2: {"bonus": {ranked[0]: 2 + level // 10}},
            3: {"bonus": {ranked[1]: 2 + level // 10}, **third},
            4: {"bonus": {ranked[0]: 3 + level // 8}, "melee": 0.10,
                "crit": 0.10, "allure": 5},
        },
        "own_pieces": COLLECTION_OWN_PIECES,
        "own_bonus": {"bonus": {stat: 2 for stat in STAT_NAMES},
                      "allure": 3},
    }


def build_garment(victim:dict[str, Any], kind:str) -> dict[str, Any]:
    garment = BOUTIQUE_GARMENTS[kind]
    material = BOUTIQUE_MATERIALS[victim_material(victim)]
    level = victim["level"]
    ranked = sorted(STAT_NAMES, key=lambda stat: victim["stats"][stat],
                    reverse=True)
    main = min(BOUTIQUE_MAIN_BASE + level // BOUTIQUE_MAIN_STEP,
               BOUTIQUE_MAIN_MAX)
    second = min(BOUTIQUE_SECOND_BASE + level // BOUTIQUE_SECOND_STEP,
                 BOUTIQUE_SECOND_MAX)
    item: dict[str, Any] = {
        "name": f"{victim['name']} {material['label']} "
                f"{garment['label']}",
        "slot": garment["slot"],
        **({"requires": garment["requires"]} if "requires" in garment
           else {}),
        "rarity": "couture",
        "bonus": {ranked[0]: main, ranked[1]: second},
        "allure": (garment["allure"] + BOUTIQUE_ALLURE_BONUS
                   + material["allure"]),
        "no_loot": True,
        "boutique": True,
        "made_from": victim["name"],
        "set": collection_id(victim["name"]),
        "price": BOUTIQUE_PRICE_BASE + level * BOUTIQUE_PRICE_PER_LEVEL,
        "note": f"{material['note']}, handmade by <<boutique.owner>> – "
                f"from {victim['name']}, level {level}",
    }
    if garment.get("armor"):
        item["armor"] = max(1, round(
            (garment["armor"] * BOUTIQUE_ARMOR_FACTOR
             + level // BOUTIQUE_ARMOR_STEP) * material["armor"]))
    if garment["slot"] in BOUTIQUE_DAMAGE_SLOTS:
        item["damage"] = BOUTIQUE_DAMAGE_BASE + level // BOUTIQUE_DAMAGE_STEP
    if kind == "bra":
        item["allure"] += BUST_ALLURE.get(victim["body"]["breasts"], 0)
    if victim["body"]["build"] == "Curvy":
        item["allure"] += 1
    if kind == "codpiece":
        tailor_codpiece(item, victim)
    if victim.get("sweat", 0) >= SWEAT_CURED_TIER:
        item["armor"] = item.get("armor", 0) + 1
        item["note"] += " – salt-cured in its owner's sweat"
    if victim.get("sweat", 0) >= SWEAT_MUSK_TIER:
        item["allure"] += 1
        item["name"] = item["name"].replace(f"{victim['name']} ",
                                            f"{victim['name']} Musk ", 1)
        item["note"] += ", still heavy with musk"
    if victim.get("source") == "hunted":
        hunted(item, victim["name"], kind)
    return item


def tailor_codpiece(item:dict[str, Any], victim:dict[str, Any]) -> None:
    shape = shape_of(victim.get("gender", ""), victim["body"]) or "Human"
    length = victim["body"].get("endowment", DEFAULT_ENDOWMENT)
    item["name"] = f"{victim['name']} {CODPIECE_PREFIX[shape]} Codpiece"
    item["note"] = (f"{item['note']} – tailored for {length} cm "
                    f"({shape.lower()})")
    item["allure"] += length // CODPIECE_CM_STEP
    if shape == "Equine":
        item["bonus"]["agility"] = item["bonus"].get("agility", 0) - 1
    elif shape == "Canine":
        item["crit"] = 0.05
    elif shape == "Draconic":
        item["armor"] = item.get("armor", 0) + 2


def hunted_bonus(victim_name:str, kind:str) -> int:
    low, high = BOUTIQUE_HUNTED["bonus"]
    return random.Random(f"hunted:{victim_name}:{kind}").randint(low, high)


def hunted(item:dict[str, Any], victim_name:str, kind:str) -> None:
    item["name"] += " ★"
    boost = hunted_bonus(victim_name, kind)
    item["bonus"] = {stat: value + boost
                     for stat, value in item["bonus"].items()}
    if "armor" in item:
        item["armor"] = round(item["armor"] * BOUTIQUE_HUNTED["armor"])
    if "damage" in item:
        item["damage"] += BOUTIQUE_HUNTED["damage"]
    item["allure"] += BOUTIQUE_HUNTED["allure"]
    item["price"] = round(item["price"] * BOUTIQUE_HUNTED["price"])
    item["note"] = item["note"].replace(
        "handmade by", "hunted down and handmade by")


class Boutique:
    def __init__(self, data_path:Path) -> None:
        self.path = data_path / SETTINGS["file"]
        self.entries: list[dict[str, Any]] = read_json(self.path, [])
        for entry in self.entries:
            if entry.get("victim_data"):
                entry["item"] = build_garment(entry["victim_data"],
                                              entry["kind"])
            ITEMS[entry["id"]] = entry["item"]
        newest: dict[str, dict[str, Any]] = {}
        for entry in self.entries:
            if entry.get("victim_data"):
                newest[entry["victim"]] = entry["victim_data"]
        for victim in newest.values():
            register_collection(victim)

    def save(self) -> None:
        write_json(self.path, self.entries)

    def add(self, player:Player, source:str="sold") -> str:
        kind = pick_garment(player)
        item_id = f"couture_{uuid.uuid4().hex[:10]}"
        victim = snapshot(player)
        victim["source"] = source
        register_collection(victim)
        item = build_garment(victim, kind)
        ITEMS[item_id] = item
        self.entries.append({
            "id": item_id,
            "victim": player.name,
            "victim_data": victim,
            "kind": kind,
            "item": item,
            "sold": False,
            "date": timestamp(),
        })
        self.save()
        return item_id

    def stock(self) -> list[str]:
        unsold = [entry["id"] for entry in self.entries if not entry["sold"]]
        return unsold[-BOUTIQUE_STOCK:]

    def sell(self, item_id:str) -> None:
        for entry in self.entries:
            if entry["id"] == item_id:
                entry["sold"] = True
        self.save()


class BoutiqueMixin(BoutiqueNpcMixin):
    session: Any
    event: dict[str, Any]

    def open_boutique(self, now:float, intro:list[str]) -> list[str]:
        session = self.session
        session.state = "event"
        session.deadline = now + ROUND_TIMEOUT_SECONDS
        self.event = {"kind": "boutique", "used": set(), "data": {}}
        return intro + self.offer_boutique("window")[1:]

    def boutique_lines(self) -> list[str]:
        texts = EVENT_TEXTS["boutique"]
        lines = stock_lines(self.boutique_groups())
        return lines + [texts["options"].format(
            options=options_text(self.available()),
            seconds=int(ROUND_TIMEOUT_SECONDS))]

    def offer_boutique(self, intro_key:str="intro") -> list[str]:
        texts = EVENT_TEXTS["boutique"]
        self.event["phase"] = "boutique"
        self.event["data"]["stock"] = self.session.boutique.stock()
        self.event["data"]["inside"] = False
        return ["", texts[intro_key], self.strip_timer(texts["options"]).format(
            options=options_text(self.available()),
            seconds=int(ROUND_TIMEOUT_SECONDS))]

    def enter_boutique(self) -> list[Message]:
        texts = EVENT_TEXTS["boutique"]
        stock = self.event["data"]["stock"]
        self.event["data"]["inside"] = True
        lines = [texts["enter"]] + stock_lines(self.boutique_groups())
        if not stock:
            lines.append(texts["empty"])
        names = {player.name for player in self.session.party}
        sweaty = [player for player in self.session.living()
                  if sweat_tier(player) >= SWEATY_WANDERER_TIER]
        if sweaty:
            lines.append(texts["sweaty"].format(
                name=max(sweaty, key=sweat_tier).name))
        victims = {ITEMS[item_id]["made_from"] for item_id in stock}
        for victim in sorted(victims & names):
            lines.append(texts["own"].format(name=victim))
        return self.continue_event(lines)

    def sell_self(self, player:Player, now:float) -> list[Message]:
        session = self.session
        texts = EVENT_TEXTS["boutique"]
        tier = sweat_tier(player)
        gold = round(self_price(player) * (1 + tier * BOUTIQUE_SWEAT_PRICE))
        player.gold += gold
        lines = [texts["sweaty_sale"].format(name=player.name)] if tier else []
        lines.append(texts["sellself"].format(name=player.name, gold=gold,
                                              their=their(player)))
        text = fate_text(player, "fashion", None)
        player.last_fate_text = text
        lines += session.kill_outside(player, "fashion", text,
                                      SETTINGS["owner"], "designers")
        item_id = session.boutique.add(player)
        session.keeper_takes("fashion", player, item_id)
        self.event["data"]["stock"].append(item_id)
        nr = len(self.event["data"]["stock"])
        lines.append(texts["fresh"].format(
            nr=nr, item=item_summary(item_id), price=base_price(item_id)))
        if not session.living():
            self.reset()
            return [Message("\n".join(lines + session.end_run()))]
        return self.continue_event(lines)

    def boutique_active(self) -> bool:
        return (self.session.state == "event"
                and self.event.get("kind") == "boutique")

    def boutique_groups(self) -> list[tuple[int, str, int]]:
        stock = self.event["data"]["stock"]
        groups: dict[tuple[str, int], list] = {}
        for nr, item_id in enumerate(stock, 1):
            if item_id in self.event["used"]:
                continue
            key = (item_summary(item_id), base_price(item_id))
            if key in groups:
                groups[key][2] += 1
            else:
                groups[key] = [nr, item_id, 1]
        return [(nr, item_id, count) for nr, item_id, count
                in groups.values()]

    def boutique_sell(self, name:str, reference:str) -> list[Message]:
        texts = EVENT_TEXTS["boutique"]
        player = self.session.member(name)
        if not self.boutique_active() or player is None or not player.alive:
            return [Message("There is no one here to sell to.", name)]
        item_id = find_inventory_item(player, reference) if reference else None
        if item_id is None:
            return [Message(texts["sell_what"], name)]
        remove_item(player.inventory, item_id)
        price = sell_price(item_id)
        player.gold += price
        self.session.repository.save(player)
        self.session.deadline += ROUND_TIMEOUT_SECONDS / 2
        return [Message(texts["sell"].format(
            name=player.name, item=ITEMS[item_id]["name"], price=price,
            gold=player.gold))]

    def boutique_action(self, player:Player, command:str,
                        now:float) -> list[Message]:
        texts = EVENT_TEXTS["boutique"]
        if command == "depart":
            self.save_party()
            return self.finish([texts["depart"]], now)
        if command == "sellself":
            return self.sell_self(player, now)
        stock = self.event["data"]["stock"]
        item_id = stock[int(command.split()[1]) - 1]
        item = ITEMS[item_id]
        price = buy_price(item_id, player)
        values = {"name": player.name, "item": item["name"], "price": price,
                  "their": their(player), "gold": player.gold}
        if player.gold < price:
            return [Message(texts["poor"].format(**values), player.name)]
        if len(player.inventory) >= player.bag_size:
            return [Message(texts["full"].format(**values), player.name)]
        player.gold -= price
        player.inventory.append(Item(item_id, creator=SETTINGS["creator"]))
        self.event["used"].add(item_id)
        self.session.boutique.sell(item_id)
        self.session.repository.save(player)
        key = "buy_own" if item["made_from"] == player.name else "buy"
        lines = [texts[key].format(**values)]
        if key == "buy" and self.session.member(item["made_from"]):
            lines.append(texts["friend"].format(victim=item["made_from"],
                                                **values))
        return self.continue_event(lines)

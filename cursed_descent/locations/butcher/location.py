import random
from typing import Any

from ...body import fake_amount, shape_of
from ...config import (
    BUTCHER_BASIC_STOCK, MEAT_BUILD_BONUS, MEAT_COOKED_HEAL, MEAT_COOKED_MANA,
    HUNG_GENDERS, MEAT_EQUINE_BONUS, MEAT_GRADES, MEAT_GRADE_ORDER,
    MEAT_IMPLANT_PARTS, MEAT_IMPLANT_PRICE, MEAT_IMPLANT_STEP,
    MEAT_KG_PER_CUT, MEAT_LEVEL_STEP, MEAT_MAX_CUTS, MEAT_PRIME_BUST,
    MEAT_PRIME_BUTT, MEAT_PRIME_FACTOR, MEAT_RAW_HEAL, MEAT_RAW_PRICE,
    MEAT_SAUSAGE_FACTOR, MEAT_STOCK_MAX, MEAT_SWEAT_BONUS, MEAT_VIT_STEP,
    MEAT_COOKED_HUNGER, MEAT_RAW_HUNGER, SMOKERY_GRADE_BONUS,
    SMOKERY_HUNGER, SMOKERY_SMOKED_FACTOR, VENUE_LIST_MAX,
)
from ...content import ITEMS
from ...models import Message, Player
from ...sweat import sweat_tier
from .content import (
    BUTCHER_CUTS, EXTRA_CUTS, IMPLANT_CUTS, IMPLANT_UNITS, MEAT_GRADE_LABELS,
    PRIME_CUTS, SAUSAGE_CUTS, VENUE_TEXTS,
)
from ...curing import cure_stage


CURE_NOTES = {
    "fresh": "still damp and mild, cured by foot sweat and aroma, best "
             "left to hang a while longer",
    "cured": "cured in the Northern Smokery by foot sweat and aroma alone, "
             "ready to eat, with a distinctive magical foot aroma",
    "dried": "hung and matured until firm, dark and intense, with a "
             "concentrated magical foot aroma",
}


def meat_profile(player:Player) -> dict[str, Any]:
    return {"level": player.level, "build": player.body["build"],
            "vitality": player.stats["vitality"],
            "breasts": player.body["breasts"],
            "shape": shape_of(player.gender, player.body),
            "weight": player.body.get("weight", 65),
            "sweat": sweat_tier(player),
            "hung": player.gender in HUNG_GENDERS,
            "bust": player.body["bust"] - fake_amount(player.body, "bust"),
            "butt": player.body["butt"] - fake_amount(player.body, "butt"),
            "implants": {part: fake_amount(player.body, part)
                         for part in MEAT_IMPLANT_PARTS
                         if fake_amount(player.body, part) > 0}}


def meat_score(victim:dict[str, Any]) -> int:
    if not victim:
        return 0
    return (victim["level"] // MEAT_LEVEL_STEP
            + victim["vitality"] // MEAT_VIT_STEP
            + MEAT_BUILD_BONUS.get(victim["build"], 0)
            + victim.get("sweat", 0) * MEAT_SWEAT_BONUS
            + (MEAT_EQUINE_BONUS if victim.get("shape") == "Equine" else 0))


def meat_grade(score:int) -> tuple[str, float]:
    for limit, rarity, factor in MEAT_GRADES:
        if score >= limit:
            return rarity, factor
    return "common", 1.0


def meat_yield(victim:dict[str, Any]) -> int:
    if not victim:
        return 1
    cuts = round(victim.get("weight", 65) / MEAT_KG_PER_CUT)
    return min(max(cuts, 1), MEAT_MAX_CUTS)


def meat_cuts(entry:dict[str, Any]) -> list[str]:
    """Names of the regular cuts of this victim, the main cut first."""
    main = BUTCHER_CUTS.get(entry.get("detail", ""), "Cuts")
    others = [name for name in list(BUTCHER_CUTS.values())
              + list(EXTRA_CUTS.values()) if name != main]
    seed = f"{entry['name']}|{entry['stage']}"
    random.Random(seed).shuffle(others)
    count = meat_yield(entry.get("victim", {}))
    return ([main] + others)[:count]


def sausage_cut(entry:dict[str, Any]) -> str:
    return SAUSAGE_CUTS.get(entry.get("victim", {}).get("shape", ""), "")


IMPLANT_SUFFIX = {"bust": "ib", "butt": "ir", "endowment": "ie",
                  "balls": "it"}


def prime_suffixes(entry:dict[str, Any]) -> list[str]:
    victim = entry.get("victim", {})
    suffixes: list[str] = []
    if victim.get("bust", 0) >= MEAT_PRIME_BUST:
        suffixes.append("b")
    if victim.get("hung"):
        suffixes.append("t")
    if victim.get("butt", 0) >= MEAT_PRIME_BUTT:
        suffixes.append("r")
    if entry.get("fate") == "smoked":
        suffixes.append("h")
    return suffixes


def implant_suffixes(entry:dict[str, Any]) -> list[str]:
    implants = entry.get("victim", {}).get("implants", {})
    return [IMPLANT_SUFFIX[part] for part in MEAT_IMPLANT_PARTS
            if part in implants]


def prime_names(entry:dict[str, Any]) -> list[str]:
    return [PRIME_CUTS[suffix] for suffix in prime_suffixes(entry)]


def implant_names(entry:dict[str, Any]) -> list[str]:
    return [IMPLANT_CUTS[suffix] for suffix in implant_suffixes(entry)]


def meat_piece_ids(entry:dict[str, Any]) -> list[str]:
    ids = [f"meat_{entry['id']}"]
    ids += [f"meat_{entry['id']}_{number}"
            for number in range(2, len(meat_cuts(entry)) + 1)]
    if sausage_cut(entry):
        ids.append(f"meat_{entry['id']}_s")
    ids += [f"meat_{entry['id']}_{suffix}"
            for suffix in prime_suffixes(entry) + implant_suffixes(entry)]
    return ids


def meat_unsold(entry:dict[str, Any]) -> list[str]:
    sold = set(entry.get("meat_sold_ids", []))
    if entry.get("meat_sold"):
        sold.add(f"meat_{entry['id']}")
    return [item_id for item_id in meat_piece_ids(entry)
            if item_id not in sold]


def register_meat(entry:dict[str, Any]) -> None:
    victim = entry.get("victim", {})
    smoked = entry.get("fate") == "smoked"
    rarity, factor = meat_grade(meat_score(victim)
                                + (SMOKERY_GRADE_BONUS if smoked else 0))
    label = MEAT_GRADE_LABELS[rarity]
    salted = ("naturally salted from a sweaty last fight, "
              if victim.get("sweat") else "")
    grade = f"{label} " if label else ""
    cooked = MEAT_GRADE_ORDER[min(MEAT_GRADE_ORDER.index(rarity) + 1,
                                  len(MEAT_GRADE_ORDER) - 1)]
    register_implants(entry)
    pieces = list(zip(meat_piece_ids(entry), meat_cuts(entry)))
    if sausage_cut(entry):
        pieces.append((f"meat_{entry['id']}_s", sausage_cut(entry)))
    pieces += [(f"meat_{entry['id']}_{suffix}", PRIME_CUTS[suffix])
               for suffix in prime_suffixes(entry)]
    for item_id, cut in pieces:
        if smoked:
            register_smoked_piece(entry, item_id, cut, rarity, factor)
            continue
        prime = item_id.rsplit("_", 1)[-1] in PRIME_CUTS
        special = item_id.endswith("_s") or prime
        boost = (MEAT_PRIME_FACTOR if prime
                 else MEAT_SAUSAGE_FACTOR if special else 1.0)
        key = item_id.removeprefix("meat_")
        ITEMS[item_id] = {
            "name": f"{entry['name']} {grade}{cut} (raw)",
            "slot": "consumable", "rarity": rarity,
            "heal": round(MEAT_RAW_HEAL * factor * boost),
            "no_loot": True, "price": round(MEAT_RAW_PRICE * factor * boost),
            "raw_meat": True, "needs": {"hunger": MEAT_RAW_HUNGER},
            "note": f"{salted}butchered by <<npc.hamhock_first>> – "
                    + ("the house specialty, " if special else "")
                    + "cook it over a campfire ([cook] at a wanderer's "
                      "fire)",
        }
        ITEMS[f"cooked_{key}"] = {
            "name": f"Grilled {entry['name']} {grade}{cut}",
            "slot": "consumable", "rarity": cooked,
            "heal": round(MEAT_COOKED_HEAL * factor * boost),
            "mana": round(MEAT_COOKED_MANA * factor * boost),
            "no_loot": True, "needs": {"hunger": MEAT_COOKED_HUNGER,
                                       "thirst": -5},
            "price": round(MEAT_RAW_PRICE * 2 * factor * boost),
            "note": "campfire-grilled, smoky",
        }


def register_smoked_piece(entry:dict[str, Any], item_id:str, cut:str,
                          rarity:str, factor:float) -> None:
    stage, heal_factor, price_factor = cure_stage(entry)
    suffix = item_id.rsplit("_", 1)[-1]
    boost = (MEAT_PRIME_FACTOR if suffix in PRIME_CUTS
             else MEAT_SAUSAGE_FACTOR if item_id.endswith("_s") else 1.0)
    price = round(MEAT_RAW_PRICE * 2.2 * factor * boost * price_factor)
    if suffix == "h":
        ITEMS[item_id] = {
            "name": f"{entry['name']} {cut} ({stage})",
            "slot": "consumable", "rarity": "rare", "no_loot": True,
            "price": price * 2,
            "note": "salt-tanned in the Northern Smokery, not edible, "
                    "a collector's piece that reeks of Nord feet"}
        return
    ITEMS[item_id] = {
        "name": f"{entry['name']} {cut} (foot-{stage})",
        "slot": "consumable", "rarity": rarity, "no_loot": True,
        "heal": round(MEAT_COOKED_HEAL * SMOKERY_SMOKED_FACTOR * factor
                      * boost * heal_factor),
        "mana": round(MEAT_COOKED_MANA * SMOKERY_SMOKED_FACTOR * factor
                      * boost * heal_factor),
        "price": price, "needs": {"hunger": SMOKERY_HUNGER[stage]},
        "note": f"{stage}: " + CURE_NOTES[stage]}


def register_implants(entry:dict[str, Any]) -> None:
    implants = entry.get("victim", {}).get("implants", {})
    for part in MEAT_IMPLANT_PARTS:
        if part not in implants:
            continue
        suffix = IMPLANT_SUFFIX[part]
        ITEMS[f"meat_{entry['id']}_{suffix}"] = {
            "name": f"{entry['name']}'s {IMPLANT_CUTS[suffix]}",
            "slot": "consumable", "rarity": "common",
            "price": MEAT_IMPLANT_PRICE + (
                implants[part] // MEAT_IMPLANT_STEP) * MEAT_IMPLANT_PRICE,
            "no_loot": True,
            "note": f"not edible – {implants[part]} "
                    f"{IMPLANT_UNITS[suffix]}, scrubbed clean by <<npc.hamhock_first>>, "
                    f"sold as a curiosity"}


def register_all_meat(entries:list[dict[str, Any]]) -> None:
    for entry in entries:
        if entry["fate"] in ("butchered", "smoked"):
            register_meat(entry)


def cook_meat(player:Player) -> list[str]:
    cooked: list[str] = []
    for index, item_id in enumerate(player.inventory):
        if ITEMS[item_id].get("raw_meat"):
            new_id = item_id.replace("meat_", "cooked_", 1)
            player.inventory[index] = new_id
            cooked.append(ITEMS[new_id]["name"])
    return cooked


class ButcherMixin:
    session: Any
    event: dict[str, Any]

    def butcher_stock(self) -> list[str]:
        cuts = [item_id for entry in self.located("butchered")
                for item_id in meat_unsold(entry)][-MEAT_STOCK_MAX:]
        return [item_id for item_id in cuts + list(BUTCHER_BASIC_STOCK)
                if item_id not in self.event["used"]]

    def offer_butcher(self) -> list[str]:
        texts = VENUE_TEXTS["butcher_shop"]
        self.event["data"]["inside"] = False
        return ["", texts["intro"], texts["door"], self.options_line(texts)]

    def enter_butcher(self) -> list[Message]:
        texts = VENUE_TEXTS["butcher_shop"]
        self.event["data"]["inside"] = True
        entries = self.located("butchered")
        names = list(dict.fromkeys(entry["name"] for entry in entries))
        lines = [texts["enter"]]
        if names:
            lines.append(texts["hanging"].format(
                names=", ".join(names[-VENUE_LIST_MAX:])))
        else:
            lines.append(texts["empty"])
        lines += self.own_lines(entries, texts["own"])
        return self.continue_venue(lines)

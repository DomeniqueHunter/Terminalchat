import random
from typing import Any

from ...body import size_class
from ...config import (
    BREWERY_BATCH_MAX, BREWERY_FRESH_LIMIT, BREWERY_FRESH_PRICE,
    BREWERY_GEAR_MAX, BREWERY_GEAR_PRIORITY, BREWERY_GEAR_TO_SHOP,
    BREWERY_HAIR_CHANCE, BREWERY_OFFER_TIER, BREWERY_SELF_FACTOR,
    BREWERY_CUM_MAX, BREWERY_STOCK, CUM_BREW_EQUINE, CUM_BREW_FACTOR,
    BREWERY_SWEAT_PRICE, BREWERY_TALK_LIMIT, BREW_HEAL, BREW_MANA, BREW_PRICE,
    BREW_SWEAT_BONUS, BREW_TAP_FACTOR, DEFAULT_GENDER, FRESH_HEAL, FRESH_MANA, FRESH_STEP,
    MEAT_SWEAT_BONUS, PRONOUNS, ROUND_TIMEOUT_SECONDS,
    VENUE_LIST_MAX,
)
from ...content import ITEMS
from ...dungeon import find_inventory_item, give_item
from ...formulas import max_hp, max_mana
from ...items import remove_item, Item
from ...models import Message, Player
from ...sweat import sweat_tier
from ..shop.location import (
    base_price, buy_price, discount, find_index, item_description,
    item_summary, sell_price,
)
from .content import (
    ASTRID_GROWTH, BREWERY_STYLES, BREWERY_TEXTS, BREW_GRADE_LABELS,
    FRESH_TIERS,
)
from .npc import keeper_greeting


def fresh_id(heal:int, mana:int) -> str:
    return f"brew_fresh_{heal}_{mana}"


def register_fresh_drinks() -> None:
    for heal in range(FRESH_HEAL[0], FRESH_HEAL[1] + 1, FRESH_STEP):
        for mana in range(FRESH_MANA[0], FRESH_MANA[1] + 1, FRESH_STEP):
            score = heal + 2 * mana
            _, tier, rarity = next(row for row in FRESH_TIERS
                                   if score >= row[0])
            ITEMS[fresh_id(heal, mana)] = {
                "name": f"<<npc.astrid_first>>'s Fresh Mug ({tier})", "slot": "consumable",
                "rarity": rarity, "heal": heal, "mana": mana,
                "price": max(10, round(heal * 0.4 + mana * 0.8)),
                "no_loot": True,
                "note": "poured at the bar just now – still warm, thick and "
                        "creamy, with a heavy musk and a slightly salty "
                        "finish",
            }


def roll_fresh() -> str:
    def roll(low:int, high:int, mode:int) -> int:
        value = round(random.triangular(low, high, mode) / FRESH_STEP)
        return min(max(value * FRESH_STEP, low), high)
    return fresh_id(roll(*FRESH_HEAL), roll(*FRESH_MANA))


def fresh_price(player:Player) -> int:
    return max(1, round(BREWERY_FRESH_PRICE * (1 - discount(player))))


def astrid_growth(entries:list[dict[str, Any]], part:int) -> str:
    taken = sum(1 for entry in entries if entry["fate"] == "brewed")
    for minimum, *lines in ASTRID_GROWTH:
        if taken >= minimum:
            return lines[part]
    return ""


def register_brew(entry:dict[str, Any]) -> None:
    from ..butcher.location import meat_grade, meat_score
    style = BREWERY_STYLES.get(entry.get("detail", ""),
                               BREWERY_STYLES["yogurt"])
    victim = entry.get("victim", {})
    score = (meat_score(victim)
             + victim.get("sweat", 0) * (BREW_SWEAT_BONUS - MEAT_SWEAT_BONUS))
    rarity, factor = meat_grade(score)
    label = BREW_GRADE_LABELS[rarity]
    taste = ("an even heavier musk and a saltier finish from a sweaty "
             "last fight" if victim.get("sweat")
             else "a heavy musk and a slightly salty finish")
    grade = f"{label} " if label else ""
    ITEMS[f"brew_{entry['id']}"] = {
        "name": f"{entry['name']}'s {grade}{style}", "slot": "consumable",
        "rarity": rarity, "heal": round(BREW_HEAL * factor),
        "mana": round(BREW_MANA * factor), "no_loot": True,
        "price": round(BREW_PRICE * factor),
        "note": "churned by <<npc.astrid_first>> <<npc.astrid_last>> – thick, creamy and "
                f"yogurt-smooth, with {taste}",
    }


def cum_brew_id(entry_id:str) -> str:
    return f"astrid_cum_{entry_id}"


def register_cum_brew(entry:dict[str, Any]) -> None:
    base = ITEMS["cum_flask"]
    factor = CUM_BREW_FACTOR + (
        CUM_BREW_EQUINE if entry.get("victim", {}).get("shape") == "Equine"
        else 0.0)
    ITEMS[cum_brew_id(entry["id"])] = {
        "name": f"{entry['name']}'s Stud Brew", "slot": "consumable",
        "rarity": "rare", "heal": round(base["heal"] * factor),
        "mana": round(base["mana"] * factor),
        "price": round(base["price"] * factor), "no_loot": True,
        "note": "sold on by <<npc.old_trotter_first>> and labelled by <<npc.astrid_first>> – thick, "
                "warm and salty, with a stud's musk",
    }


def cum_batches(ledger:list[dict[str, Any]]) -> list[dict[str, Any]]:
    batches = [entry for entry in reversed(ledger)
               if entry.get("job") == "cum" and entry.get("left", 0) > 0]
    return batches[:BREWERY_CUM_MAX]


def register_all_cum_brews(ledger:list[dict[str, Any]]) -> None:
    for entry in ledger:
        if entry.get("job") == "cum":
            register_cum_brew(entry)


def register_all_brews(entries:list[dict[str, Any]]) -> None:
    for entry in entries:
        if entry["fate"] == "brewed":
            register_brew(entry)


def find_stock(items:list[str], reference:str) -> int | None:
    index = find_index(items, reference)
    if index is not None:
        return index
    wanted = reference.strip().casefold()
    hits = [position for position, item_id in enumerate(items)
            if wanted and wanted in ITEMS[item_id]["name"].casefold()]
    return hits[0] if len(hits) == 1 else None


RARITY_RANK = {"common": 0, "rare": 1, "epic": 2}


def drink_quality(entry:dict[str, Any]) -> tuple[int, int]:
    item = ITEMS.get(f"brew_{entry['id']}", {})
    return (RARITY_RANK.get(item.get("rarity", "common"), 0),
            item.get("heal", 0) + item.get("mana", 0))


def gear_tag(entry:dict[str, Any]) -> str:
    texts = BREWERY_TEXTS
    smell = texts["gear_smell_words"][entry.get("gear_smell", 0)]
    if entry.get("gear_slot") == "feet":
        size = texts["gear_size_words"].get(entry.get("gear_size"), "medium")
        return texts["gear_tag_feet"].format(name=entry["name"], size=size,
                                             smell=smell)
    return texts["gear_tag"].format(name=entry["name"], smell=smell)


def gear_scene(player:Player, slot:str, item_id:str) -> str:
    texts = BREWERY_TEXTS
    tier = sweat_tier(player)
    values = {"name": player.name, "item": ITEMS[item_id]["name"]}
    if slot == "feet":
        return texts["gear_feet"].format(
            size_line=texts["gear_size_lines"][size_class(
                player.body["height"])],
            smell_line=texts["gear_smell_lines"][tier], **values)
    return texts["gear_other"].format(
        smell_line=texts["gear_other_smell"][tier], **values)


def pick_gear(player:Player) -> tuple[str, str] | None:
    for slot in BREWERY_GEAR_PRIORITY:
        item_id = player.equipment.get(slot)
        if item_id and item_id in ITEMS:
            return slot, item_id
    return None


def self_quote(player:Player) -> tuple[int, int, str, str]:
    """(plain price, value of the piece she keeps, item name, slot)"""
    base = self_offer(player)
    gear = pick_gear(player)
    if gear is None:
        return base, 0, "", ""
    return base, base_price(gear[1]), ITEMS[gear[1]]["name"], gear[0]


def self_total(player:Player) -> int:
    base, value, _, _ = self_quote(player)
    return base + value


def self_line(player:Player) -> str:
    base, value, item, _ = self_quote(player)
    extra = (BREWERY_TEXTS["menu_self_gear"].format(
        base=base, value=value, item=item) if value else "")
    return BREWERY_TEXTS["menu_self"].format(gold=base + value, extra=extra)


def self_offer(player:Player) -> int:
    from ...events.common import self_price
    return round(self_price(player) * BREWERY_SELF_FACTOR
                 * (1 + sweat_tier(player) * BREWERY_SWEAT_PRICE))


def sweat_offer(player:Player) -> str:
    tier = sweat_tier(player)
    if tier < BREWERY_OFFER_TIER:
        return ""
    pool = BREWERY_TEXTS["offer_drenched" if tier >= 3 else "offer"]
    return random.choice(pool).format(name=player.name,
                                      gold=self_total(player))


class BreweryMixin:
    session: Any
    event: dict[str, Any]

    def brewery_inside(self) -> bool:
        return (self.event.get("kind") == "brewery"
                and bool(self.event["data"].get("inside")))

    def brewery_offers(self) -> list[tuple[str, str, str]]:
        offers = [(item_id, item_id, "") for item_id in BREWERY_STOCK]
        entries = self.located("brewed")
        batches = [entry for entry in reversed(entries)
                   if not entry.get("brew_sold")]
        batches.sort(key=drink_quality, reverse=True)
        for entry in batches[:BREWERY_BATCH_MAX]:
            offers.append((f"brew_{entry['id']}", f"brew_{entry['id']}", ""))
        for entry in cum_batches(self.session.farm_ledger.entries):
            register_cum_brew(entry)
            offers.append((f"cumbrew_{entry['id']}", cum_brew_id(entry["id"]),
                           BREWERY_TEXTS["cum_tag"]))
        gear = [entry for entry in entries
                if entry.get("gear") in ITEMS and not entry.get("gear_sold")]
        for entry in gear[-BREWERY_GEAR_MAX:]:
            offers.append((f"gear_{entry['id']}", entry["gear"],
                           gear_tag(entry)))
        return [offer for offer in offers
                if offer[0] not in self.event["used"]]

    def brewery_stock(self) -> list[tuple[int, str, int]]:
        if not self.brewery_inside():
            return []
        return [(nr, item_id, base_price(item_id))
                for nr, (_, item_id, _) in enumerate(self.brewery_offers(), 1)]

    def hero_drinks(self) -> list[tuple[str, str]]:
        return [(key, item_id) for key, item_id, _ in self.brewery_offers()
                if key.startswith("brew_") and key not in BREWERY_STOCK]

    def brewery_special(self) -> tuple[str, str] | None:
        drinks = self.hero_drinks()
        return drinks[0] if drinks else None

    def brewery_note(self, nr:int) -> str:
        offers = self.brewery_offers()
        if not 0 < nr <= len(offers):
            return ""
        note = offers[nr - 1][2]
        special = self.brewery_special()
        if special and offers[nr - 1][0] == special[0]:
            note += BREWERY_TEXTS["special_tag"]
        return note

    def brewery_ad_parts(self) -> tuple[str, str, str] | None:
        special = self.brewery_special()
        if not special:
            return None
        texts = BREWERY_TEXTS
        item = ITEMS[special[1]]
        count = len(self.hero_drinks())
        stock = (texts["ad_stock_one"] if count == 1
                 else texts["ad_stock_many"].format(count=count))
        quality = texts["ad_quality"].get(item["rarity"],
                                          texts["ad_quality"]["common"])
        return item["name"], quality, stock

    def brewery_ad(self, key:str="ad") -> list[str]:
        texts = BREWERY_TEXTS
        parts = self.brewery_ad_parts()
        if parts is None:
            return [texts["ad_none"]] if key == "ad" else []
        item, quality, stock = parts
        lines = [texts[key].format(item=item, quality=quality, stock=stock)]
        heroes = {entry["id"]: entry["name"]
                  for entry in self.session.remains.entries}
        drinks = {heroes.get(drink_key.partition("_")[2]): item_id
                  for drink_key, item_id in self.hero_drinks()}
        for member in self.session.party:
            if member.name in drinks:
                lines.append(texts["ad_own"].format(
                    name=member.name, item=ITEMS[drinks[member.name]]["name"]))
        return lines

    def brewery_special_text(self) -> str:
        parts = self.brewery_ad_parts()
        if parts is None:
            return "No house specials in stock – fresh batches wanted."
        item, quality, stock = parts
        return f"★ Today's special: {item} – {quality}, {stock}"

    def fresh_left(self) -> int:
        if self.event.get("kind") != "brewery":
            return 0
        return self.event["data"].get("fresh_left", BREWERY_FRESH_LIMIT)

    def brewery_fresh_line(self, player:Player) -> str:
        left = self.fresh_left()
        if left <= 0:
            return BREWERY_TEXTS["menu_fresh_dry"]
        return BREWERY_TEXTS["menu_fresh"].format(
            price=fresh_price(player), left=left)

    def brewery_options(self) -> list[str]:
        if not self.brewery_inside():
            return ["examine", "enter", "pass"]
        tap = ["tap"] if self.event["data"].get("tap") else []
        return ["examine", "shop", "buy <nr>", "fresh", "sell <nr>",
                "sellself", *tap, "depart"]

    def brewery_options_line(self) -> str:
        options = " | ".join(f"[{option}]"
                             for option in self.brewery_options())
        return self.strip_timer(BREWERY_TEXTS["options"]).format(
            options=options, seconds=int(ROUND_TIMEOUT_SECONDS))

    def brewery_continue(self, lines:list[str]) -> list[Message]:
        return [Message("\n".join(lines + [self.brewery_options_line()]))]

    def brewery_board(self, where:str) -> list[str]:
        texts = BREWERY_TEXTS
        entries = self.located("brewed")
        names = list(dict.fromkeys(entry["name"] for entry in entries))
        if not names:
            return [texts[f"{where}_empty"]]
        return [texts[where].format(names=", ".join(names[-VENUE_LIST_MAX:]))]

    def brewery_stock_lines(self) -> list[str]:
        return [BREWERY_TEXTS["stock"].format(
            nr=nr, item=item_summary(item_id), price=price,
            note=self.brewery_note(nr))
            for nr, item_id, price in self.brewery_stock()]

    def offer_brewery(self) -> list[str]:
        self.event["data"]["inside"] = False
        self.event["data"]["fresh_left"] = BREWERY_FRESH_LIMIT
        return (["", BREWERY_TEXTS["intro"]] + self.brewery_ad("ad")
                + [BREWERY_TEXTS["outside"], self.brewery_options_line()])

    def enter_brewery(self) -> list[Message]:
        self.event["data"]["inside"] = True
        texts = BREWERY_TEXTS
        lines = [texts["enter"]]
        sweatiest = max(self.session.living(), key=sweat_tier, default=None)
        offer = sweat_offer(sweatiest) if sweatiest else ""
        if offer:
            lines.append(offer)
        size = astrid_growth(self.session.remains.entries, 0)
        if size:
            lines.append(size)
        delivery = cum_batches(self.session.farm_ledger.entries)
        if delivery:
            names = ", ".join(sorted({entry["name"] for entry in delivery}))
            lines.append(texts["cum_delivery"].format(names=names))
        lines += self.brewery_board("board_in")
        lines += self.own_lines(self.located("brewed"), texts["own"])
        lines += self.brewery_ad("ad_in")
        lines += self.brewery_stock_lines()
        return self.brewery_continue(lines)

    def leave_brewery(self, now:float) -> list[Message]:
        key = "depart" if self.brewery_inside() else "pass"
        self.save_party()
        return self.finish([BREWERY_TEXTS[key]], now)

    def brewery_examine(self, player:Player) -> list[Message]:
        texts = BREWERY_TEXTS
        if not self.brewery_inside():
            lines = [texts["look_outside"]]
            lines += self.brewery_board("board_out")
            lines += self.own_lines(self.located("brewed"), texts["own"])
            lines += self.brewery_ad("ad")
            lines.append(texts["look_hint"])
            return [Message("\n".join(lines), player.name)]
        lines = [texts["look_shop"], "", texts["look_keeper"]]
        size = astrid_growth(self.session.remains.entries, 0)
        if size:
            lines.append(size)
        lines += self.brewery_board("board_in")
        lines += self.own_lines(self.located("brewed"), texts["own"])
        lines += self.brewery_ad("ad_in")
        lines += ["", texts["menu_sale"]]
        lines += [f"  {nr}. {item_description(item_id)} – "
                  f"{buy_price(item_id, player)} gold{self.brewery_note(nr)}"
                  for nr, item_id, _ in self.brewery_stock()]
        lines += [self.brewery_fresh_line(player),
                  texts["look_buys"], self_line(player)]
        return [Message("\n".join(lines), player.name)]

    def brewery_talk(self, player:Player, now:float) -> list[Message]:
        data = self.event["data"]
        data["talks"] = data.get("talks", 0) + 1
        if BREWERY_TALK_LIMIT and data["talks"] >= BREWERY_TALK_LIMIT:
            return self.brewery_sell_self(player, now, forced=True)
        return self.brewery_menu(player)

    def brewery_menu(self, player:Player) -> list[Message]:
        texts = BREWERY_TEXTS
        lines = [keeper_greeting(player)]
        offer = sweat_offer(player)
        if offer:
            lines.append(offer)
        warn = BREWERY_TALK_LIMIT - self.event["data"].get("talks", 0)
        if BREWERY_TALK_LIMIT and 0 < warn <= len(texts["talk_warn"]):
            lines.append(texts["talk_warn"][-warn].format(name=player.name))
        lines += ["", f"💰 Your gold: {player.gold}"]
        if discount(player):
            lines.append(texts["discount"].format(
                percent=round(discount(player) * 100)))
        lines.append(texts["menu_sale"])
        lines += [f"  {nr}. {item_description(item_id)} – "
                  f"{buy_price(item_id, player)} gold{self.brewery_note(nr)}"
                  for nr, item_id, _ in self.brewery_stock()]
        if player.inventory:
            lines.append(texts["menu_bag"])
            lines += [f"  {index}. {ITEMS[item_id]['name']} – "
                      f"{sell_price(item_id)} gold"
                      for index, item_id in enumerate(player.inventory,
                                                      start=1)]
        lines.append(self.brewery_fresh_line(player))
        lines.append(self_line(player))
        return [Message("\n".join(lines), player.name)]

    def brewery_buy(self, player:Player, reference:str) -> list[Message]:
        texts = BREWERY_TEXTS
        offers = self.brewery_offers()
        items = [item_id for _, item_id, _ in offers]
        index = find_stock(items, reference) if reference else None
        if index is None:
            return [Message(texts["buy_what"], player.name)]
        key, item_id, _ = offers[index]
        price = buy_price(item_id, player)
        values = {"name": player.name, "item": ITEMS[item_id]["name"],
                  "price": price, "gold": player.gold}
        if player.gold < price:
            return [Message(texts["poor"].format(**values), player.name)]
        if len(player.inventory) >= player.bag_size:
            return [Message(texts["full"].format(**values), player.name)]
        player.gold -= price
        lines = [texts["buy"].format(**values), give_item(player, item_id)]
        self.event["data"]["talks"] = 0
        if key.startswith("cumbrew_"):
            from ..farm.location import product_id
            self.session.farm_ledger.take(
                product_id("shift", key.partition("_")[2]))
        sold = {"brew_": "brew_sold", "gear_": "gear_sold"}
        flag = next((value for prefix, value in sold.items()
                     if key.startswith(prefix) and key not in BREWERY_STOCK),
                    "")
        if flag:
            self.event["used"].add(key)
            entry_id = key.partition("_")[2]
            for entry in self.session.remains.entries:
                if entry["id"] == entry_id:
                    entry[flag] = True
            self.session.remains.save()
        self.session.repository.save(player)
        return self.brewery_continue(lines)

    def brewery_fresh(self, player:Player) -> list[Message]:
        texts = BREWERY_TEXTS
        price = fresh_price(player)
        values = {"name": player.name, "price": price, "gold": player.gold}
        if self.fresh_left() <= 0:
            return [Message(texts["fresh_empty"], player.name)]
        if player.gold < price:
            return [Message(texts["fresh_poor"].format(**values),
                            player.name)]
        if len(player.inventory) >= player.bag_size:
            return [Message(texts["fresh_full"].format(**values),
                            player.name)]
        player.gold -= price
        item_id = roll_fresh()
        player.inventory.append(Item(item_id, creator="brewery"))
        lines = [random.choice(texts["fresh_pay"]).format(**values),
                 random.choice(texts["fresh_work"]),
                 random.choice(texts["fresh_serve"]).format(**values)]
        if random.random() < BREWERY_HAIR_CHANCE:
            lines.append(random.choice(texts["fresh_hair"]).format(**values))
        lines.append(texts["fresh_item"].format(
            name=player.name, item=item_summary(item_id)))
        self.event["data"]["talks"] = 0
        left = self.fresh_left() - 1
        self.event["data"]["fresh_left"] = left
        if left == 1:
            lines.append(texts["fresh_tired"])
        elif left == 0:
            lines.append(texts["fresh_dry"])
        self.session.repository.save(player)
        return self.brewery_continue(lines)

    def brewery_sell(self, player:Player, reference:str) -> list[Message]:
        texts = BREWERY_TEXTS
        item_id = find_inventory_item(player, reference) if reference else None
        if item_id is None:
            return [Message(texts["sell_what"], player.name)]
        remove_item(player.inventory, item_id)
        price = sell_price(item_id)
        player.gold += price
        self.session.repository.save(player)
        return self.brewery_continue([texts["sell"].format(
            name=player.name, item=ITEMS[item_id]["name"], price=price,
            gold=player.gold)])

    def brewery_sell_self(self, player:Player, now:float,
                          forced:bool=False) -> list[Message]:
        from ...combat import fate_text
        session = self.session
        texts = BREWERY_TEXTS
        tier = sweat_tier(player)
        known = any(player.owns(entry)
                    for entry in self.located("brewed"))
        base, value, gear_name, _ = self_quote(player)
        their = PRONOUNS.get(player.gender, PRONOUNS[DEFAULT_GENDER])[2]
        lines = []
        if forced:
            self.event["data"]["talks"] = 0
            text = random.choice(texts["forced"]).format(name=player.name)
        else:
            player.gold += base + value
            if tier:
                lines.append(texts["sweaty"])
            lines.append(texts["sellself"].format(
                name=player.name, gold=base + value, their=their))
            if value:
                lines.append(texts["sellself_gear"].format(
                    base=base, value=value, name=player.name, their=their,
                    item=gear_name))
            if known:
                lines.append(texts["known"].format(name=player.name))
            text = fate_text(player, "brewed", None)
        player.last_fate = "brewed"
        player.last_fate_text = text
        fallen = session.kill_outside(player, "brewed", text,
                                      "Astrid Creamworth", "brewers",
                                      random.choice(list(BREWERY_STYLES)))
        lines.append(fallen[0])
        lines.append("🍺 " + astrid_growth(session.remains.entries, 1))
        lines += fallen[1:]
        entry = session.remains.entries[-1]
        register_brew(entry)
        gear = pick_gear(player)
        if gear:
            slot, item_id = gear
            player.equipment[slot] = None
            if BREWERY_GEAR_TO_SHOP:
                entry.update(gear=item_id, gear_slot=slot,
                             gear_smell=sweat_tier(player),
                             gear_size=size_class(player.body["height"]))
                lines.append(gear_scene(player, slot, item_id))
            else:
                lines.append(texts["gear_eaten"].format(
                    name=player.name, item=ITEMS[item_id]["name"]))
            session.remains.save()
            session.repository.save(player)
        lines.append(texts["fresh"].format(
            item=ITEMS[f"brew_{entry['id']}"]["name"]))
        self.event["data"]["tap"] = {"id": entry["id"], "victim": player.name,
                                     "drank": set()}
        lines.append(texts["tap_hint"].format(victim=player.name))
        if not session.living():
            self.reset()
            return [Message("\n".join(lines + session.end_run()))]
        return self.brewery_continue(lines)

    def brewery_tap(self, player:Player) -> list[Message]:
        texts = BREWERY_TEXTS
        tap = self.event["data"].get("tap")
        if not tap:
            return [Message(texts["tap_none"], player.name)]
        if player.name in tap["drank"]:
            return [Message(texts["tap_done"].format(name=player.name),
                            player.name)]
        tap["drank"].add(player.name)
        item = ITEMS[f"brew_{tap['id']}"]
        player.hp = min(max_hp(player), player.hp + round(
            item["heal"] * BREW_TAP_FACTOR))
        player.mana = min(max_mana(player), player.mana + round(
            item["mana"] * BREW_TAP_FACTOR))
        their = PRONOUNS.get(player.gender, PRONOUNS[DEFAULT_GENDER])[2]
        text = random.choice(texts["tap_drink"]).format(
            name=player.name, victim=tap["victim"], their=their)
        self.session.repository.save(player)
        return self.brewery_continue([text])

    def brewery_action(self, player:Player, command:str, args:list[str],
                       now:float) -> list[Message]:
        texts = BREWERY_TEXTS
        inside = self.brewery_inside()
        if command == "examine":
            return self.brewery_examine(player)
        if command in ("pass", "depart"):
            return self.leave_brewery(now)
        if not inside:
            if command == "enter":
                return self.enter_brewery()
            if command in ("shop", "buy", "fresh", "sell", "sellself"):
                return [Message(texts["not_inside"], player.name)]
        else:
            reference = " ".join(args)
            if command == "shop":
                return self.brewery_talk(player, now)
            if command == "buy":
                return self.brewery_buy(player, reference)
            if command == "fresh":
                return self.brewery_fresh(player)
            if command == "sell":
                return self.brewery_sell(player, reference)
            if command == "sellself":
                return self.brewery_sell_self(player, now)
            if command == "tap":
                return self.brewery_tap(player)
        return [Message(texts["invalid"].format(
            options=" | ".join(f"[{o}]" for o in self.brewery_options())),
            player.name)]

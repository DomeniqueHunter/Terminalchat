# General shop engine: a shop is a ShopDef (data) plus a stock file of its own.
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .config import SHOPS_DIR_NAME
from .content import ITEMS
from .items import Item
from .locations.shop.location import (
    base_price, buy_price, find_index, item_description, sell_price,
)
from .models import Message, Player
from .storage import read_json, write_json


CATEGORIES = ("armor", "weapons", "consumables")
ARMOR_TABS = {"ladies": "lady", "gents": "gent"}
RARITY_WEIGHTS = {"common": 55, "rare": 35, "epic": 10}
MAX_STOCK = 10


@dataclass
class ShopDef:
    shop_id:str
    name:str
    description:str
    categories:tuple[str, ...]
    stock:dict[str, int] = field(default_factory=dict)
    consumables:tuple[str, ...] = ()
    always:str = ""
    creator:str = "shop"
    texts:dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_data(cls, data:dict[str, Any]) -> "ShopDef":
        return cls(data["id"], data["name"], data["description"],
                   tuple(data["categories"]), dict(data.get("stock", {})),
                   tuple(data.get("consumables", ())),
                   data.get("always", ""), data.get("creator", "shop"),
                   data.get("texts", {}))


def category_of(item_id:str) -> str:
    slot = ITEMS[item_id]["slot"]
    if slot == "consumable":
        return "consumables"
    return "weapons" if slot == "weapon" else "armor"


def fits(item_id:str, tab:str) -> bool:
    wanted = ARMOR_TABS[tab]
    return ITEMS[item_id].get("for", "both") in (wanted, "both")


def tag_of(item_id:str) -> str:
    side = ITEMS[item_id].get("for", "both")
    return {"lady": " [ladies]", "gent": " [gents]"}.get(side, "")


class Shop:
    def __init__(self, defn:ShopDef, data_path:Path) -> None:
        self.defn = defn
        self.path = data_path / SHOPS_DIR_NAME / f"{defn.shop_id}.json"
        saved = read_json(self.path, {})
        self.stock:dict[str, list[str]] = {
            category: [item_id for item_id in saved.get(category, [])
                       if item_id in ITEMS]
            for category in defn.stock}
        if any(not items for items in self.stock.values()):
            self.restock()

    def save(self) -> None:
        write_json(self.path, self.stock)

    def always_items(self) -> list[str]:
        if not self.defn.always:
            return []
        return [item_id for item_id, item in ITEMS.items()
                if item.get(self.defn.always)]

    def pool(self, category:str) -> list[str]:
        return [item_id for item_id, item in ITEMS.items()
                if self.defn.shop_id in item.get("shops", ())
                and category_of(item_id) == category
                and item["rarity"] in RARITY_WEIGHTS]

    def restock(self, rng:random.Random | None=None) -> str:
        rng = rng or random.Random(random.random())
        for category, size in self.defn.stock.items():
            options = self.pool(category)
            chosen:list[str] = []
            while options and len(chosen) < size:
                weights = [RARITY_WEIGHTS[ITEMS[item_id]["rarity"]]
                           for item_id in options]
                pick = rng.choices(options, weights=weights)[0]
                chosen.append(pick)
                options.remove(pick)
            self.stock[category] = chosen
        self.save()
        return self.defn.texts.get("restock", "")

    def items_of(self, category:str) -> list[str]:
        if category == "consumables":
            return list(self.defn.consumables)
        stocked = self.stock.get(category, [])
        extra = [item_id for item_id in self.always_items()
                 if category_of(item_id) == category
                 and item_id not in stocked]
        return extra + stocked

    def offers(self) -> list[str]:
        return [item_id for category in CATEGORIES
                if category in self.defn.categories
                for item_id in self.items_of(category)]

    def line(self, player:Player, item_id:str) -> str:
        number = self.offers().index(item_id) + 1
        return (f"  {number}. {item_description(item_id)}{tag_of(item_id)}"
                f" – {buy_price(item_id, player)} gold")

    def head(self, player:Player) -> list[str]:
        return [f"💰 Your gold: {player.gold}"]

    def categories_line(self) -> str:
        words = " ".join(f"[{category}]" for category in self.defn.categories)
        return f"Browse: {words} – [examine] – [talk] – [buy <nr>]"

    def show(self, player:Player) -> list[Message]:
        greeting = self.defn.texts.get("greeting")
        opening = greeting(player) if callable(greeting) else greeting
        lines = [opening, ""] + self.head(player)
        lines += self.defn.texts.get("extra", lambda player: [])(player)
        lines.append(self.categories_line())
        lines.append(self.sell_hint(player))
        return [Message("\n".join(line for line in lines if line is not None),
                        player.name)]

    def sell_hint(self, player:Player) -> str:
        if not player.inventory:
            return ""
        return "Your bag – [sell <nr>]:\n" + "\n".join(
            f"  {index}. {ITEMS[item_id]['name']} – {sell_price(item_id)} gold"
            for index, item_id in enumerate(player.inventory, start=1)
            if self.buys(item_id))

    def examine(self, player:Player) -> list[Message]:
        counts = ", ".join(
            f"{len(self.items_of(category))} {category}"
            for category in self.defn.categories)
        return [Message(f"{self.defn.description}\nOn the shelves: {counts}.",
                        player.name)]

    def talk(self, player:Player) -> list[Message]:
        lines = self.defn.texts.get("talk", ())
        text = random.choice(list(lines)) if lines else "…"
        return [Message(text.format(name=player.name), player.name)]

    def browse(self, player:Player, category:str,
               option:str="") -> list[Message]:
        if category not in self.defn.categories:
            return [Message(self.defn.texts["no_category"].format(
                category=category), player.name)]
        lines = self.head(player)
        if category == "armor":
            lines += self.armor_lines(player, option)
        elif category == "weapons":
            lines += self.weapon_lines(player, option)
        else:
            lines += [self.line(player, item_id)
                      for item_id in self.items_of("consumables")]
        lines.append("[buy <nr>] to buy.")
        return [Message("\n".join(lines), player.name)]

    def classes(self) -> list[str]:
        return sorted({ITEMS[item_id].get("class", "other")
                       for item_id in self.items_of("weapons")})

    def view_items(self, category:str, option:str="") -> list[str]:
        items = self.items_of(category)
        if category == "armor" and option in ARMOR_TABS:
            return [item_id for item_id in items if fits(item_id, option)]
        if category == "weapons" and option:
            return [item_id for item_id in items
                    if ITEMS[item_id].get("class", "other") == option]
        return items

    def armor_lines(self, player:Player, option:str) -> list[str]:
        tabs = [option] if option in ARMOR_TABS else list(ARMOR_TABS)
        lines:list[str] = []
        for tab in tabs:
            rows = [self.line(player, item_id)
                    for item_id in self.items_of("armor")
                    if fits(item_id, tab)]
            lines.append(f"[{tab}] {len(rows)} pieces")
            lines += rows or ["  (nothing here for the " + tab + ")"]
        return lines

    def weapon_lines(self, player:Player, option:str) -> list[str]:
        items = self.items_of("weapons")
        classes = sorted({ITEMS[item_id].get("class", "other")
                          for item_id in items})
        chosen = [option] if option in classes else classes
        lines = ["Classes: " + " ".join(f"[{name}]" for name in classes)]
        for name in chosen:
            lines.append(f"[{name}]")
            lines += [self.line(player, item_id) for item_id in items
                      if ITEMS[item_id].get("class", "other") == name]
        return lines

    def buys(self, item_id:str) -> bool:
        return category_of(item_id) in self.defn.texts.get(
            "buys", self.defn.categories)

    def buy(self, player:Player, reference:str) -> list[Message]:
        texts = self.defn.texts
        offers = self.offers()
        index = find_index(offers, reference) if reference else None
        if index is None:
            return [Message(texts["which"], player.name)]
        item_id = offers[index]
        price = buy_price(item_id, player)
        if player.gold < price:
            return [Message(texts["broke"].format(price=price,
                                                  gold=player.gold),
                            player.name)]
        if len(player.inventory) >= player.bag_size:
            return [Message(texts["full"].format(name=player.name),
                            player.name)]
        player.gold -= price
        player.inventory.append(Item(item_id, creator=self.defn.creator))
        category = category_of(item_id)
        if item_id in self.stock.get(category, []):
            self.stock[category].remove(item_id)
            self.save()
        text = random.choice(texts["buy"]).format(
            name=player.name, item=ITEMS[item_id]["name"], price=price)
        return [Message(f"{text}\n💰 Gold left: {player.gold}", player.name)]

    def shelve(self, item_id:str) -> str:
        category = category_of(item_id)
        if category not in self.stock:
            return ITEMS[item_id]["name"] if category == "consumables" else ""
        shelf = self.stock[category]
        donated = ""
        if item_id not in shelf:
            shelf.append(item_id)
        if len(shelf) > MAX_STOCK:
            donated = ITEMS[shelf.pop(0)]["name"]
        self.save()
        return donated

    def sell(self, player:Player, reference:str) -> list[Message]:
        texts = self.defn.texts
        index = (find_index(player.inventory, reference) if reference
                 else None)
        if index is None:
            return [Message(texts["which_sell"], player.name)]
        item_id = player.inventory[index]
        if not self.buys(item_id):
            return [Message(texts["not_buying"].format(
                item=ITEMS[item_id]["name"]), player.name)]
        player.inventory.pop(index)
        price = sell_price(item_id)
        player.gold += price
        donated = self.shelve(item_id)
        cursed = ITEMS[item_id]["rarity"] == "cursed" and "sell_cursed" in texts
        template = (texts["sell_cursed"] if cursed
                    else random.choice(texts["sell"]))
        text = template.format(name=player.name, item=ITEMS[item_id]["name"],
                               price=price)
        note = (f"\n🎁 The shelves are full, so {donated} is donated "
                f"to the poor." if donated else "")
        return [Message(f"{text}\n💰 Gold: {player.gold}{note}",
                        player.name)]

    def command(self, player:Player, args:list[str]) -> list[Message]:
        word = args[0].lower() if args else ""
        rest = args[1].lower() if len(args) > 1 else ""
        if word == "examine":
            return self.examine(player)
        if word == "talk":
            return self.talk(player)
        if word in CATEGORIES:
            return self.browse(player, word, rest)
        if word in self.defn.categories:
            return self.browse(player, word, rest)
        return self.show(player)


class ShopHub:
    def __init__(self, data_path:Path, defs:list[ShopDef]) -> None:
        self.shops = {defn.shop_id: Shop(defn, data_path) for defn in defs}

    def restock(self) -> str:
        lines = [shop.restock() for shop in self.shops.values()]
        return next((line for line in lines if line), "")

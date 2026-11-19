import random
from pathlib import Path

from cursed_descent.content import ITEMS
from cursed_descent.controller import GameController
from cursed_descent.locations.shop.location import VELVET
from cursed_descent.locations.smith.location import SMITH
from cursed_descent.shop_system import Shop, ShopDef, category_of, fits


def texts(messages) -> str:
    return "\n".join(message.text for message in messages)


def make_shop(tmp_path:Path, data:dict) -> Shop:
    return Shop(ShopDef.from_data(data), tmp_path)


def test_every_shop_keeps_its_own_stock_file(
        controller:GameController) -> None:
    folder = controller.repository.items.directory.parent / "shops"
    assert (folder / "velvet.json").exists()
    assert (folder / "smith.json").exists()


def test_stock_never_holds_cursed_gear_and_follows_the_shop_ids(
        tmp_path:Path) -> None:
    for data in (VELVET, SMITH):
        shop = make_shop(tmp_path, data)
        for _ in range(10):
            shop.restock(random.Random())
            for category, items in shop.stock.items():
                for item_id in items:
                    assert ITEMS[item_id]["rarity"] != "cursed"
                    assert data["id"] in ITEMS[item_id]["shops"]
                    assert category_of(item_id) == category


def test_armor_tabs_split_ladies_and_gents(tmp_path:Path) -> None:
    shop = make_shop(tmp_path, VELVET)
    for item_id in shop.view_items("armor", "ladies"):
        assert fits(item_id, "ladies")
        assert ITEMS[item_id].get("for", "both") in ("lady", "both")
    for item_id in shop.view_items("armor", "gents"):
        assert ITEMS[item_id].get("for", "both") in ("gent", "both")


def test_a_shop_with_only_ladies_armor_has_an_empty_gents_tab(
        tmp_path:Path) -> None:
    shop = make_shop(tmp_path, VELVET)
    shop.stock["armor"] = [item_id for item_id in shop.pool("armor")
                           if ITEMS[item_id].get("for") == "lady"][:4]
    assert shop.view_items("armor", "ladies")
    assert shop.view_items("armor", "gents") == []
    player = type("P", (), {"gold": 5, "name": "x", "body": {},
                            "needs": {}, "inventory": [],
                            "equipment": {}, "buffs": []})
    lines = "\n".join(shop.armor_lines(player, "gents"))
    assert "nothing here for the gents" in lines


def test_smith_has_no_consumables_and_velvet_has_no_heavy_weapons(
        controller:GameController) -> None:
    assert "No consumables" in texts(
        controller.handle("kerl", "!smith consumables"))
    velvet = controller.shop
    classes = set(velvet.classes())
    assert not classes & {"axe", "blunt", "ranged"}


def test_shop_commands_examine_talk_and_categories(
        controller:GameController) -> None:
    assert "Velvet's shop" in texts(controller.handle("kerl", "!shop examine"))
    assert texts(controller.handle("kerl", "!shop talk"))
    armor = texts(controller.handle("kerl", "!shop armor"))
    assert "[ladies]" in armor and "[gents]" in armor
    assert "Classes:" in texts(controller.handle("kerl", "!shop weapons"))
    assert "Potion" in texts(controller.handle("kerl", "!shop consumables"))
    assert "Browse:" in texts(controller.handle("kerl", "!shop"))


def test_category_words_use_the_shop_you_visited(
        controller:GameController) -> None:
    controller.handle("kerl", "!smith")
    reply = texts(controller.handle("kerl", "!weapons"))
    assert "Classes:" in reply
    controller.handle("kerl", "!shop")
    assert "[ladies]" in texts(controller.handle("kerl", "!armor"))


def test_buying_records_the_shop_as_creator(
        controller:GameController) -> None:
    player = controller.repository.load("kerl")
    player.gold = 100000
    player.inventory = []
    controller.repository.save(player)
    controller.handle("kerl", "!forge 1")
    controller.repository.save(player)
    bought = player.inventory[0]
    record = controller.repository.items.get(bought.iid)
    assert record["creator"] == "smith"
    assert record["owner"] == player.id


def test_smith_always_stocks_the_forged_to_order_weapons(
        controller:GameController) -> None:
    offers = controller.smith.offers()
    for item_id, item in ITEMS.items():
        if item.get("smith"):
            assert item_id in offers


def test_lady_gear_cannot_be_worn_by_a_gent() -> None:
    from cursed_descent.formulas import can_wear
    from cursed_descent.models import Player
    lady = Player(name="A", gender="Female")
    gent = Player(name="B", gender="Male")
    assert can_wear(lady, "rapier")
    assert not can_wear(gent, "rapier")
    assert can_wear(gent, "longsword") and can_wear(lady, "longsword")


def test_dungeon_loot_gear_is_up_to_a_quarter_stronger(monkeypatch) -> None:
    from cursed_descent import dungeon
    from cursed_descent.item_store import base_stats
    monkeypatch.setattr(dungeon.random, "uniform", lambda low, high: high)
    stats = dungeon.loot_stats("war_axe")
    base = base_stats("war_axe")
    assert stats["damage"] == round(base["damage"] * 1.25)
    assert stats["bonus"]["strength"] >= base["bonus"]["strength"]
    monkeypatch.setattr(dungeon.random, "uniform", lambda low, high: low)
    assert dungeon.loot_stats("war_axe") == base
    assert dungeon.loot_stats("potion_small") is None


def test_loot_keeps_negative_bonuses_and_never_weakens(monkeypatch) -> None:
    from cursed_descent import dungeon
    from cursed_descent.item_store import base_stats
    monkeypatch.setattr(dungeon.random, "uniform", lambda low, high: high)
    stats = dungeon.loot_stats("cursed_plate")
    assert stats["bonus"] == base_stats("cursed_plate")["bonus"]
    assert stats["armor"] >= base_stats("cursed_plate")["armor"]


def test_given_loot_carries_its_stats_to_the_character() -> None:
    from cursed_descent import dungeon
    from cursed_descent.formulas import equipped_items
    from cursed_descent.models import Player
    hero = Player(name="Hero", gender="Male")
    dungeon.give_item(hero, "war_axe")
    item = hero.inventory[-1]
    assert item.stats["damage"] >= ITEMS["war_axe"]["damage"]
    assert item.creator == "dungeon"
    hero.equipment["weapon"] = hero.inventory.pop()
    assert equipped_items(hero)[0]["damage"] == item.stats["damage"]


def test_lingerie_sets_cover_distinct_slots_and_fit_their_gender() -> None:
    for set_id, side in (("boudoir", "lady"), ("silk_leather", "gent")):
        pieces = [item for item in ITEMS.values() if item.get("set") == set_id]
        assert len(pieces) == 6
        assert len({item["slot"] for item in pieces}) == 6
        assert all(item["for"] == side for item in pieces)
    lingerie = [item for item in ITEMS.values() if item["slot"] == "lingerie"]
    assert {item.get("for", "both") for item in lingerie} == {"lady", "gent", "both"}
    assert len(lingerie) >= 20


def test_equip_refusal_names_the_wrong_gender(tmp_path) -> None:
    from cursed_descent.formulas import wear_refusal
    from cursed_descent.items import Item
    from cursed_descent.models import Player
    hero = Player(name="Hero", gender="Male")
    lady_id = next(key for key, item in ITEMS.items()
                   if item.get("for") == "lady" and "requires" not in item
                   and item["slot"] != "consumable")
    text = wear_refusal(hero, Item(lady_id))
    assert "ladies" in text and "Male" in text


def test_selling_into_a_full_shelf_donates_the_oldest_piece(
        tmp_path:Path) -> None:
    from cursed_descent.items import Item
    from cursed_descent.models import Player
    from cursed_descent.shop_system import MAX_STOCK
    shop = make_shop(tmp_path, SMITH)
    weapons = [key for key in ITEMS if category_of(key) == "weapons"
               and "smith" in ITEMS[key].get("shops", ())]
    shop.stock["weapons"] = weapons[:MAX_STOCK]
    spare = next(key for key in weapons if key not in shop.stock["weapons"])
    hero = Player(name="Hero", gender="Male")
    hero.inventory = [Item(spare)]
    reply = texts(shop.sell(hero, "1"))
    assert "donated" in reply
    assert len(shop.stock["weapons"]) == MAX_STOCK
    assert weapons[0] not in shop.stock["weapons"]
    assert spare in shop.stock["weapons"]


def test_sold_consumables_are_donated(tmp_path:Path) -> None:
    from cursed_descent.items import Item
    from cursed_descent.models import Player
    shop = make_shop(tmp_path, VELVET)
    hero = Player(name="Hero", gender="Male")
    hero.inventory = [Item("potion_small")]
    reply = texts(shop.sell(hero, "1"))
    assert "donated" in reply and not hero.inventory

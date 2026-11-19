from pathlib import Path

from cursed_descent.item_store import ItemStore, allowed_for


def test_equipment_gets_unique_ids_and_template_defaults(
        empty_data_path:Path) -> None:
    store = ItemStore(empty_data_path)
    first = store.create("domina_whip", "bev", "Blackhide")
    second = store.create("domina_whip", "bev", "Blackhide")
    assert first != second
    record = store.get(first)
    assert record["owner"] == "bev" and record["creator"] == "Blackhide"
    assert record["stats"]["damage"] == 18
    assert record["name"] == "Domina's Bullwhip"
    assert record["for"] == "both"


def test_identical_consumables_share_one_id(empty_data_path:Path) -> None:
    store = ItemStore(empty_data_path)
    first = store.create("potion_small", "bev", "shop")
    second = store.create("potion_small", "bev", "shop")
    assert first == second


def test_same_consumable_of_other_owner_is_another_object(
        empty_data_path:Path) -> None:
    store = ItemStore(empty_data_path)
    mine = store.create("potion_small", "bev", "shop")
    theirs = store.create("potion_small", "galactica", "shop")
    assert mine != theirs
    assert store.transfer(mine, "galactica") == theirs
    assert store.get(mine)["owner"] == "bev"


def test_transfer_changes_owner_but_keeps_gear_id_and_creator(
        empty_data_path:Path) -> None:
    store = ItemStore(empty_data_path)
    item = store.create("domina_whip", "dead_hero", "dungeon")
    assert store.transfer(item, "bev") == item
    record = store.get(item)
    assert record["owner"] == "bev" and record["creator"] == "dungeon"


def test_improve_changes_stats_of_one_exemplar_only(
        empty_data_path:Path) -> None:
    store = ItemStore(empty_data_path)
    first = store.create("domina_whip", "bev", "shop")
    second = store.create("domina_whip", "bev", "shop")
    assert store.improve(first, {"damage": 3})
    assert store.get(first)["stats"]["damage"] == 21
    assert store.get(second)["stats"]["damage"] == 18
    assert not store.improve(store.create("potion_small", "bev", "shop"),
                             {"heal": 1})


def test_items_survive_a_new_store_instance(empty_data_path:Path) -> None:
    item = ItemStore(empty_data_path).create("domina_whip", "bev", "shop")
    again = ItemStore(empty_data_path)
    assert again.get(item)["owner"] == "bev"
    assert again.owned_by("bev") == [item]
    assert again.orphans(set()) == [item]
    assert again.orphans({item}) == []
    assert again.remove(item) and not again.exists(item)


def test_restriction_gent_lady_both() -> None:
    for gender in ("Male", "Male-Herm", "Herm", "Cunt-boy"):
        assert allowed_for("gent", gender)
    for gender in ("Female", "Shemale", "Herm"):
        assert allowed_for("lady", gender)
    for gender in ("Female", "Shemale"):
        assert not allowed_for("gent", gender)
    for gender in ("Male", "Male-Herm", "Cunt-boy"):
        assert not allowed_for("lady", gender)
    for gender in ("Transgender", "None"):
        assert allowed_for("gent", gender) and allowed_for("lady", gender)
    assert allowed_for("both", "Male") and allowed_for("both", "Female")


def make_hero(name:str="Hero", gender:str="Male"):
    from cursed_descent.models import Player
    return Player(name=name, gender=gender)


def test_saving_binds_worn_gear_to_a_record(empty_data_path:Path) -> None:
    from cursed_descent.storage import PlayerRepository
    repository = PlayerRepository(empty_data_path)
    hero = make_hero()
    hero.equipment["weapon"] = "domina_whip"
    repository.add(hero)
    worn = hero.equipment["weapon"]
    assert worn.iid
    record = repository.items.get(worn.iid)
    assert record["owner"] == hero.id and record["template"] == "domina_whip"
    assert record["stats"]["damage"] == 18


def test_worn_gear_keeps_its_id_and_stats_after_reload(
        empty_data_path:Path) -> None:
    from cursed_descent.storage import PlayerRepository
    repository = PlayerRepository(empty_data_path)
    hero = make_hero()
    hero.equipment["weapon"] = "domina_whip"
    repository.add(hero)
    iid = hero.equipment["weapon"].iid
    repository.items.improve(iid, {"damage": 4})
    again = PlayerRepository(empty_data_path).load("Hero")
    assert again.equipment["weapon"].iid == iid
    assert again.equipment["weapon"].stats["damage"] == 22


def test_improved_stats_count_in_equipped_items(
        empty_data_path:Path) -> None:
    from cursed_descent.formulas import equipped_items
    from cursed_descent.storage import PlayerRepository
    repository = PlayerRepository(empty_data_path)
    hero = make_hero()
    hero.equipment["weapon"] = "domina_whip"
    repository.add(hero)
    repository.items.improve(hero.equipment["weapon"].iid, {"damage": 2})
    repository.items.pull(hero.equipment["weapon"])
    assert equipped_items(hero)[0]["damage"] == 20


def test_gear_identity_survives_unequip_and_wear(
        empty_data_path:Path) -> None:
    from cursed_descent.storage import PlayerRepository
    repository = PlayerRepository(empty_data_path)
    hero = make_hero()
    hero.equipment["weapon"] = "domina_whip"
    repository.add(hero)
    worn = hero.equipment["weapon"]
    hero.equipment["weapon"] = None
    hero.inventory.append(worn)
    repository.save(hero)
    again = PlayerRepository(empty_data_path).load("Hero")
    bag = [item for item in again.inventory if item == "domina_whip"]
    assert bag and bag[0].iid == worn.iid


def test_can_wear_respects_the_item_restriction() -> None:
    from cursed_descent.formulas import can_wear
    from cursed_descent.items import Item
    lady_sword = Item("rusty_sword", restriction="lady")
    gent_sword = Item("rusty_sword", restriction="gent")
    assert can_wear(make_hero("A", "Female"), lady_sword)
    assert not can_wear(make_hero("B", "Male"), lady_sword)
    assert can_wear(make_hero("C", "Male"), gent_sword)
    assert not can_wear(make_hero("D", "Shemale"), gent_sword)
    assert can_wear(make_hero("E", "Male"), Item("rusty_sword"))


def test_inventory_is_saved_as_stacks_of_ids(empty_data_path:Path) -> None:
    import json
    from cursed_descent.storage import PlayerRepository
    repository = PlayerRepository(empty_data_path)
    hero = make_hero()
    hero.inventory = ["potion_small", "potion_small", "potion_small",
                      "rusty_sword"]
    repository.add(hero)
    saved = json.loads(repository.save_path(hero).read_text())["inventory"]
    stack = next(entry for entry in saved if entry["id"] == "potion_small")
    assert stack["n"] == 3 and stack["iid"]
    sword = next(entry for entry in saved if entry["id"] == "rusty_sword")
    assert sword.get("n", 1) == 1 and sword["iid"]
    again = PlayerRepository(empty_data_path).load("Hero")
    assert [str(item) for item in again.inventory].count("potion_small") == 3
    assert len({item.iid for item in again.inventory
                if item == "potion_small"}) == 1


def test_same_potion_of_two_owners_gets_two_ids(
        empty_data_path:Path) -> None:
    from cursed_descent.storage import PlayerRepository
    repository = PlayerRepository(empty_data_path)
    first, second = make_hero("Bev"), make_hero("Galactica")
    first.inventory = ["potion_small"]
    second.inventory = ["potion_small"]
    repository.add(first)
    repository.add(second)
    assert first.inventory[0].iid != second.inventory[0].iid


def test_picking_up_foreign_gear_changes_the_owner(
        empty_data_path:Path) -> None:
    from cursed_descent.storage import PlayerRepository
    repository = PlayerRepository(empty_data_path)
    first, second = make_hero("Bev"), make_hero("Galactica")
    first.inventory = ["rusty_sword"]
    repository.add(first)
    sword = first.inventory.pop()
    repository.save(first)
    second.inventory.append(sword)
    repository.add(second)
    record = repository.items.get(sword.iid)
    assert record["owner"] == second.id
    assert record["creator"] == "shop"


def test_item_report_shows_creator_and_restriction(
        empty_data_path:Path) -> None:
    from cursed_descent.item_report import item_report
    from cursed_descent.items import Item
    from cursed_descent.storage import PlayerRepository
    repository = PlayerRepository(empty_data_path)
    hero = make_hero()
    hero.inventory = [Item("rusty_sword", creator="Blackhide",
                           restriction="gent")]
    repository.add(hero)
    text = "\n".join(item_report(hero, "rusty_sword", repository))
    assert "Made by Blackhide" in text
    assert "Made for gents only" in text


def test_enchanting_keeps_the_identity_of_the_item(
        empty_data_path:Path) -> None:
    import random
    from cursed_descent.items import Item
    from cursed_descent.locations.mage_tower import enchantments as mage
    from cursed_descent.storage import PlayerRepository
    repository = PlayerRepository(empty_data_path)
    hero = make_hero()
    hero.equipment["weapon"] = Item("rusty_sword", creator="smith")
    repository.add(hero)
    iid = hero.equipment["weapon"].iid
    mage.create(hero, "rusty_sword", 2, "plain", random.Random(1))
    repository.save(hero)
    worn = hero.equipment["weapon"]
    record = repository.items.get(iid)
    assert worn.iid == iid and worn != "rusty_sword"
    assert record["creator"] == "smith" and record["owner"] == hero.id
    assert record["template"] == str(worn)
    assert record["stats"]["damage"] > 0


def test_purge_removes_only_unreferenced_records(
        empty_data_path:Path) -> None:
    from cursed_descent.storage import PlayerRepository
    repository = PlayerRepository(empty_data_path)
    hero = make_hero()
    hero.equipment["weapon"] = "domina_whip"
    hero.inventory = ["rusty_sword"]
    repository.add(hero)
    stray = repository.items.create("domina_whip", "nobody", "dungeon")
    kept = {hero.equipment["weapon"].iid, hero.inventory[0].iid}
    assert repository.items.purge(empty_data_path) == [stray]
    assert all(repository.items.exists(item_id) for item_id in kept)
    assert not repository.items.exists(stray)


def test_items_debug_command_reports_and_purges(data_path:Path) -> None:
    from cursed_descent.controller import GameController
    controller = GameController(data_path, debug=True)
    controller.repository.items.create("domina_whip", "nobody", "dungeon")
    report = controller.handle("kerl", "!items")[0].text
    assert "not referenced" in report
    done = controller.handle("kerl", "!items purge")[0].text
    assert done.startswith("Removed")
    assert controller.repository.items.orphans(
        controller.repository.items.referenced(data_path)) == []


def test_total_stats_show_base_and_item_bonus() -> None:
    from cursed_descent.formulas import stat_total_text, totals_line
    from cursed_descent.items import Item
    hero = make_hero()
    plain = stat_total_text(hero, "strength")
    hero.equipment["weapon"] = Item("domina_whip")
    text = stat_total_text(hero, "strength")
    base = hero.stats["strength"]
    assert plain.endswith(str(base))
    assert f"({base} +3)" in text and f"{base + 3}" in text
    assert totals_line(hero).startswith("Weapon 18 |")

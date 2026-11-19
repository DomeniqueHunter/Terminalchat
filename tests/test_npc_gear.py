import json
from pathlib import Path

from cursed_descent.content import ITEMS
from cursed_descent.controller import GameController
from cursed_descent.settings import PROTOTYPES, ensure_loaded
from tests.npc_files import npc_file, npc_keys


def gear_ids() -> set[str]:
    ensure_loaded()
    return {worn["id"] for record in PROTOTYPES.values()
            for worn in record["equipment"].values() if worn}


def test_every_npc_wears_something_and_the_items_exist() -> None:
    ensure_loaded()
    for key, record in PROTOTYPES.items():
        worn = {slot: item for slot, item in record["equipment"].items()
                if item}
        assert worn, key
        for slot, item in worn.items():
            template = ITEMS[item["id"]]
            assert template["slot"] == slot, (key, item["id"])
            assert item["by"], item["id"]


def test_npc_gear_is_never_sold_or_looted() -> None:
    for item_id in gear_ids():
        template = ITEMS[item_id]
        assert template["no_loot"] is True and not template["shops"]


def test_seeded_npcs_carry_their_gear_with_a_creator(tmp_path:Path) -> None:
    controller = GameController(tmp_path)
    gorm = controller.repository.load("Gorm")
    assert gorm.equipment["weapon"] == "old_gorm_mast_length_fishing_rod"
    assert gorm.equipment["weapon"].creator == "Gorm"
    ottilie = controller.repository.load("Ottilie")
    assert ottilie.equipment["feet"].creator == "Blackhide"
    assert "Wedding Ring" in ITEMS[ottilie.equipment["accessory"]]["name"]
    reginald = controller.repository.load("Sir Reginald")
    assert reginald.equipment["weapon"].creator == "Sir Reginald"
    assert reginald.equipment["head"].creator == "shop"


def test_existing_npc_files_get_their_gear_once(tmp_path:Path) -> None:
    GameController(tmp_path)
    path = npc_file(tmp_path, "Hamhock")
    data = json.loads(path.read_text(encoding="utf-8"))
    data["equipment"] = {slot: None for slot in data["equipment"]}
    own = next(key for key, item in ITEMS.items()
               if item["slot"] == "feet" and "no_loot" not in item)
    data["equipment"]["feet"] = own
    data["profile"].pop("gear")
    path.write_text(json.dumps(data), encoding="utf-8")
    controller = GameController(tmp_path)
    hamhock = controller.repository.load("Hamhock")
    assert hamhock.equipment["weapon"] == "hamhock_old_reliable_cleaver"
    assert hamhock.equipment["feet"] == own
    hamhock.equipment["weapon"] = None
    controller.repository.save(hamhock)
    again = GameController(tmp_path).repository.load("Hamhock")
    assert again.equipment["weapon"] is None


def fight_won(tmp_path:Path, template:str, roll:float):
    import random
    from cursed_descent.dungeon import build_enemy
    from cursed_descent.content import ENEMIES
    from cursed_descent.models import Player
    from cursed_descent.npc_trophies import trophy_lines
    controller = GameController(tmp_path)
    session = controller.session
    hero = Player(name="Hero")
    session.stage = 3
    session.enemies = [build_enemy(1, template, ENEMIES[template], 3)]
    return controller, session, hero, trophy_lines, roll


def test_a_beaten_npc_enemy_can_drop_a_replica_once_per_run(
        tmp_path:Path, monkeypatch) -> None:
    import random
    controller, session, hero, trophy_lines, _ = fight_won(
        tmp_path, "pigman_butcher", 0.0)
    monkeypatch.setattr(random, "random", lambda: 0.0)
    lines = trophy_lines(session, hero)
    assert len(lines) == 1 and "replica" in lines[0]
    replica = str(hero.inventory[-1])
    assert replica.endswith("_replica") and replica.startswith("hamhock_")
    assert ITEMS[replica]["name"].endswith("(Replica)")
    assert trophy_lines(session, hero) == []
    session.trophies.clear()
    again = trophy_lines(session, hero)
    assert "already owns" in again[0] or str(hero.inventory[-1]) != replica
    npc = controller.repository.load("Hamhock")
    assert npc.equipment["weapon"] == "hamhock_old_reliable_cleaver"


def test_no_trophy_when_the_roll_fails_or_the_bag_is_full(
        tmp_path:Path, monkeypatch) -> None:
    import random
    controller, session, hero, trophy_lines, _ = fight_won(
        tmp_path, "pigman_farmer", 0.0)
    monkeypatch.setattr(random, "random", lambda: 0.99)
    before = list(hero.inventory)
    assert trophy_lines(session, hero) == [] and hero.inventory == before
    monkeypatch.setattr(random, "random", lambda: 0.0)
    hero.inventory = ["potion_small"] * hero.bag_size
    assert "bag is full" in trophy_lines(session, hero)[0]
    assert session.trophies == set()


def test_examining_a_named_enemy_shows_what_it_wears(
        tmp_path:Path) -> None:
    from cursed_descent.examine_target import examine_target
    from cursed_descent.models import Player
    controller, session, hero, _, _ = fight_won(
        tmp_path, "pigman_butcher", 0.0)
    reply = examine_target(hero, "Hamhock", session.enemies, [hero],
                           controller.repository, True)[0].text
    assert "Wearing:" in reply and "Cleaver" in reply


def test_gear_descriptions_are_detailed_and_boots_are_for_ladies() -> None:
    for item_id in gear_ids():
        note = ITEMS[item_id].get("note", "")
        assert "Belongs to" not in note, item_id
        if ITEMS[item_id]["rarity"] == "epic":
            assert len(note) > 40, item_id
    boots = ITEMS["baroness_ottilie_polished_black_boots_aldric"]
    assert boots["for"] == "lady" and "Heeled" in boots["name"]
    assert "Aldric" in boots["note"]
    replica = ITEMS["baroness_ottilie_polished_black_boots_aldric_replica"]
    assert boots["note"] in replica["note"]


def test_vesper_wears_ladies_only_platform_heels(tmp_path:Path) -> None:
    item = ITEMS["vesper_overknee_platform_heels"]
    assert item["for"] == "lady" and item["slot"] == "feet"
    assert "twenty-centimetre" in item["note"]
    assert "vesper_overknee_platform_heels_replica" in ITEMS
    GameController(tmp_path)
    path = npc_file(tmp_path, "Madame Vesper")
    data = json.loads(path.read_text(encoding="utf-8"))
    data["equipment"]["feet"] = None
    data["profile"]["gear"] = True
    path.write_text(json.dumps(data), encoding="utf-8")
    vesper = GameController(tmp_path).repository.load(data["name"])
    assert vesper.equipment["feet"] == "vesper_overknee_platform_heels"
    assert vesper.equipment["feet"].creator == "Blackhide"

import json
from pathlib import Path

from cursed_descent.controller import GameController
from cursed_descent.identity import (
    character_key, is_character, new_id, same_character,
)
from cursed_descent.migrations import SCHEMA_VERSION, migrate_player
from cursed_descent.models import Player
from cursed_descent.remains import RemainsLog
from cursed_descent.storage import PlayerRepository


LEGACY = {"name": "Old", "gender": "Male", "equipment": {"armor": None},
          "inventory": ["potion_small"], "deaths": {"goblins": 1}}


def test_new_ids_are_unique() -> None:
    assert len({new_id() for _ in range(100)}) == 100


def test_entry_matches_by_id_before_name() -> None:
    entry = {"name": "Renamed", "char_id": "a1"}
    assert is_character(entry, "a1", "Different")
    assert not is_character(entry, "b2", "Renamed")


def test_legacy_entry_without_id_matches_by_name() -> None:
    entry = {"name": "Lyra"}
    assert is_character(entry, "any", "Lyra")
    assert character_key(entry) == "Lyra"


def test_same_character_across_name_change() -> None:
    first = {"name": "Lyra", "char_id": "a1"}
    second = {"name": "Lyra Dawn", "char_id": "a1"}
    assert same_character(first, second)


def test_migration_adds_version_id_and_names() -> None:
    migrated, changed = migrate_player(dict(LEGACY))
    assert changed and migrated["schema_version"] == SCHEMA_VERSION
    assert migrated["id"] and migrated["first_name"] == ""
    assert migrated["equipment"] == {"chest": None}
    assert migrated["deaths"] == {"breeding": 1}


def test_current_data_is_not_migrated_again() -> None:
    data = Player(name="New").to_dict()
    migrated, changed = migrate_player(data)
    assert not changed and migrated is data


def test_legacy_file_is_upgraded_and_saved_with_stable_id(
        empty_data_path:Path) -> None:
    repository = PlayerRepository(empty_data_path)
    repository.add(Player(name="Old"))
    path = repository.path("Old")
    path.write_text(json.dumps(LEGACY), encoding="utf-8")
    first = PlayerRepository(empty_data_path).load("Old")
    stored = json.loads(path.read_text(encoding="utf-8"))
    assert stored["id"] == first.id
    assert PlayerRepository(empty_data_path).load("Old").id == first.id


def test_repository_finds_player_by_id(empty_data_path:Path) -> None:
    repository = PlayerRepository(empty_data_path)
    player = Player(name="Lyra")
    repository.add(player)
    assert repository.load_by_id(player.id).name == "Lyra"
    assert repository.load_by_id("missing") is None


def test_character_keeps_id_through_revival(controller:GameController) -> None:
    kerl = controller.repository.load("kerl")
    before = kerl.id
    controller.handle("kerl", "!lobby")
    controller.handle("kerl", "!start", now=0.0)
    controller.handle("kerl", "!surrender", now=1.0)
    assert controller.repository.load("kerl").id == before
    assert controller.repository.load_by_id(before) is kerl


def test_remains_record_character_id(controller:GameController) -> None:
    kerl = controller.repository.load("kerl")
    controller.handle("kerl", "!lobby")
    controller.handle("kerl", "!start", now=0.0)
    controller.handle("kerl", "!surrender", now=1.0)
    last = controller.remains.entries[-1]
    assert last["name"] == "kerl" and last["char_id"] == kerl.id


def test_remains_are_backfilled_with_ids(data_path:Path) -> None:
    controller = GameController(data_path)
    ids = controller.repository.id_map()
    known = [entry for entry in controller.remains.entries
             if PlayerRepository.key(entry["name"]) in ids]
    assert known and all(entry.get("char_id") for entry in known)
    assert RemainsLog(data_path).entries[0].get("id")


def test_profile_shows_full_name_and_id(controller:GameController) -> None:
    player = controller.repository.load("kerl")
    player.first_name, player.last_name = "Kerl", "Stone"
    text = controller.handle("kerl", "!profile")[0].text
    assert "Kerl Stone" in text and player.id[:8] in text

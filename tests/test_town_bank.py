import json
from pathlib import Path

from cursed_descent.models import Player
from cursed_descent.town_buildings.bank.ledger import (
    Account, Bank, bank_menu, bank_move,
)
from cursed_descent.towns import START_TOWN, TOWNS, town_text


def hero() -> Player:
    player = Player(name="Hero")
    player.gold = 100
    player.inventory = ["potion_small", "potion_small"]
    return player


def move(player:Player, account:Account, args:list[str],
         deposit:bool=True, in_run:bool=False) -> str:
    return bank_move(player, account, args, deposit, in_run)[0].text


def test_start_town_lists_its_buildings() -> None:
    text = town_text(TOWNS[START_TOWN])
    assert "Last Light" in text
    for command in ("shop", "smith", "clinic", "bank"):
        assert f"[{command}]" in text


def test_every_town_has_bank_smith_and_shop() -> None:
    for town in TOWNS.values():
        if town.wip:
            continue
        needed = {"bank", "smith", "shop"}
        assert needed <= set(town.buildings)


def test_gold_moves_both_ways() -> None:
    player, account = hero(), Account()
    move(player, account, ["gold", "30"])
    assert (player.gold, account.gold) == (70, 30)
    move(player, account, ["gold", "all"], deposit=False)
    assert (player.gold, account.gold) == (100, 0)


def test_gold_overdraw_is_refused() -> None:
    player, account = hero(), Account()
    assert "Not enough" in move(player, account, ["gold", "500"])
    assert player.gold == 100


def test_items_move_both_ways_and_respect_limits() -> None:
    player, account = hero(), Account()
    move(player, account, ["1"])
    assert len(player.inventory) == 1 and len(account.items) == 1
    move(player, account, ["1"], deposit=False)
    assert len(player.inventory) == 2 and account.items == []
    assert "No item" in move(player, account, ["9"])


def test_bank_is_closed_in_a_run() -> None:
    player, account = hero(), Account()
    assert "shut" in move(player, account, ["gold", "5"], in_run=True)
    assert player.gold == 100


def test_menu_shows_stored_things() -> None:
    player, account = hero(), Account()
    move(player, account, ["1"])
    move(player, account, ["gold", "10"])
    text = bank_menu(player, account)[0].text
    assert "1/40" in text and "Stored: 10" in text


def test_bank_lives_in_bank_json_not_in_the_character(tmp_path:Path) -> None:
    player, bank = hero(), Bank(tmp_path)
    account = bank.account(player)
    move(player, account, ["1"])
    move(player, account, ["gold", "20"])
    bank.save()
    saved = json.loads((tmp_path / "bank.json").read_text())
    entry = saved[player.id]
    assert entry["gold"] == 20 and len(entry["items"]) == 1
    sheet = player.to_dict()
    assert "bank_gold" not in sheet and "bank_items" not in sheet
    again = Bank(tmp_path).account(player)
    assert again.gold == 20 and len(again.items) == 1


def test_empty_accounts_are_not_written(tmp_path:Path) -> None:
    bank = Bank(tmp_path)
    bank.account(hero())
    bank.save()
    assert json.loads((tmp_path / "bank.json").read_text()) == {}


def test_commands_work_through_the_controller(controller) -> None:
    controller.handle("Kerl", "!deposit gold 10")
    text = "\n".join(m.text for m in controller.handle("Kerl", "!bank"))
    assert "Stored: 10" in text
    assert "Last Light" in controller.handle("Kerl", "!town")[0].text
    assert (controller.bank.path).exists()


def test_every_town_is_a_folder_named_town_and_race() -> None:
    from pathlib import Path
    import cursed_descent.towns as towns
    folders = sorted(path.name for path in Path(towns.__file__).parent
                     .iterdir() if path.is_dir() and path.name[0] != "_")
    assert folders == sorted(f"{town.key}_{town.race}"
                             for town in TOWNS.values())
    for folder in folders:
        assert (Path(towns.__file__).parent / folder / "town.py").exists()

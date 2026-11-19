import asyncio
import json
from pathlib import Path

from cursed_descent.admin_cli import main
from cursed_descent.web.hub import GameHub


def edit_gold(hub:GameHub, name:str, gold:int) -> None:
    path = hub.controller.repository.path(name)
    data = json.loads(path.read_text(encoding="utf-8"))
    data["gold"] = gold
    path.write_text(json.dumps(data), encoding="utf-8")


def test_all_refresh_reloads_changed_files(data_path:Path) -> None:
    hub = GameHub(data_path)
    repository = hub.controller.repository
    assert repository.load("kerl").gold != 4242
    edit_gold(hub, "kerl", 4242)
    assert repository.load("kerl").gold != 4242
    hub.store.request_refresh("all")
    asyncio.run(hub.process_refreshes())
    assert repository.load("kerl").gold == 4242
    assert hub.store.open_refreshes() == []


def make_account_char(hub:GameHub, name:str) -> None:
    from cursed_descent.models import Player
    serial = hub.store.new_serials(1)[0]
    account = hub.store.register(serial, "Brain", "longpassword")
    hub.controller.repository.add(Player(name=name,
                                         account_id=account.id, gold=5))


def test_an_account_refresh_reloads_only_that_account(
        data_path:Path) -> None:
    hub = GameHub(data_path)
    repository = hub.controller.repository
    make_account_char(hub, "Mine")
    before = repository.load("kerl").gold
    edit_gold(hub, "Mine", 99)
    edit_gold(hub, "kerl", 99)
    request = hub.store.request_refresh("account", "Brain")
    asyncio.run(hub.process_refreshes())
    assert "1 characters reloaded" in hub.store.refresh_result(request)
    assert repository.load("Mine").gold == 99
    assert repository.load("kerl").gold == before


def test_characters_in_a_party_are_skipped(data_path:Path) -> None:
    hub = GameHub(data_path)
    make_account_char(hub, "Mine")
    hero = hub.controller.repository.load("Mine")
    hub.controller.session.party.append(hero)
    edit_gold(hub, "Mine", 99)
    request = hub.store.request_refresh("account", "Brain")
    asyncio.run(hub.process_refreshes())
    assert "skipped (in a party): Mine" in hub.store.refresh_result(request)
    assert hub.controller.repository.load("Mine").gold == 5


def test_the_cli_queues_and_reports_when_the_server_is_silent(
        data_path:Path, capsys, monkeypatch) -> None:
    from cursed_descent import admin_cli
    monkeypatch.setattr(admin_cli, "REFRESH_WAIT_SECONDS", 0.3)
    assert main(["--data", str(data_path), "refresh"]) == 1
    assert main(["--data", str(data_path), "refresh", "--all"]) == 1
    assert "Queued" in capsys.readouterr().err
    hub = GameHub(data_path)
    assert [row["scope"] for row in hub.store.open_refreshes()] == ["all"]

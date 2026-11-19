import time
from pathlib import Path

import pytest

from cursed_descent import admin_cli
from cursed_descent.accounts import (
    PERMANENT_BAN, AccountError, AccountStore, ban_text, parse_duration,
)


@pytest.fixture
def store(tmp_path:Path) -> AccountStore:
    accounts = AccountStore(tmp_path)
    serial = accounts.new_serials(1)[0]
    accounts.register(serial, "Rowdy", "longpassword")
    return accounts


def test_durations_parse() -> None:
    assert parse_duration("30m") == 1800
    assert parse_duration("2h") == 7200
    assert parse_duration("7d") == 604800
    assert parse_duration("perm") == PERMANENT_BAN
    with pytest.raises(AccountError):
        parse_duration("soon")


def test_ban_blocks_and_ends_sessions(store:AccountStore) -> None:
    account = store.by_name("Rowdy")
    token = store.start_session(account.id)
    assert store.ban("Rowdy", 600, "too loud")
    assert store.session_account(token) is None
    banned = store.login("Rowdy", "longpassword")
    assert banned.banned and "too loud" in ban_text(banned)
    assert [entry.name for entry in store.bans()] == ["Rowdy"]


def test_unban_and_expiry(store:AccountStore) -> None:
    store.ban("Rowdy", 600)
    assert store.unban("Rowdy")
    assert not store.by_name("Rowdy").banned
    store.ban("Rowdy", 1)
    store.db.execute("UPDATE accounts SET banned_until = ?",
                     (time.time() - 5,))
    assert store.bans() == []


def test_permanent_text(store:AccountStore) -> None:
    store.ban("Rowdy", PERMANENT_BAN)
    assert "permanently" in ban_text(store.by_name("Rowdy"))


def test_admins_cannot_be_banned_or_kicked(store:AccountStore,
                                           capsys) -> None:
    store.set_admin("Rowdy", 600)
    with pytest.raises(AccountError):
        store.ban("Rowdy", 600)
    assert admin_cli.kick(store, "Rowdy") == 1
    assert "cannot be kicked" in capsys.readouterr().err


def test_cli_ban_unban_list(tmp_path:Path, store:AccountStore, capsys,
                            monkeypatch) -> None:
    monkeypatch.setattr(admin_cli, "REFRESH_WAIT_SECONDS", 0.0)
    code = admin_cli.main(["--data", str(tmp_path), "ban", "Rowdy", "2h",
                           "spam", "again"])
    assert code == 0
    assert admin_cli.main(["--data", str(tmp_path), "bans"]) == 0
    assert "spam again" in capsys.readouterr().out
    assert admin_cli.main(["--data", str(tmp_path), "unban", "Rowdy"]) == 0
    assert admin_cli.main(["--data", str(tmp_path), "bans"]) == 0
    assert "No active bans" in capsys.readouterr().out


def test_old_databases_are_migrated(tmp_path:Path) -> None:
    first = AccountStore(tmp_path)
    first.db.execute("ALTER TABLE accounts DROP COLUMN banned_until")
    first.db.execute("ALTER TABLE accounts DROP COLUMN ban_reason")
    first.close()
    second = AccountStore(tmp_path)
    assert second.bans() == []


def test_banned_login_is_refused(tmp_path:Path) -> None:
    from fastapi.testclient import TestClient
    from cursed_descent.web.app import create_app
    client = TestClient(create_app(tmp_path))
    store = AccountStore(tmp_path)
    store.register(store.new_serials(1)[0], "Rowdy", "longpassword")
    store.ban("Rowdy", 600, "test")
    reply = client.post("/login", data={"name": "Rowdy",
                                        "password": "longpassword"})
    assert reply.status_code == 403 and "banned" in reply.text


def test_kick_closes_the_connections_of_the_account(tmp_path:Path) -> None:
    import asyncio
    from cursed_descent.web.hub import Client, GameHub

    class Socket:
        closed = 0

        async def close(self, code:int=1000) -> None:
            self.closed = code

    hub = GameHub(tmp_path)
    serial = hub.store.new_serials(1)[0]
    account = hub.store.register(serial, "Rowdy", "longpassword")
    socket = Socket()
    hub.clients.append(Client(socket, account=account))
    text = asyncio.run(hub.kick("Rowdy"))
    assert "1 connections closed" in text and socket.closed == 4401
    assert asyncio.run(hub.kick("Nobody")).startswith("No account")

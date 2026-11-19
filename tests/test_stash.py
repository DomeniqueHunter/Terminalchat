import asyncio
from pathlib import Path

from cursed_descent.web import home, stash, views
from cursed_descent.web.hub import Client, GameHub
from tests.test_web_log_scope import connect


def give(hub:GameHub, gold:int=500, items:tuple[str, ...]=()) -> None:
    player = hub.controller.repository.load("kerl")
    player.gold = gold
    player.inventory = list(items)
    hub.controller.repository.save(player)


def at_bank(hub:GameHub) -> None:
    hub.controller.handle("kerl", "!bank")


def send(hub:GameHub, client:Client, text:str) -> None:
    asyncio.run(hub.handle(client, f'{{"action": "cmd", "viewer": "kerl", '
                                   f'"text": "{text}"}}'))


def first_item(hub:GameHub) -> str:
    from cursed_descent.content import ITEMS
    return next(key for key, item in ITEMS.items()
                if item.get("slot") == "consumable")


def test_bank_panel_is_only_a_summary_with_an_inventory_button(
        data_path:Path) -> None:
    hub = GameHub(data_path)
    at_bank(hub)
    player = hub.controller.repository.load("kerl")
    panel = views.location_panel(hub.controller, player)[0]
    commands = [b.command for b in panel.buttons]
    assert commands[0] == "!stash bank"
    assert not any("deposit" in c or "withdraw" in c for c in commands)
    assert panel.lines[-2].startswith("Gold:")
    assert panel.lines[-1].startswith("Items:")
    assert [section.title for section in panel.sections] == ["Locals"]
    clerk = panel.sections[0].sections[0]
    assert any(b.command.startswith("!talk") for b in clerk.buttons)


def test_inventory_overlay_moves_items_and_gold_both_ways(
        data_path:Path) -> None:
    hub = GameHub(data_path)
    item = first_item(hub)
    give(hub, 500, (item,))
    at_bank(hub)
    client = connect(hub, "kerl")
    send(hub, client, "!stash bank")
    assert client.stash == "bank"
    page = hub.panels_for(client)
    assert 'id="stash-backdrop"' in page and "Your bag" in page
    assert "Vault" in page and "!deposit 1" in page
    send(hub, client, "!deposit 1")
    send(hub, client, "!deposit gold 100")
    player = hub.controller.repository.load("kerl")
    account = hub.controller.town.bank.account(player)
    assert account.items == [item] and account.gold == 100
    assert player.gold == 400 and player.inventory == []
    assert "!withdraw 1" in hub.panels_for(client)
    send(hub, client, "!withdraw 1")
    send(hub, client, "!withdraw gold all")
    player = hub.controller.repository.load("kerl")
    assert player.inventory == [item] and player.gold == 500
    send(hub, client, "!stash close")
    assert 'id="stash-backdrop"' not in hub.panels_for(client)


def test_bank_overlay_closes_when_you_leave_the_bank(
        data_path:Path) -> None:
    hub = GameHub(data_path)
    at_bank(hub)
    client = connect(hub, "kerl")
    send(hub, client, "!stash bank")
    hub.controller.handle("kerl", "!town")
    assert 'id="stash-backdrop"' not in hub.panels_for(client)
    assert client.stash == ""


def test_the_bank_belongs_to_one_character_in_every_town(
        data_path:Path) -> None:
    hub = GameHub(data_path)
    controller = hub.controller
    player = controller.repository.load("kerl")
    account = controller.town.bank.account(player)
    account.gold = 77
    player.profile["town"] = "dusk_hollow"
    other = controller.repository.load("Galactica")
    assert controller.town.bank.account(player).gold == 77
    assert controller.town.bank.account(other).gold != 77


def test_house_chest_overlay_for_the_owner_in_town_only(
        data_path:Path) -> None:
    hub = GameHub(data_path)
    player = hub.controller.repository.load("kerl")
    player.gold = 10 ** 7
    hub.controller.repository.save(player)
    hub.controller.handle("kerl", "!home")
    key = next(b.command for s in views.location_panel(
        hub.controller, player)[0].sections for ss in s.sections
        for b in ss.buttons if b.command.startswith("!home buy"))
    hub.controller.handle("kerl", key)
    player = hub.controller.repository.load("kerl")
    panel = views.location_panel(hub.controller, player)[0]
    chest = next(s for s in panel.sections if s.title == "📦 Chest")
    assert [b.command for b in chest.buttons] == ["!stash home"]
    item = first_item(hub)
    player.inventory = [item]
    hub.controller.repository.save(player)
    client = connect(hub, "kerl")
    send(hub, client, "!stash home")
    page = hub.panels_for(client)
    assert "House chest" in page and "!home store 1" in page
    send(hub, client, "!home store 1")
    send(hub, client, "!home store gold 100")
    player = hub.controller.repository.load("kerl")
    account = stash.account_of(hub.controller, player, "home")
    assert account.items == [item] and account.gold == 100
    assert "!home take 1" in hub.panels_for(client)
    assert stash.overlay(hub.controller, player, "bank") is None

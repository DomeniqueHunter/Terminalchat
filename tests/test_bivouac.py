import random

from cursed_descent.config import SHOP_CONSUMABLES
from cursed_descent.content import ITEMS
from cursed_descent.controller import GameController
from cursed_descent.locations.bivouac.location import light_chance


def texts(messages) -> str:
    return "\n".join(message.text for message in messages)


def at_camp(controller:GameController) -> None:
    controller.handle("kerl", "!lobby", now=0.0)
    controller.handle("kerl", "!start", now=1.0)
    controller.session.stage = 5
    controller.session.events.offer_location("bivouac", 2.0)


def test_camp_offers_gather_rest_and_depart(
        controller:GameController) -> None:
    at_camp(controller)
    options = controller.session.events.available()
    assert "gather" in options and "rest" in options
    assert "depart" in options and "light" not in options


def test_firewood_is_sold_in_the_shop() -> None:
    assert "firewood" in SHOP_CONSUMABLES and "firewood" in ITEMS


def test_gathering_gives_wood_once_per_member(
        controller:GameController, monkeypatch) -> None:
    at_camp(controller)
    controller.session.member("kerl").inventory.clear()
    monkeypatch.setattr(random, "random", lambda: 0.5)
    reply = texts(controller.handle("kerl", "!gather", now=3.0))
    assert "wood" in reply
    assert "firewood" in controller.session.member("kerl").inventory
    assert "gather" not in controller.session.events.available()


def test_lighting_needs_wood_and_makes_cooking_and_talk_possible(
        controller:GameController, monkeypatch) -> None:
    at_camp(controller)
    session = controller.session
    reply = texts(controller.handle("kerl", "!light", now=3.0))
    assert "doesn't work here" in reply
    session.member("kerl").inventory[:] = ["firewood"]
    monkeypatch.setattr(random, "random", lambda: 0.0)
    reply = texts(controller.handle("kerl", "!light", now=4.0))
    assert "fire catches" in reply
    assert "firewood" not in session.member("kerl").inventory
    assert "talk" in session.events.available()


def test_failed_lighting_wastes_the_wood(controller:GameController,
                                         monkeypatch) -> None:
    at_camp(controller)
    session = controller.session
    session.member("kerl").inventory.append("firewood")
    monkeypatch.setattr(random, "random", lambda: 0.999)
    controller.handle("kerl", "!light", now=3.0)
    assert "firewood" not in session.member("kerl").inventory
    assert not session.events.event["data"]["lit"]


def test_resting_by_the_fire_heals_and_clears_sleep(
        controller:GameController, monkeypatch) -> None:
    at_camp(controller)
    session = controller.session
    player = session.member("kerl")
    player.hp = 1
    player.needs["sleep"] = 80
    player.inventory.append("firewood")
    monkeypatch.setattr(random, "random", lambda: 0.0)
    controller.handle("kerl", "!light", now=3.0)
    monkeypatch.setattr(random, "random", lambda: 0.5)
    controller.handle("kerl", "!rest", now=4.0)
    assert player.hp > 1 and player.needs["sleep"] == 0


def test_cold_rest_can_be_ambushed(controller:GameController,
                                   monkeypatch) -> None:
    at_camp(controller)
    session = controller.session
    player = session.member("kerl")
    player.hp = 1
    monkeypatch.setattr(random, "random", lambda: 0.0)
    reply = texts(controller.handle("kerl", "!rest", now=3.0))
    assert "wakes" in reply and player.hp == 1


def test_light_chance_grows_with_agility_and_intelligence(
        controller:GameController) -> None:
    at_camp(controller)
    player = controller.session.member("kerl")
    low = light_chance([player])
    player.stats["agility"] += 5
    assert light_chance([player]) > low

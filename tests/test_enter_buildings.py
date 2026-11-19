import pytest

from cursed_descent.controller import GameController

from tests.ready import confirm


def texts(messages) -> str:
    return "\n".join(message.text for message in messages)


def at_location(controller:GameController, kind:str) -> None:
    controller.handle("kerl", "!lobby", now=0.0)
    controller.handle("kerl", "!start", now=1.0)
    confirm(controller, 1.0)
    controller.session.stage = 8
    events = controller.session.events
    if kind in ("boutique", "adept"):
        controller.session.state = "event"
        controller.session.deadline = 2.0
        events.event = {"kind": kind, "used": set(), "data": {}}
        events.offer_boutique() if kind == "boutique" else events.offer_adept()
        return
    events.offer_location(kind, 2.0)


@pytest.mark.parametrize("kind,phrase", [
    ("farm", "muddy yard"), ("butcher_shop", "sawdust")])
def test_outside_offers_enter_before_the_goods(
        controller:GameController, kind:str, phrase:str) -> None:
    at_location(controller, kind)
    options = controller.session.events.available()
    assert options == ["enter", "examine", "pass"]
    assert not any(option.startswith("buy") for option in options)
    messages = controller.handle("kerl", "!enter", now=3.0)
    assert phrase in texts(messages)
    assert any(option.startswith("buy")
               for option in controller.session.events.available())


@pytest.mark.parametrize("kind", ["farm", "butcher_shop"])
def test_buildings_can_be_left_from_outside(
        controller:GameController, kind:str) -> None:
    at_location(controller, kind)
    controller.handle("kerl", "!pass", now=3.0)
    assert controller.session.state != "event"


@pytest.mark.parametrize("kind", ["farm", "butcher_shop", "boutique", "hut"])
def test_every_building_offers_enter_examine_pass(
        controller:GameController, kind:str) -> None:
    at_location(controller, kind)
    assert controller.session.events.available() == [
        "enter", "examine", "pass"]


@pytest.mark.parametrize("kind", ["boutique"])
def test_enter_opens_the_inside_and_pass_leaves(
        controller:GameController, kind:str) -> None:
    at_location(controller, kind)
    before = controller.session.events.available()
    messages = controller.handle("kerl", "!enter", now=3.0)
    assert messages and controller.session.state == "event"
    assert not controller.session.events.outside()
    assert controller.session.events.available() != before


@pytest.mark.parametrize("kind", ["boutique", "couch", "adept", "farm",
                                  "butcher_shop", "hut", "brewery"])
def test_time_stands_still_in_every_location(
        controller:GameController, kind:str) -> None:
    at_location(controller, kind)
    assert controller.session.events.paused()
    controller.session.events.action("kerl", "pass", 5000.0)
    assert controller.session.deadline >= 5000.0


def test_outside_text_has_no_timer(controller:GameController) -> None:
    at_location(controller, "couch")
    lines = controller.session.events.offer_venue("couch")
    assert "no time limit" in lines[-1] and "(40 s)" not in lines[-1]


@pytest.mark.parametrize("kind", ["couch", "adept", "wardrobe", "throne"])
def test_things_in_the_corridor_need_no_door(
        controller:GameController, kind:str) -> None:
    at_location(controller, kind)
    options = controller.session.events.available()
    assert "enter" not in options
    assert "examine" in options and "depart" in options
    assert not controller.session.events.outside()
    assert texts(controller.handle("kerl", "!examine", now=3.0)
                 ).startswith("🔎")
    controller.handle("kerl", "!depart", now=4.0)
    assert controller.session.state != "event"


def test_work_on_the_farm_explains_that_a_role_must_be_chosen_first(
        controller:GameController) -> None:
    at_location(controller, "farm")
    controller.handle("kerl", "!enter", now=3.0)
    reply = texts(controller.handle("kerl", "!work", now=4.0))
    assert "work horse" in reply and "doesn't work here" not in reply
    controller.handle("kerl", "!work horse", now=5.0)
    assert "shift turn 1" in texts(controller.handle("kerl", "!work",
                                                     now=6.0))


@pytest.mark.parametrize("kind", ["hut", "butcher_shop", "farm", "boutique"])
def test_examine_describes_the_place_outside_and_inside(
        controller:GameController, kind:str) -> None:
    at_location(controller, kind)
    outside = texts(controller.handle("kerl", "!examine", now=3.0))
    assert outside.startswith("🔎") and "nothing here worth" not in outside
    controller.handle("kerl", "!enter", now=4.0)
    inside = texts(controller.handle("kerl", "!examine", now=5.0))
    assert inside.startswith("🔎") and inside != outside
    assert "nothing here worth" not in inside


@pytest.mark.parametrize("kind,owner", [
    ("butcher_shop", "Hamhock"), ("farm", "Old Trotter"),
    ("boutique", "Madame Vesper")])
def test_examine_shows_the_owner_from_the_npc_file(
        controller:GameController, kind:str, owner:str) -> None:
    at_location(controller, kind)
    assert f"{owner}" in texts(controller.handle("kerl", "!examine",
                                                  now=3.0))


@pytest.mark.parametrize("kind", ["butcher_shop", "boutique"])
def test_every_event_place_offers_work_once_inside(
        controller:GameController, kind:str) -> None:
    at_location(controller, kind)
    assert not any(o.startswith("work")
                   for o in controller.session.events.available())
    controller.handle("kerl", "!enter", now=3.0)
    options = controller.session.events.available()
    assert sum(o.startswith("work ") for o in options) == 3
    listing = texts(controller.handle("kerl", "!work", now=4.0))
    assert "has work" in listing


@pytest.mark.parametrize("kind", ["butcher_shop", "boutique"])
def test_a_shift_pays_or_the_owner_keeps_the_worker(
        controller:GameController, kind:str, monkeypatch) -> None:
    import random as random_module
    at_location(controller, kind)
    controller.handle("kerl", "!enter", now=3.0)
    role = next(o.split()[1] for o in controller.session.events.available()
                if o.startswith("work "))
    gold = controller.repository.load("kerl").gold
    monkeypatch.setattr(random_module, "random", lambda: 0.99)
    reply = texts(controller.handle("kerl", f"!work {role}", now=4.0))
    assert "The shift is over" in reply
    assert controller.repository.load("kerl").gold > gold
    again = texts(controller.handle("kerl", f"!work {role}", now=5.0))
    assert "One shift a day" in again


@pytest.mark.parametrize("kind", ["butcher_shop", "boutique"])
def test_a_kept_worker_meets_the_fate(
        controller:GameController, kind:str, monkeypatch) -> None:
    import random as random_module
    at_location(controller, kind)
    controller.handle("kerl", "!enter", now=3.0)
    monkeypatch.setattr(random_module, "random", lambda: 0.0)
    role = next(o.split()[1] for o in controller.session.events.available()
                if o.startswith("work "))
    reply = texts(controller.handle("kerl", f"!work {role}", now=4.0))
    assert "💀" in reply


def test_the_hunter_is_out_and_the_party_can_eat_in_his_hut(
        controller:GameController, monkeypatch) -> None:
    import random as random_module
    at_location(controller, "hut")
    controller.handle("kerl", "!enter", now=3.0)
    options = controller.session.events.available()
    assert "eat" in options and not any(o.startswith("work") for o in options)
    assert "Sir Reginald Thornbury" not in texts(
        controller.handle("kerl", "!examine", now=4.0))
    monkeypatch.setattr(random_module, "random", lambda: 0.99)
    assert "raids Reginald's larder" in texts(
        controller.handle("kerl", "!eat", now=5.0))


def test_eating_in_the_hut_can_bring_reginald_back(
        controller:GameController, monkeypatch) -> None:
    import random as random_module
    at_location(controller, "hut")
    controller.handle("kerl", "!enter", now=3.0)
    monkeypatch.setattr(random_module, "random", lambda: 0.0)
    reply = texts(controller.handle("kerl", "!eat", now=4.0))
    assert "PORT" in reply and controller.session.state == "combat"


def test_a_freshly_brewed_adventurer_can_be_drunk_from_the_tap(
        controller:GameController, monkeypatch) -> None:
    session = controller.session
    controller.handle("kerl", "!lobby", now=0.0)
    controller.handle("Galactica", "!join", now=0.5)
    controller.handle("kerl", "!start", now=1.0)
    confirm(controller, 1.0)
    session.events.offer_location("brewery", 2.0)
    controller.handle("kerl", "!enter", now=3.0)
    assert "tap" not in session.events.available()
    assert "Nothing fresh yet" in texts(controller.handle("kerl", "!tap", now=3.5))
    session.events.brewery_sell_self(session.member("Galactica"), 4.0,
                                     forced=True)
    assert "tap" in session.events.available()
    kerl = session.member("kerl")
    kerl.hp = 1
    reply = texts(controller.handle("kerl", "!tap", now=5.0))
    assert "Galactica" in reply and kerl.hp > 1
    assert "Not again so soon" in texts(
        controller.handle("kerl", "!tap", now=6.0))


def test_the_party_can_cook_raw_meat_at_reginalds_hearth(
        controller:GameController, monkeypatch) -> None:
    import random as random_module
    from cursed_descent.content import ITEMS
    raw = next(item_id for item_id, item in ITEMS.items()
               if item.get("raw_meat"))
    at_location(controller, "hut")
    controller.handle("kerl", "!enter", now=3.0)
    assert "cook" not in controller.session.events.available()
    controller.session.member("kerl").inventory.append(raw)
    assert "cook" in controller.session.events.available()
    monkeypatch.setattr(random_module, "random", lambda: 0.99)
    reply = texts(controller.handle("kerl", "!cook", now=4.0))
    assert "hearth" in reply
    assert not any(ITEMS[item_id].get("raw_meat") for item_id in
                   controller.session.member("kerl").inventory)
    assert "cook" not in controller.session.events.available()


def test_cooking_in_the_hut_can_bring_reginald_back(
        controller:GameController, monkeypatch) -> None:
    import random as random_module
    from cursed_descent.content import ITEMS
    raw = next(item_id for item_id, item in ITEMS.items()
               if item.get("raw_meat"))
    at_location(controller, "hut")
    controller.handle("kerl", "!enter", now=3.0)
    controller.session.member("kerl").inventory.append(raw)
    monkeypatch.setattr(random_module, "random", lambda: 0.0)
    reply = texts(controller.handle("kerl", "!cook", now=4.0))
    assert "my hearth" in reply.lower() and controller.session.state == "combat"


def test_give_at_the_campfire_goes_to_the_wanderer_not_to_a_player(
        controller:GameController) -> None:
    controller.handle("kerl", "!lobby", now=0.0)
    controller.handle("kerl", "!start", now=1.0)
    confirm(controller, 1.0)
    session = controller.session
    session.state = "event"
    session.deadline = 99.0
    session.events.event = {"kind": "wanderer", "used": set(), "data": {}}
    session.events.offer_wanderer()
    assert "give" in session.events.available()
    kerl = session.member("kerl")
    kerl.inventory = ["potion_small"]
    reply = texts(controller.handle("kerl", "!give 1", now=2.0))
    assert "nobody like that" not in reply and "Usage" not in reply
    assert "give" in session.events.event["used"]


def test_no_tap_without_a_fresh_brew_even_if_astrid_brewed_before(
        controller:GameController) -> None:
    session = controller.session
    controller.handle("kerl", "!lobby", now=0.0)
    controller.handle("Galactica", "!join", now=0.5)
    controller.handle("kerl", "!start", now=1.0)
    confirm(controller, 1.0)
    session.events.offer_location("brewery", 2.0)
    controller.handle("kerl", "!enter", now=3.0)
    session.events.brewery_sell_self(session.member("Galactica"), 4.0,
                                     forced=True)
    controller.handle("kerl", "!depart", now=5.0)
    session.events.offer_location("brewery", 6.0)
    controller.handle("kerl", "!enter", now=7.0)
    assert "tap" not in session.events.available()
    assert "Nothing fresh yet" in texts(controller.handle("kerl", "!tap",
                                                          now=8.0))


def test_the_farm_roles_are_work_buttons_and_rent_still_works(
        controller:GameController) -> None:
    at_location(controller, "farm")
    controller.handle("kerl", "!enter", now=3.0)
    options = controller.session.events.available()
    assert "work horse" in options and "rent horse" not in options
    reply = texts(controller.handle("kerl", "!rent horse", now=4.0))
    assert "shift" in reply.lower()

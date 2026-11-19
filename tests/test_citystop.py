import random

from cursed_descent.config import CITY_STOP_EVERY, CITY_STOP_FIRST
from cursed_descent.locations.citystop.location import pick_town
from cursed_descent.locations.venues import city_stop_at
from cursed_descent.models import Player
from cursed_descent.town_buildings.station.rail_pass import (
    has_pass, passes, try_pass,
)
from cursed_descent.towns import START_TOWN


def test_a_town_stop_comes_every_thirty_stages_but_never_on_a_boss() -> None:
    stages = [stage for stage in range(1, 400) if city_stop_at(stage)]
    assert stages[:3] == [35, 65, 95]
    assert all(stage % 10 for stage in stages)
    assert stages[1] - stages[0] == CITY_STOP_EVERY
    assert CITY_STOP_FIRST == 35


def test_only_a_stationmaster_deal_opens_a_line() -> None:
    kerl = Player(name="Kerl", gold=1000)
    assert passes(kerl) == [START_TOWN]
    ok, _ = try_pass(kerl, "ironhold", "pay")
    assert ok and has_pass(kerl, "ironhold") and kerl.gold == 850
    assert "ironhold" in kerl.profile["towns_seen"]
    poor = Player(name="Pia", gold=10)
    ok, text = try_pass(poor, "cogsworth", "bribe")
    assert not ok and "costs" in text and not has_pass(poor, "cogsworth")


def test_bribes_can_fail_and_talking_gets_easier() -> None:
    outcomes = set()
    for seed in range(40):
        kerl = Player(name="Kerl", gold=1000)
        outcomes.add(try_pass(kerl, "mudgate", "bribe",
                              random.Random(seed))[0])
    assert outcomes == {True, False}
    low = Player(name="Lo", gold=0)
    results = [try_pass(low, "mudgate", "talk", random.Random(1))[0]
               for _ in range(8)]
    assert results[-1] is True or has_pass(low, "mudgate")


def test_the_dungeon_stop_picks_a_town_and_marks_it_visited() -> None:
    kerl = Player(name="Kerl")
    picks = {pick_town([kerl], random.Random(seed)) for seed in range(60)}
    assert picks and START_TOWN not in picks


def test_the_dungeon_platform_sells_a_rail_pass(controller) -> None:
    kerl = controller.repository.load("kerl")
    kerl.gold = 1000
    controller.repository.save(kerl)
    controller.handle("kerl", "!lobby", now=0.0)
    controller.handle("kerl", "!start", now=1.0)
    lines = controller.session.events.offer_location("citystop", 2.0)
    town = controller.session.events.event["data"]["town"]
    assert any("rail pass" in line for line in lines)
    assert town in controller.repository.load("kerl").profile["towns_seen"]
    reply = " ".join(message.text for message in
                     controller.handle("kerl", "!pay", now=3.0))
    kerl = controller.repository.load("kerl")
    assert town in kerl.profile["rail_pass"] and kerl.gold == 850
    assert "pass" in reply
    assert controller.session.state == "event"
    controller.handle("kerl", "!depart", now=4.0)
    assert controller.session.events.event.get("kind") != "citystop"


def at_platform(controller, names=("kerl",)) -> str:
    controller.handle(names[0], "!lobby", now=0.0)
    for name in names[1:]:
        controller.handle(name, "!join", now=0.5)
    controller.handle("kerl", "!start", now=1.0)
    controller.session.events.offer_location("citystop", 2.0)
    return controller.session.events.event["data"]["town"]


def test_offering_yourself_always_works_and_gives_the_pass(
        controller) -> None:
    from cursed_descent.town_buildings.station.rail_pass import has_pass
    town = at_platform(controller)
    assert "offer" in controller.session.events.available()
    reply = " ".join(m.text for m in controller.handle("kerl", "!offer",
                                                       now=3.0))
    kerl = controller.session.member("kerl")
    assert has_pass(kerl, town) and "rail pass" in reply
    again = " ".join(m.text for m in controller.handle("kerl", "!offer",
                                                       now=4.0))
    assert "already have your pass" in again
    assert controller.session.state == "event"


def test_only_acts_the_body_allows_are_offered() -> None:
    from cursed_descent.locations.citystop.location import eligible_acts
    man = Player(name="M", gender="Male")
    woman = Player(name="W", gender="Female")
    woman.body["breasts"] = "Huge"
    assert set(eligible_acts(man)) == {"anal", "oral", "milk_cock"}
    assert set(eligible_acts(woman)) == {"anal", "oral", "vaginal",
                                         "milk_bust"}


def test_the_keepers_child_has_the_keepers_species(
        controller, monkeypatch) -> None:
    from cursed_descent.births import add_child
    from cursed_descent.towns import TOWNS
    from cursed_descent.locations.citystop.content import STATION_ID
    kerl = Player(name="Kerl", gender="Female")
    kerl.pregnant = "party"
    kerl.profile["pregnant_by_id"] = f"{STATION_ID}ironhold"
    assert add_child(kerl)["species"] == TOWNS["ironhold"].race_key


def test_sneaking_in_can_succeed(controller, monkeypatch) -> None:
    from cursed_descent.town_buildings.station.rail_pass import has_pass
    town = at_platform(controller)
    monkeypatch.setattr(random, "random", lambda: 0.0)
    controller.handle("kerl", "!sneak", now=3.0)
    assert has_pass(controller.session.member("kerl"), town)
    assert controller.session.state == "event"


def test_a_caught_sneak_leaves_a_stake_at_the_gate(
        controller, monkeypatch) -> None:
    town = at_platform(controller, ("kerl", "galactica"))
    monkeypatch.setattr(random, "random", lambda: 0.99)
    reply = " ".join(m.text for m in controller.handle("kerl", "!sneak",
                                                       now=3.0))
    entry = controller.session.remains.entries[-1]
    assert entry["fate"] == "staked" and entry["detail"] == town
    assert "stake" in reply
    lines = controller.session.events.stake_lines(town)
    assert "Kerl" in lines[0] or "kerl" in lines[0]
    picked = controller.session.remains.pick(entry["stage"], "other-run",
                                             set())
    assert picked is None or picked["fate"] != "staked"
    again = " ".join(m.text for m in controller.handle("kerl", "!sneak",
                                                       now=4.0))
    assert again


def test_sneaking_is_tried_once_per_stop(controller, monkeypatch) -> None:
    at_platform(controller, ("kerl", "galactica"))
    monkeypatch.setattr(random, "random", lambda: 0.99)
    controller.handle("galactica", "!sneak", now=3.0)
    reply = " ".join(m.text for m in controller.handle("galactica", "!sneak",
                                                       now=4.0))
    assert reply


def test_enter_appears_once_everyone_holds_the_pass(controller) -> None:
    town = at_platform(controller, ("kerl", "galactica"))
    events = controller.session.events
    assert "enter" not in events.available()
    controller.handle("kerl", "!offer", now=3.0)
    assert "enter" not in events.available()
    controller.handle("galactica", "!offer", now=4.0)
    assert "enter" in events.available()
    assert town in controller.session.member("galactica").profile["rail_pass"]


def test_entering_the_town_pauses_the_run_and_resume_goes_on_after_it(
        controller) -> None:
    town = at_platform(controller)
    kerl = controller.session.member("kerl")
    kerl.inventory[:] = ["potion_small"]
    kerl.gold = 777
    controller.handle("kerl", "!offer", now=3.0)
    reply = " ".join(m.text for m in controller.handle("kerl", "!enter",
                                                       now=4.0))
    assert "boards the train" in reply and "The curse awakens" not in reply
    assert controller.session.state == "paused"
    assert not controller.session.in_run("kerl")
    kerl = controller.repository.load("kerl")
    assert kerl.profile["town"] == town and kerl.profile["where"] == "town"
    assert kerl.gold == 777 and "potion_small" in kerl.inventory
    stage = controller.session.stage
    assert "waiting" in " ".join(m.text for m in controller.handle(
        "kerl", "!lobby", now=5.0))
    reply = " ".join(m.text for m in controller.handle("kerl", "!resume",
                                                       now=6.0))
    assert "return to the dungeon" in reply
    assert controller.session.stage == stage + 1
    assert controller.session.in_run("kerl")


def test_retiring_a_paused_run_ends_it_for_good(controller) -> None:
    at_platform(controller)
    controller.handle("kerl", "!offer", now=3.0)
    controller.handle("kerl", "!enter", now=4.0)
    depth = controller.session.stage
    reply = " ".join(m.text for m in controller.handle("kerl", "!retire",
                                                       now=5.0))
    assert f"after stage {depth}" in reply
    assert controller.session.state == "idle"
    assert "no waiting run" in " ".join(m.text for m in controller.handle(
        "kerl", "!resume", now=6.0)).lower()


def test_departing_the_platform_goes_on_with_the_next_stage(
        controller) -> None:
    at_platform(controller)
    stage = controller.session.stage
    controller.handle("kerl", "!depart", now=4.0)
    assert controller.session.stage == stage + 1


def test_the_wedding_comes_once_per_run_in_the_location_slot(
        controller) -> None:
    import random
    controller.handle("kerl", "!lobby", now=0.0)
    controller.handle("kerl", "!start", now=1.0)
    events = controller.session.events
    random.seed(1)
    seen = [events.location_for(48) for _ in range(300)]
    assert seen.count("wedding") == 1
    assert {"couch", "throne", "wardrobe"} <= set(seen)

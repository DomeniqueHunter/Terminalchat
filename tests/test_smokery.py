import random

import pytest

from cursed_descent.config import SMOKERY_CYCLES
from cursed_descent.content import ITEMS
from cursed_descent.controller import GameController
from cursed_descent.locations.smokery.location import smoke_chance
from cursed_descent.npcs.store import find_local


def texts(messages) -> str:
    return "\n".join(message.text for message in messages)


def at_smokery(controller:GameController) -> None:
    controller.handle("kerl", "!lobby", now=0.0)
    controller.handle("kerl", "!start", now=1.0)
    controller.session.stage = 12
    controller.session.events.offer_location("smokery", 2.0)
    controller.handle("kerl", "!enter", now=3.0)


def test_the_owner_is_a_2_9_metre_nord(controller:GameController) -> None:
    controller.handle("kerl", "!lobby", now=0.0)
    controller.handle("kerl", "!start", now=1.0)
    lines = controller.session.events.offer_location("smokery", 2.0)
    assert "2.9 metres" in "\n".join(lines) and "Nord" in "\n".join(lines)


def test_outside_offers_enter_examine_and_pass(
        controller:GameController) -> None:
    controller.handle("kerl", "!lobby", now=0.0)
    controller.handle("kerl", "!start", now=1.0)
    controller.session.events.offer_location("smokery", 2.0)
    assert controller.session.events.available() == [
        "enter", "examine", "pass"]
    assert controller.handle("kerl", "!examine", now=2.5)
    controller.handle("kerl", "!pass", now=3.0)
    assert controller.session.state != "event"


def test_survival_over_five_cycles_is_about_one_in_ten(
        controller:GameController) -> None:
    kerl = controller.repository.load("kerl")
    kerl.stats["vitality"] = 10
    assert smoke_chance(kerl) ** SMOKERY_CYCLES == pytest.approx(0.1,
                                                                  abs=0.01)


def test_vitality_helps_but_is_capped(controller:GameController) -> None:
    kerl = controller.repository.load("kerl")
    kerl.stats["vitality"] = 10
    low = smoke_chance(kerl)
    kerl.stats["vitality"] = 500
    assert smoke_chance(kerl) > low and smoke_chance(kerl) <= 0.8


def test_smoking_pays_the_hero_up_front_and_survivors_get_a_bonus(
        controller:GameController, monkeypatch) -> None:
    at_smokery(controller)
    kerl = controller.session.member("kerl")
    kerl.gold = 0
    pay = controller.session.events.smoke_pay()
    monkeypatch.setattr(random, "random", lambda: 0.0)
    controller.handle("kerl", "!smoke", now=4.0)
    assert kerl.gold == pay
    for _ in range(SMOKERY_CYCLES - 1):
        controller.handle("kerl", "!endure", now=5.0)
    assert kerl.gold == pay * 3


def test_a_survivor_gets_vitality_and_a_trait(
        controller:GameController, monkeypatch) -> None:
    at_smokery(controller)
    kerl = controller.session.member("kerl")
    kerl.gold = 10 ** 6
    vitality = kerl.stats["vitality"]
    monkeypatch.setattr(random, "random", lambda: 0.0)
    texts(controller.handle("kerl", "!smoke", now=4.0))
    for number in range(2, SMOKERY_CYCLES + 1):
        reply = texts(controller.handle("kerl", "!endure", now=5.0))
        assert f"cycle {number}/5" in reply
    assert "alive" in reply and kerl.alive
    assert kerl.stats["vitality"] == vitality + 2
    assert kerl.profile["smoked"] == 1
    assert "depart" in controller.session.events.available()


def test_death_turns_the_hero_into_foot_smoked_meat(
        controller:GameController, monkeypatch) -> None:
    at_smokery(controller)
    session = controller.session
    session.member("kerl").gold = 10 ** 6
    monkeypatch.setattr(random, "random", lambda: 0.999)
    reply = texts(controller.handle("kerl", "!smoke", now=4.0))
    assert "💀" in reply and "orc butcher carves" in reply
    entry = session.remains.entries[-1]
    assert entry["fate"] == "smoked" and entry["location"] == 12
    pieces = [item for item in ITEMS if item.startswith(
        f"meat_{entry['id']}")]
    edible = [item for item in pieces if not item.endswith("_h")]
    assert edible and all("foot-" in ITEMS[item]["name"]
                          for item in edible)
    assert any(item.endswith("_h") for item in pieces)
    assert not any(ITEMS[item].get("raw_meat") for item in pieces)


def test_every_smoked_hero_counts_as_a_kill_for_jorveig(
        controller:GameController, monkeypatch) -> None:
    at_smokery(controller)
    session = controller.session
    session.member("kerl").gold = 10 ** 6
    monkeypatch.setattr(random, "random", lambda: 0.999)
    controller.handle("kerl", "!smoke", now=4.0)
    owner = find_local(session.repository.npc_players(), "jorveig")
    assert owner.records["kills"] == 1


def test_smoked_hero_is_sold_on_a_later_visit(
        controller:GameController, monkeypatch) -> None:
    at_smokery(controller)
    session = controller.session
    session.member("kerl").gold = 10 ** 6
    monkeypatch.setattr(random, "random", lambda: 0.999)
    controller.handle("kerl", "!smoke", now=4.0)
    entry = session.remains.entries[-1]
    session.run_id = "other-run"
    session.events.reset()
    session.stage = 12
    session.events.offer_location("smokery", 10.0)
    stock = session.events.smokery_stock()
    assert f"meat_{entry['id']}" in stock


def test_begging_can_release_or_not(controller:GameController,
                                    monkeypatch) -> None:
    at_smokery(controller)
    session = controller.session
    session.member("kerl").gold = 10 ** 6
    monkeypatch.setattr(random, "random", lambda: 0.0)
    controller.handle("kerl", "!smoke", now=4.0)
    monkeypatch.setattr("cursed_descent.locations.smokery.location."
                        "SMOKERY_RELEASE", 0.0)
    assert "Bit early" in texts(controller.handle("kerl", "!beg", now=5.0))
    monkeypatch.setattr("cursed_descent.locations.smokery.location."
                        "SMOKERY_RELEASE", 1.0)
    assert "pops the" in texts(controller.handle("kerl", "!beg", now=6.0))
    assert session.events.smoke_boxes() == {}


def test_cannot_depart_while_in_the_box(controller:GameController,
                                        monkeypatch) -> None:
    at_smokery(controller)
    controller.session.member("kerl").gold = 10 ** 6
    monkeypatch.setattr(random, "random", lambda: 0.0)
    controller.handle("kerl", "!smoke", now=4.0)
    assert "Not while somebody" in texts(
        controller.handle("kerl", "!depart", now=5.0))
    assert "Not while somebody" in texts(
        controller.handle("kerl", "!depart", now=6.0))


def test_the_smoking_uses_no_fire_only_foot_sweat_and_aroma() -> None:
    from cursed_descent.locations.smokery import content, fates, npc
    text = " ".join(str(part) for part in (
        content.SMOKERY_TEXTS, content.SMOKERY_TRAITS, fates.FATES,
        npc.SMOKERY_STAFF)).casefold()
    for word in ("herb", "chimney", "flames", "burning", "hickory"):
        assert word not in text


def test_death_is_described_inside_the_box_with_both_feet(
        controller:GameController, monkeypatch) -> None:
    at_smokery(controller)
    controller.session.member("kerl").gold = 10 ** 6
    monkeypatch.setattr(random, "random", lambda: 0.999)
    reply = texts(controller.handle("kerl", "!smoke", now=4.0))
    assert "both of her huge bare feet" in reply
    assert "{" not in reply and "}" not in reply
    assert "feet" in reply and "tears" in reply or "tastes" in reply


def die_at(controller:GameController, monkeypatch, cycle:int) -> dict:
    at_smokery(controller)
    controller.session.member("kerl").gold = 10 ** 6
    rolls = iter([0.0] * (cycle - 1) + [0.999])
    monkeypatch.setattr(random, "random", lambda: next(rolls, 0.999))
    controller.handle("kerl", "!smoke", now=4.0)
    for step in range(cycle - 1):
        controller.handle("kerl", "!endure", now=5.0 + step)
    return controller.session.remains.entries[-1]


def test_early_death_is_fresh_and_late_death_is_dried(
        controller:GameController, monkeypatch) -> None:
    from cursed_descent.curing import cure_stage
    early = die_at(controller, monkeypatch, 1)
    assert early["cure"] == 1 and cure_stage(early)[0] == "fresh"


def test_late_death_hangs_half_dried(controller:GameController,
                                     monkeypatch) -> None:
    from cursed_descent.curing import cure_stage
    late = die_at(controller, monkeypatch, 5)
    assert late["cure"] == 5 and cure_stage(late)[0] == "dried"


def test_racks_ripen_with_every_visit() -> None:
    from cursed_descent.curing import cure_stage, ripen
    entry = {"cure": 1}
    assert not ripen(entry) and entry["cure"] == 2
    assert ripen(entry) and cure_stage(entry)[0] == "cured"
    for _ in range(5):
        ripen(entry)
    assert entry["cure"] == 5 and cure_stage(entry)[0] == "dried"


def test_fresh_meat_is_worth_less_than_dried() -> None:
    from cursed_descent.curing import cure_stage
    assert cure_stage({"cure": 1})[2] < cure_stage({"cure": 5})[2]


def test_meat_fills_the_stomach() -> None:
    from cursed_descent.locations.butcher.location import register_meat
    from cursed_descent.needs import item_needs
    entry = {"id": "abc", "name": "Kerl", "fate": "smoked", "stage": 3,
             "cure": 3, "detail": "", "victim": {
                 "level": 3, "build": "Average", "vitality": 10, "weight": 70}}
    register_meat(entry)
    assert item_needs("meat_abc")["hunger"] <= -30
    raw = {"id": "def", "name": "Kerl", "fate": "butchered", "stage": 3,
           "detail": "", "victim": entry["victim"]}
    register_meat(raw)
    assert item_needs("meat_def")["hunger"] < 0
    assert item_needs("cooked_def")["hunger"] <= -40

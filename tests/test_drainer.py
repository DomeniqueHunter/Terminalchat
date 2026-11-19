from pathlib import Path

from cursed_descent.body import body_text, fake_amount
from cursed_descent.content import ENEMIES, ITEMS
from cursed_descent.controller import GameController
from cursed_descent.events.drainer.ledger import (
    Ledger, bottle_name, drain, item_id_of, register_bottle, restore,
)
from cursed_descent.models import Player
from cursed_descent.spawns import RULES_BY_KIND
from tests.ready import confirm


def say(controller:GameController, name:str, text:str) -> str:
    return "\n".join(m.text for m in controller.handle(name, text))


def make(name:str, gender:str, **body:int) -> Player:
    player = Player(name=name, gold=500, gender=gender)
    player.body = {"height": 170, "weight": 65, "build": "Average",
                   "breasts": "None", "bust": 300, "butt": 95,
                   "endowment": 15, "girth": 12, "balls": 5, "fake": {}}
    player.body.update(body)
    return player


def start(tmp_path:Path, players:list[Player]) -> GameController:
    controller = GameController(tmp_path, debug=True)
    for player in players:
        controller.repository.save(player)
    say(controller, players[0].name, "!lobby")
    for player in players[1:]:
        say(controller, player.name, "!join")
    say(controller, players[0].name, "!start")
    confirm(controller)
    say(controller, players[0].name, "!trigger drainer")
    return controller


def test_the_drainer_is_rare_and_registered() -> None:
    rule = RULES_BY_KIND["drainer"]
    assert rule.once_per_run and rule.weight == 1 and rule.min_stage >= 10
    assert ENEMIES["drainer"]["hp"] >= 500


def test_a_female_loses_chest_then_curves_and_nothing_else() -> None:
    lena = make("Lena", "Female")
    first = drain(lena, 5)
    assert first["part"] == "bust" and first["label"] == "Boy Chest"
    assert lena.body["bust"] == 0 and lena.body["breasts"] == "None"
    second = drain(lena, 5)
    assert second["part"] == "butt" and second["label"] == "Flat-ass"
    assert lena.body["butt"] == 60
    assert drain(lena, 5) is None
    assert "Boy Chest" in body_text(lena.body)


def test_a_herm_goes_through_all_four_parts_in_order() -> None:
    herm = make("Mira", "Herm")
    parts = [drain(herm, 5)["part"] for _ in range(4)]
    assert parts == ["bust", "butt", "penis", "balls"]
    assert drain(herm, 5) is None
    assert herm.body["endowment"] == 4 and herm.body["girth"] == 4
    assert fake_amount(herm.body, "balls") == herm.body["balls"] == 5


def test_a_flat_man_skips_the_chest() -> None:
    hero = make("Hero", "Male", bust=0)
    assert drain(hero, 5)["part"] == "butt"


def test_a_bottle_gives_the_values_back_in_full() -> None:
    herm = make("Mira", "Herm")
    bottles = [drain(herm, 5) for _ in range(4)]
    for bottle in bottles:
        restore(herm, bottle)
    assert herm.body["bust"] == 300 and herm.body["butt"] == 95
    assert herm.body["endowment"] == 15 and herm.body["girth"] == 12
    assert fake_amount(herm.body, "balls") == 0
    assert not herm.body.get("drained")


def test_the_ledger_keeps_and_hands_out_bottles(tmp_path:Path) -> None:
    ledger = Ledger(tmp_path)
    ledger.add(drain(make("Lena", "Female"), 5))
    assert len(ledger.bottles()) == 1
    assert ledger.take_random()["victim"] == "Lena"
    assert ledger.take_random() is None


def test_a_sacrifice_by_majority_drains_and_lets_the_party_pass(
        tmp_path:Path) -> None:
    controller = start(tmp_path, [make("Hero", "Male", bust=0),
                                  make("Lena", "Female")])
    assert controller.session.events.event["kind"] == "drainer"
    say(controller, "Hero", "!sacrifice Lena")
    assert controller.session.events.event["kind"] == "drainer"
    output = say(controller, "Lena", "!sacrifice Lena")
    assert "Boy Chest" in output
    lena = controller.repository.load("Lena")
    assert lena.alive and lena.body["bust"] == 0
    assert controller.session.events.event == {}
    bottles = Ledger(controller.repository.data_path).bottles()
    assert [bottle["victim"] for bottle in bottles] == ["Lena"]


def test_a_challenge_vote_starts_the_fight(tmp_path:Path) -> None:
    controller = start(tmp_path, [make("Hero", "Male"),
                                  make("Lena", "Female")])
    say(controller, "Hero", "!challenge")
    say(controller, "Lena", "!challenge")
    session = controller.session
    assert session.state == "combat" and session.bonus_fight == "drainer"
    assert session.enemies[0].boss


def test_the_panel_offers_one_button_per_candidate(tmp_path:Path) -> None:
    from cursed_descent.web.run_panels import run_shop_panel
    controller = start(tmp_path, [make("Hero", "Male", bust=0),
                                  make("Lena", "Female")])
    hero = controller.repository.load("Hero")
    panel = run_shop_panel(controller, hero)
    commands = [button.command for button in panel.buttons]
    assert "!sacrifice Lena" in commands and "!challenge" in commands


def test_a_victory_hands_one_bottle_to_one_bag(tmp_path:Path) -> None:
    controller = start(tmp_path, [make("Hero", "Male", bust=0),
                                  make("Lena", "Female")])
    ledger = Ledger(controller.repository.data_path)
    ledger.add(drain(make("Mira", "Female", bust=450), 3))
    ledger.add(drain(make("Cara", "Female"), 3))
    say(controller, "Hero", "!challenge")
    say(controller, "Lena", "!challenge")
    session = controller.session
    for enemy in session.enemies:
        enemy.hp = 0
    session.clear_bonus(1.0)
    assert session.events.event["data"]["mode"] == "restore"
    assert len(ledger.bottles()) == 1
    say(controller, "Hero", "!give Lena")
    output = say(controller, "Lena", "!give Lena")
    assert "pockets the bottle" in output
    lena = session.member("Lena")
    bottles = [item for item in lena.inventory
               if str(item).startswith("drainer_bottle_")]
    assert len(bottles) == 1 and session.events.event == {}
    assert "Bottle:" in ITEMS[str(bottles[0])]["name"]


def test_a_bottle_is_named_by_its_values_and_has_a_fixed_price() -> None:
    bottle = drain(make("Mira", "Female", bust=450), 3)
    bottle["id"] = "abc12345"
    assert bottle_name(bottle) == "Bottle: Mira's chest (450 cc)"
    register_bottle(bottle)
    item = ITEMS[item_id_of(bottle)]
    assert item["slot"] == "consumable" and item["price"] == 400
    assert item["no_loot"]


def test_drinking_a_bottle_gives_the_values_back(tmp_path:Path) -> None:
    controller = GameController(tmp_path, debug=True)
    lena = make("Lena", "Female", bust=450)
    controller.repository.save(lena)
    ledger = Ledger(controller.repository.data_path)
    ledger.add(drain(lena, 3))
    entry = ledger.entries()[0]
    lena.inventory.append(item_id_of(entry))
    controller.repository.save(lena)
    assert lena.body["bust"] == 0
    output = say(controller, "Lena", f"!consume {item_id_of(entry)}")
    assert "returns" in output
    lena = controller.repository.load("Lena")
    assert lena.body["bust"] == 450
    assert not [item for item in lena.inventory
                if str(item).startswith("drainer_bottle_")]
    assert ledger.entries() == []


def test_a_bottle_of_a_manhood_is_useless_for_a_female(
        tmp_path:Path) -> None:
    controller = GameController(tmp_path, debug=True)
    herm = make("Mira", "Herm", bust=0, butt=60)
    lena = make("Lena", "Female")
    controller.repository.save(herm)
    ledger = Ledger(controller.repository.data_path)
    ledger.add(drain(herm, 3))
    entry = ledger.entries()[0]
    lena.inventory.append(item_id_of(entry))
    controller.repository.save(lena)
    output = say(controller, "Lena", f"!consume {item_id_of(entry)}")
    assert "can do nothing" in output
    assert controller.repository.load("Lena").inventory
    assert ledger.get(entry["id"]) is not None


def test_a_left_bottle_goes_back_on_the_belt(tmp_path:Path) -> None:
    controller = start(tmp_path, [make("Hero", "Male", bust=0),
                                  make("Lena", "Female")])
    ledger = Ledger(controller.repository.data_path)
    ledger.add(drain(make("Mira", "Female"), 3))
    say(controller, "Hero", "!challenge")
    say(controller, "Lena", "!challenge")
    session = controller.session
    for enemy in session.enemies:
        enemy.hp = 0
    session.clear_bonus(1.0)
    assert ledger.bottles() == []
    say(controller, "Hero", "!depart")
    say(controller, "Lena", "!depart")
    assert len(ledger.bottles()) == 1


def test_a_wipe_costs_one_player_a_part(tmp_path:Path) -> None:
    controller = start(tmp_path, [make("Hero", "Male", bust=0),
                                  make("Lena", "Female")])
    say(controller, "Hero", "!challenge")
    say(controller, "Lena", "!challenge")
    session = controller.session
    output = "\n".join(session.end_run())
    assert "takes his due" in output
    assert len(Ledger(controller.repository.data_path).bottles()) == 1

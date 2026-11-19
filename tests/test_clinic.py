import random

import pytest

from cursed_descent.config import CLINIC_MAGIC_FACTOR, CLINIC_PRICES
from cursed_descent.models import Player
from cursed_descent.locations.clinic import location as clinic
from cursed_descent.locations.clinic.location import (
    PARTS, apply_mod, clinic_menu, clinic_mod, clinic_options,
    enhancement_lines, magic_chance, part_price,
)


def part(key:str) -> clinic.Part:
    return next(item for item in PARTS if item.key == key)


@pytest.fixture
def rich() -> Player:
    return Player(name="Rich", gender="Female", gold=10**9)


@pytest.fixture
def hung() -> Player:
    return Player(name="Hung", gender="Male", gold=10**9)


def options(player:Player) -> dict[str, int]:
    return {command: price for command, _, price in clinic_options(player)}


def test_every_part_can_grow_and_shrink(rich:Player) -> None:
    offered = options(rich)
    for command in ("height up", "weight up", "muscle up", "bust up",
                    "bust up magic", "butt up", "butt up magic"):
        assert command in offered
    assert "bust down" not in offered and "height down" in offered
    rich.body["bust"] = 300
    assert "bust down" in options(rich)


def test_hung_parts_only_for_hung_genders(rich:Player, hung:Player) -> None:
    assert "cock up" not in options(rich)
    assert not {"girth up", "balls up", "shape equine"} & set(options(rich))
    assert {"cock up", "girth up", "balls up", "shape equine"} <= set(
        options(hung))


def test_magic_costs_more_than_implants(rich:Player) -> None:
    offered = options(rich)
    assert offered["bust up magic"] == offered["bust up"] * (
        CLINIC_MAGIC_FACTOR)


def test_prices_grow_with_size() -> None:
    bust = part("bust")
    assert part_price(bust, 300) < part_price(bust, 900) < part_price(
        bust, 3000)


def test_magic_gets_harder_but_never_impossible() -> None:
    bust = part("bust")
    chances = [magic_chance(bust, value) for value in (300, 600, 5000)]
    assert chances == sorted(chances, reverse=True)
    assert chances[-1] >= 0.35 and chances[0] > chances[-1]


def test_implant_is_tracked_as_fake(rich:Player) -> None:
    clinic_mod(rich, ["bust", "up"], False)
    assert rich.body["bust"] == 150
    assert rich.body["fake"]["bust"] == 150
    assert rich.body["breasts_real"] == "None"


def test_magic_growth_is_real(rich:Player, monkeypatch) -> None:
    monkeypatch.setattr(random, "random", lambda: 0.0)
    clinic_mod(rich, ["bust", "up", "magic"], False)
    assert rich.body["bust"] == 150 and rich.body.get("fake", {}) == {}
    assert rich.body["breasts_real"] == "Small"


def test_failed_magic_costs_gold_and_changes_nothing(
        rich:Player, monkeypatch) -> None:
    monkeypatch.setattr(random, "random", lambda: 0.999)
    before, gold = dict(rich.body), rich.gold
    message = clinic_mod(rich, ["bust", "up", "magic"], False)[0].text
    assert "nothing changes" in message
    assert rich.body == before and rich.gold < gold


def test_shrinking_removes_implants_first(rich:Player, monkeypatch) -> None:
    monkeypatch.setattr(random, "random", lambda: 0.0)
    clinic_mod(rich, ["bust", "up", "magic"], False)
    clinic_mod(rich, ["bust", "up"], False)
    clinic_mod(rich, ["bust", "down"], False)
    assert rich.body["bust"] == 150
    assert rich.body["fake"] == {}


def test_growth_is_not_capped(rich:Player) -> None:
    for _ in range(200):
        apply_mod(rich, "height up")
    assert rich.body["height"] == 170 + 200 * 5
    for _ in range(40):
        apply_mod(rich, "bust up")
    assert rich.body["bust"] == 40 * 150
    assert rich.body["breasts"] == "Massive"


def test_minimums_are_respected(rich:Player) -> None:
    rich.body["height"] = 32
    assert "height down" not in options(rich)


def test_changes_are_stored_as_mods(rich:Player) -> None:
    apply_mod(rich, "muscle up")
    assert rich.body_mods["muscle"] == 30 == rich.body["muscle"]


def test_alias_commands_still_work(rich:Player) -> None:
    clinic_mod(rich, ["taller"], False)
    assert rich.body["height"] == 175
    clinic_mod(rich, ["lighter"], False)
    assert rich.body["weight"] == 60


def test_build_change_keeps_bought_muscle(rich:Player) -> None:
    apply_mod(rich, "muscle up")
    apply_mod(rich, "build muscular")
    assert rich.body["build"] == "Muscular"
    assert rich.body["muscle"] == 30 + (70 - 25)


def test_shape_change_costs_gold(hung:Player) -> None:
    gold = hung.gold
    clinic_mod(hung, ["shape", "equine"], False)
    assert hung.body["endowment_shape"] == "Equine"
    assert hung.gold == gold - CLINIC_PRICES["shape"]


def test_poor_players_are_turned_away(rich:Player) -> None:
    rich.gold = 1
    message = clinic_mod(rich, ["bust", "up"], False)[0].text
    assert "gold" in message and rich.body["bust"] == 0


def test_clinic_is_closed_during_a_run(rich:Player) -> None:
    assert "come back" in clinic_mod(rich, ["bust", "up"], True)[0].text


def test_unknown_commands_show_the_menu(rich:Player) -> None:
    assert "[mod bust up]" in clinic_mod(rich, ["nonsense"], False)[0].text


def test_enhancements_toggle_as_before(rich:Player) -> None:
    apply_mod(rich, "butt")
    assert "butt" in rich.enhancements
    apply_mod(rich, "remove butt")
    assert "butt" not in rich.enhancements


def test_measurements_list_implants(rich:Player) -> None:
    apply_mod(rich, "bust up")
    line = enhancement_lines(rich)[0]
    assert "implants" in line and "butt 95 cm" in line


def test_menu_lists_prices(rich:Player) -> None:
    assert "gold)" in clinic_menu(rich)[0].text


def test_the_keeper_greets_and_advises_per_town() -> None:
    from cursed_descent.locations.clinic.location import clinic_advice
    thin = Player(name="Kerl", gender="Male", age=30)
    thin.body.update({"build": "Thin", "butt": 80})
    advice = " ".join(clinic_advice(thin))
    assert "mod balls up" in advice and "smaller" not in advice
    thin.gender = "Female"
    thin.body["breasts"] = "Large"
    thin.body["bust"] = 3000
    assert "mod bust up" in " ".join(clinic_advice(thin))
    assert "up magic" in " ".join(clinic_advice(thin, "cogsworth"))
    thin.gender = "Male"
    text = clinic_menu(thin, "cogsworth")[0].text
    assert "Professor Fizzwick" in text and "speciality" in text
    assert "Grizzla" in clinic_menu(thin, "mudgate")[0].text
    assert "Dr. Vane" in clinic_menu(thin)[0].text


def test_goblin_clinic_only_does_implants(rich:Player) -> None:
    from cursed_descent.locations.clinic.location import clinic_options
    assert any("up magic" in command
               for command, _, _ in clinic_options(rich))
    rich.profile["town"] = "mudgate"
    options = [command for command, _, _ in clinic_options(rich)]
    assert not any("magic" in command for command in options)
    assert "bust up" in options


def test_the_clinic_ends_a_pregnancy_for_gold() -> None:
    from cursed_descent.config import CLINIC_PRICES
    player = Player(name="Mia", gold=1000, gender="Female")
    assert "terminate" not in options(player)
    player.pregnant = "party"
    player.profile.update({"pregnant_by": "Tom", "pregnant_by_id": "x",
                           "pregnant_nights": 2})
    assert options(player)["terminate"] == CLINIC_PRICES["terminate"]
    clinic_mod(player, ["terminate"], in_run=False)
    assert player.pregnant == "" and "pregnant_by" not in player.profile
    assert player.gold == 1000 - CLINIC_PRICES["terminate"]
    assert "terminate" not in options(player)

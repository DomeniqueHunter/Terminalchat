from cursed_descent.config import NEED_RATES
from cursed_descent.controller import GameController
from cursed_descent.formulas import allure, effective_stat
from cursed_descent.models import Player
from cursed_descent.needs import (
    advance, item_needs, level_of, new_needs, penalty, satisfy,
)
from cursed_descent.needs_runtime import rest_needs, tick_needs


def test_new_player_is_satisfied(hero:Player) -> None:
    assert hero.needs == new_needs()
    assert effective_stat(hero, "strength") == hero.stats["strength"]


def test_needs_roundtrip_through_json(hero:Player) -> None:
    hero.needs["hunger"] = 55
    assert Player.from_dict(hero.to_dict()).needs["hunger"] == 55


def test_levels_and_penalties() -> None:
    assert [level_of(v) for v in (0, 39, 40, 70, 90, 100)] == [0, 0, 1, 2, 3, 3]
    needs = new_needs()
    needs["hunger"] = 95
    assert penalty(needs, "strength") == 6


def test_advance_reports_level_rises() -> None:
    needs = new_needs()
    needs["hunger"] = 40 - NEED_RATES["hunger"]
    risen = advance(needs)
    assert ("hunger", 1) in risen
    assert needs["hunger"] == 40


def test_needs_are_capped() -> None:
    needs = {key: 99 for key in new_needs()}
    advance(needs)
    assert max(needs.values()) == 100


def test_satisfy_clamps_at_zero() -> None:
    needs = new_needs()
    needs["thirst"] = 10
    assert satisfy(needs, {"thirst": -40}) == {"thirst": -10}
    assert needs["thirst"] == 0


def test_item_rules() -> None:
    assert item_needs("bread_loaf") == {"hunger": -35}
    assert item_needs("cooked_beef")["hunger"] < 0
    assert item_needs("sword") == {}


def test_arousal_gives_allure_when_high(hero:Player) -> None:
    base = allure(hero)
    hero.needs["arousal"] = 95
    assert allure(hero) > base


def test_tick_starving_hurts_but_never_kills(hero:Player) -> None:
    hero.hp = 1
    hero.needs["hunger"] = 100
    tick_needs(hero)
    assert hero.hp == 1


def test_tick_starving_costs_hp(hero:Player) -> None:
    from cursed_descent.formulas import max_hp
    hero.hp = max_hp(hero)
    hero.needs["thirst"] = 100
    lines = tick_needs(hero)
    assert hero.hp < max_hp(hero)
    assert any("HP" in line for line in lines)


def test_sweat_adds_thirst(hero:Player) -> None:
    clean = Player(name="A", gender="Male")
    sweaty = Player(name="B", gender="Male")
    sweaty.sweat = 10 ** 6
    tick_needs(clean)
    tick_needs(sweaty)
    assert sweaty.needs["thirst"] > clean.needs["thirst"]


def test_rest_resets_sleep(hero:Player) -> None:
    hero.needs["sleep"] = 80
    hero.needs["hunger"] = 50
    rest_needs(hero)
    assert hero.needs["sleep"] == 0 and hero.needs["hunger"] == 50


def test_consume_command(controller:GameController) -> None:
    player = controller.repository.load("kerl")
    player.inventory.append("bread_loaf")
    player.needs["hunger"] = 60
    controller.repository.save(player)
    messages = controller.handle("kerl", "!consume bread_loaf")
    assert "Hardtack" in messages[0].text
    reloaded = controller.repository.load("kerl")
    assert reloaded.needs["hunger"] == 25
    assert "bread_loaf" not in reloaded.inventory


def test_consume_rejects_non_food(controller:GameController) -> None:
    messages = controller.handle("kerl", "!consume 1")
    assert "Usage" in messages[0].text


def test_needs_command_and_profile(controller:GameController) -> None:
    assert "Needs:" in controller.handle("kerl", "!needs")[0].text
    assert "Needs:" in controller.handle("kerl", "!profile")[0].text


def test_shop_sells_provisions(controller:GameController) -> None:
    from cursed_descent.config import SHOP_CONSUMABLES
    assert "bread_loaf" in SHOP_CONSUMABLES

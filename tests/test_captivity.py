from pathlib import Path

from cursed_descent.config import DEATH_GOLD_LOSS, WORLD_DAY_SECONDS
from cursed_descent.captivity import is_captive
from cursed_descent.controller import GameController
from cursed_descent.models import Player
from cursed_descent.towns.last_light_humans.cafe.furniture import make_furniture


def make_controller(tmp_path:Path) -> GameController:
    controller = GameController(tmp_path)
    controller.town.visits_on = False
    return controller


def test_a_stool_costs_gold_but_returns_with_everything_else(
        tmp_path:Path) -> None:
    controller = make_controller(tmp_path)
    hero = Player(name="Hero", gold=1000, inventory=["potion_small"])
    controller.repository.add(hero)
    lost = make_furniture(hero, controller.repository,
                          controller.town.world.day)
    assert lost == int(1000 * DEATH_GOLD_LOSS)
    stool = controller.repository.load("Hero")
    assert stool.npc == "furniture" and is_captive(stool)
    assert stool.gold == 0 and stool.inventory == []
    controller.town.world.anchor -= WORLD_DAY_SECONDS
    messages = controller.town.tick_world()
    assert any("back among the living" in m.text for m in messages)
    back = controller.repository.load("Hero")
    assert back.npc == "" and back.gold == 1000 - lost
    assert [str(item) for item in back.inventory] == ["potion_small"]
    assert not back.records["cafe_lock"]
    assert "Hero" in controller.repository.names()


def test_the_world_clock_runs_by_itself(tmp_path:Path) -> None:
    controller = make_controller(tmp_path)
    assert controller.town.tick_world() == []
    controller.town.world.anchor -= 2 * WORLD_DAY_SECONDS
    controller.tick()
    assert controller.town.world.day == 2
    assert "day 3 of year 1" in controller.town.world.clock_text()


def test_the_clock_survives_a_restart(tmp_path:Path) -> None:
    controller = make_controller(tmp_path)
    controller.town.world.anchor -= WORLD_DAY_SECONDS
    controller.town.tick_world()
    again = make_controller(tmp_path)
    assert again.town.world.day == 1

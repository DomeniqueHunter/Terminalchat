from pathlib import Path

from cursed_descent.web.hub import GameHub


def test_online_characters_get_hungrier_and_heal(data_path:Path) -> None:
    hub = GameHub(data_path)
    town = hub.controller.town
    player = hub.controller.repository.load("kerl")
    player.hp = 1
    player.needs["hunger"] = 0
    hub.controller.repository.save(player)
    town.online = lambda: {"kerl"}
    town.world.due = lambda wall=None: 1
    messages = town.tick_world()
    after = hub.controller.repository.load("kerl")
    assert after.needs["hunger"] > 0 and after.hp > 1
    assert isinstance(messages, list)


def test_offline_characters_are_left_alone(data_path:Path) -> None:
    hub = GameHub(data_path)
    town = hub.controller.town
    player = hub.controller.repository.load("kerl")
    player.needs["hunger"] = 0
    hub.controller.repository.save(player)
    town.online = lambda: set()
    town.world.due = lambda wall=None: 1
    town.tick_world()
    assert hub.controller.repository.load("kerl").needs["hunger"] == 0

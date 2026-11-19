import pytest

from cursed_descent.controller import GameController
from cursed_descent.towns import TOWNS


CASES = [(town.key, building.key, command)
         for town in TOWNS.values()
         for building in town.building_list()
         for command in building.place_commands[:1]]


@pytest.mark.parametrize("town,key,command", CASES)
def test_clicking_a_building_does_something(controller:GameController,
                                            town:str, key:str,
                                            command:str) -> None:
    player = controller.repository.load("Kerl")
    player.profile.update(town=town, where="town")
    controller.repository.save(player)
    messages = controller.handle("Kerl", f"!{command}")
    assert messages, f"{town}: !{command} gives no answer"
    assert controller.repository.load("Kerl").profile["where"] == key or (
        controller.town.where(controller.repository.load("Kerl")) != "town")

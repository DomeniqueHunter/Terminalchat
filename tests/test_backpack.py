from cursed_descent.config import BACKPACK_MAX_EXTRA, INVENTORY_SIZE
from cursed_descent.controller import GameController
from cursed_descent.inventory import (
    backpack_price, grouped, sort_inventory,
)
from cursed_descent.models import Player


def texts(messages) -> str:
    return "\n".join(message.text for message in messages)


def test_bag_size_grows_with_extra_slots() -> None:
    player = Player(name="Hero")
    assert player.bag_size == INVENTORY_SIZE
    player.bag_extra = 3
    assert player.bag_size == INVENTORY_SIZE + 3
    assert Player.from_dict(player.to_dict()).bag_extra == 3


def test_sort_puts_gear_first_then_consumables() -> None:
    player = Player(name="Hero")
    player.inventory = ["potion_small", "leather_vest", "water_flask",
                        "rusty_sword", "iron_helmet"]
    sort_inventory(player)
    assert player.inventory == ["rusty_sword", "iron_helmet", "leather_vest",
                                "potion_small", "water_flask"]
    gear, consumables = grouped(player)
    assert len(gear) == 3 and len(consumables) == 2


def test_inv_shows_group_headers_with_continuous_numbers(
        controller:GameController) -> None:
    player = controller.repository.load("kerl")
    player.inventory = ["potion_small", "rusty_sword"]
    controller.repository.save(player)
    output = texts(controller.handle("kerl", "!inv"))
    assert output.index("-- Gear --") < output.index("1. ")
    assert output.index("-- Consumables --") < output.index("2. ")
    assert f"/{player.bag_size})" in output


def test_buying_a_slot_costs_gold_and_raises_the_price(
        controller:GameController) -> None:
    player = controller.repository.load("kerl")
    player.gold = 1000
    player.bag_extra = 0
    controller.repository.save(player)
    assert "costs" in texts(controller.handle("kerl", "!backpack"))
    first = backpack_price(player)
    assert "Slot sewn" in texts(controller.handle("kerl", "!backpack buy"))
    player = controller.repository.load("kerl")
    assert player.bag_extra == 1 and player.gold == 1000 - first
    assert backpack_price(player) > first


def test_not_enough_gold_and_maximum_are_refused(
        controller:GameController) -> None:
    player = controller.repository.load("kerl")
    player.gold = 0
    controller.repository.save(player)
    assert "costs" in texts(controller.handle("kerl", "!backpack buy"))
    assert controller.repository.load("kerl").bag_extra == 0
    player.gold = 10 ** 6
    player.bag_extra = BACKPACK_MAX_EXTRA
    controller.repository.save(player)
    assert "no more" in texts(controller.handle("kerl", "!backpack buy"))
    assert controller.repository.load("kerl").bag_extra == BACKPACK_MAX_EXTRA


def test_extra_slots_allow_a_fuller_bag(controller:GameController) -> None:
    player = controller.repository.load("kerl")
    player.bag_extra = 2
    player.inventory = ["water_flask"] * INVENTORY_SIZE
    controller.repository.save(player)
    assert f"{INVENTORY_SIZE}/{INVENTORY_SIZE + 2})" in texts(
        controller.handle("kerl", "!inv"))


def test_slots_beyond_twenty_get_expensive() -> None:
    player = Player(name="Hero")
    prices = []
    for extra in range(BACKPACK_MAX_EXTRA):
        player.bag_extra = extra
        prices.append(backpack_price(player))
    assert prices == sorted(prices) and len(set(prices)) == len(prices)
    assert prices[9] <= 800 < 2000 <= prices[10]
    assert prices[-1] > 100 * prices[9]
    assert INVENTORY_SIZE + BACKPACK_MAX_EXTRA > 20

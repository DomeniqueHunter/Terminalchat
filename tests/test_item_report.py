from cursed_descent.controller import GameController
from cursed_descent.item_report import find_owned, item_report
from cursed_descent.items import Item
from cursed_descent.models import Player


def hero_with_items() -> Player:
    hero = Player(name="Hero")
    hero.inventory = ["potion_small", Item("potion_small")]
    return hero


def test_find_owned_by_number_and_name() -> None:
    hero = hero_with_items()
    assert find_owned(hero, "1")[1] == "in your bag (nr 1)"
    assert find_owned(hero, "potion_small") is not None
    assert find_owned(hero, "9") is None
    assert find_owned(hero, "") is None


def test_report_lists_price_and_place() -> None:
    lines = item_report(hero_with_items(), "1")
    text = "\n".join(lines)
    assert "🔎" in text and "sells for" in text and "bag (nr 1)" in text


def test_report_shows_traces_and_sweat() -> None:
    hero = hero_with_items()
    worn = Item("potion_small", {"abc": {"name": "Lyra Dawn",
                                         "strength": 45}}, soak=3)
    hero.inventory = [worn]
    text = "\n".join(item_report(hero, "1"))
    assert "reeking of Lyra Dawn" in text and "soaked with sweat" in text


def test_unknown_item_gives_usage() -> None:
    assert "No such item" in item_report(hero_with_items(), "99")[0]


def test_item_command_answers_privately(controller:GameController) -> None:
    player = controller.repository.load("kerl")
    player.inventory = ["potion_small"]
    messages = controller.handle("kerl", "!item 1")
    assert messages[0].is_private and "🔎" in messages[0].text

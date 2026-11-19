from cursed_descent.controller import GameController
from cursed_descent.formulas import max_hp
from cursed_descent.towns.brandholm_nords.ember_cask import content


def text(messages) -> str:
    return "\n".join(message.text for message in messages)


def setup(controller:GameController, gold:int=1000) -> None:
    player = controller.repository.load("Kerl")
    player.profile.update(town="brandholm", where="ember_cask")
    player.gold = gold
    player.hp = 1
    controller.repository.save(player)


def number(key:str) -> int:
    return list(content.DRINKS).index(key) + 2


def test_menu_hides_the_feast_casks(controller:GameController) -> None:
    setup(controller)
    menu = text(controller.handle("Kerl", "!ember_cask"))
    assert "Matriarch's Cream" in menu and "Smoke Ale" in menu
    assert "Herrin's Cream" not in menu


def test_drink_heals_pays_and_buffs(controller:GameController) -> None:
    setup(controller)
    reply = text(controller.handle(
        "Kerl", f"!ember_cask {number('smoke_ale')}"))
    player = controller.repository.load("Kerl")
    assert player.gold == 1000 - 25 and player.hp > 1
    assert "ember_smoke" in player.buffs and "HP" in reply
    assert player.hp <= max_hp(player)


def test_hall_casks_are_limited_per_day(controller:GameController) -> None:
    setup(controller)
    for _ in range(content.HALL_LIMIT):
        controller.handle("Kerl", f"!ember_cask {number('council_gold')}")
    reply = text(controller.handle(
        "Kerl", f"!ember_cask {number('hall_cream')}"))
    assert "all the hall gave me" in reply
    controller.town.pass_day()
    reply = text(controller.handle(
        "Kerl", f"!ember_cask {number('hall_cream')}"))
    assert "pays" in reply


def test_matriarch_cream_can_get_you_pregnant(
        controller:GameController) -> None:
    setup(controller)
    player = controller.repository.load("Kerl")
    player.gender = "Female"
    controller.repository.save(player)
    original = content.DRINKS["matriarch_cream"]
    content.DRINKS["matriarch_cream"] = (*original[:5], 100.0, original[6])
    try:
        controller.handle("Kerl", f"!ember_cask {number('matriarch_cream')}")
    finally:
        content.DRINKS["matriarch_cream"] = original
    assert controller.repository.load("Kerl").pregnant == "party"


def test_not_enough_gold(controller:GameController) -> None:
    setup(controller, gold=5)
    reply = text(controller.handle("Kerl", f"!ember_cask {number('hall_mead')}"))
    assert "costs" in reply

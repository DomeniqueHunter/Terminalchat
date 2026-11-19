from cursed_descent.controller import GameController
from cursed_descent.towns import TOWNS, START_TOWN


def texts(messages) -> str:
    return "\n".join(message.text for message in messages)


def other_town() -> str:
    return next(key for key in TOWNS if key != START_TOWN)


def test_a_hero_from_another_town_cannot_join(
        controller:GameController) -> None:
    claudia = controller.repository.load("Galactica")
    claudia.profile["town"] = other_town()
    controller.repository.save(claudia)
    controller.handle("kerl", "!lobby", now=0.0)
    text = texts(controller.handle("Galactica", "!join", now=1.0))
    assert "Travel there first" in text
    assert controller.session.member("Galactica") is None


def test_a_hero_from_the_same_town_can_join(
        controller:GameController) -> None:
    controller.handle("kerl", "!lobby", now=0.0)
    controller.handle("Galactica", "!join", now=1.0)
    assert controller.session.member("Galactica") is not None


def test_the_lobby_town_is_forgotten_after_a_reset(
        controller:GameController) -> None:
    controller.handle("kerl", "!lobby", now=0.0)
    assert controller.session.lobby_town == START_TOWN
    controller.session.reset()
    assert controller.session.lobby_town == ""

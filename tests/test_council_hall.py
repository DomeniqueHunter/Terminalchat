from cursed_descent.controller import GameController


def setup(controller:GameController):
    player = controller.repository.load("Kerl")
    player.profile.update(town="brandholm", where="town")
    player.gold = 1000
    controller.repository.save(player)


def text(messages) -> str:
    return "\n".join(message.text for message in messages)


def test_hall_shows_menu(controller:GameController) -> None:
    setup(controller)
    out = text(controller.handle("Kerl", "!hall"))
    assert "Ask for an audience" in out
    assert "Read the Town Book" in out
    assert "Petition the Matriarch" in out


def test_audience_and_book(controller:GameController) -> None:
    setup(controller)
    controller.handle("Kerl", "!hall")
    assert "Sigrunn" in text(controller.handle("Kerl", "!hall 1"))
    assert "Town Book" in text(controller.handle("Kerl", "!hall 2"))


def test_favour_once(controller:GameController) -> None:
    setup(controller)
    controller.handle("Kerl", "!hall")
    controller.handle("Kerl", "!hall 3")
    player = controller.repository.load("Kerl")
    assert player.buffs.count("hall_favour") == 1
    assert player.gold == 700
    out = text(controller.handle("Kerl", "!hall 3"))
    assert "already" in out
    player = controller.repository.load("Kerl")
    assert player.buffs.count("hall_favour") == 1
    assert player.gold == 700


def test_favour_needs_gold(controller:GameController) -> None:
    setup(controller)
    player = controller.repository.load("Kerl")
    player.gold = 10
    controller.repository.save(player)
    controller.handle("Kerl", "!hall")
    controller.handle("Kerl", "!hall 3")
    player = controller.repository.load("Kerl")
    assert "hall_favour" not in player.buffs
    assert player.gold == 10

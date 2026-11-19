from pathlib import Path

from cursed_descent.controller import GameController
from cursed_descent.debug_goddess import GODDESS, LEVEL


def texts(messages) -> str:
    return "\n".join(message.text for message in messages)


def test_goddess_is_ignored_without_debug(
        controller:GameController) -> None:
    assert controller.handle("kerl", "!goddess") == []


def test_goddess_is_created_and_reset(data_path:Path) -> None:
    controller = GameController(data_path, debug=True)
    reply = texts(controller.handle("kerl", "!goddess"))
    assert "created" in reply
    claudia = controller.repository.load(GODDESS)
    assert claudia.level == LEVEL and claudia.gender == "Female"
    assert claudia.affinity["melee"] == 250
    assert claudia.equipment["weapon"]
    claudia.gold = 1
    assert "reset" in texts(controller.handle("kerl", "!goddess 60"))
    assert controller.repository.load(GODDESS).gold > 1


def test_goddess_clears_the_deep_stages(data_path:Path) -> None:
    controller = GameController(data_path, debug=True)
    controller.handle("kerl", "!goddess 100")
    controller.handle(GODDESS, "!lobby")
    controller.handle(GODDESS, "!start")
    session = controller.session
    now = 0.0
    for _ in range(40):
        controller.handle(GODDESS, "!stage 100", now)
        now += 1000.0
        for _ in range(12):
            if session.state != "combat":
                break
            controller.handle(GODDESS, "!hit", now)
            now += 1000.0
        assert session.living()
    assert session.stage >= 100

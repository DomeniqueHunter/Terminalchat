from cursed_descent.controller import GameController


def texts(messages) -> str:
    return "\n".join(message.text for message in messages)


def lobby(controller:GameController) -> None:
    controller.handle("kerl", "!lobby", now=0.0)
    controller.handle("Galactica", "!join", now=1.0)


def test_a_solo_start_needs_no_confirmation(
        controller:GameController) -> None:
    controller.handle("kerl", "!lobby", now=0.0)
    controller.handle("kerl", "!start", now=1.0)
    assert controller.session.state == "combat"


def test_start_waits_for_the_other_human(controller:GameController) -> None:
    lobby(controller)
    text = texts(controller.handle("kerl", "!start", now=2.0))
    assert "[ready]" in text
    assert controller.session.state == "lobby"
    assert controller.ready.waiting_for("Galactica")
    controller.handle("Galactica", "!ready", now=3.0)
    assert controller.session.state == "combat"


def test_decline_calls_the_descent_off(controller:GameController) -> None:
    lobby(controller)
    controller.handle("kerl", "!start", now=2.0)
    text = texts(controller.handle("Galactica", "!decline", now=3.0))
    assert "called off" in text
    assert controller.session.state == "lobby"
    assert not controller.ready.active()


def test_no_answer_times_out(controller:GameController) -> None:
    lobby(controller)
    controller.handle("kerl", "!start", now=2.0)
    assert controller.tick(now=30.0) == []
    text = texts(controller.tick(now=70.0))
    assert "No answer from Galactica" in text
    assert controller.session.state == "lobby"


def test_only_the_chief_can_start_and_kick(
        controller:GameController) -> None:
    lobby(controller)
    assert "opened the lobby" in texts(
        controller.handle("Galactica", "!start", now=2.0))
    assert "opened the lobby" in texts(
        controller.handle("Galactica", "!kick kerl", now=2.0))
    controller.handle("kerl", "!kick Galactica", now=3.0)
    assert controller.session.member("Galactica") is None


def test_a_held_hero_blocks_the_start(controller:GameController) -> None:
    lobby(controller)
    controller.town.held_text = lambda player: (
        "pinned" if player.name == "Galactica" else "")
    controller.ready.held_text = controller.town.held_text
    text = texts(controller.handle("kerl", "!start", now=2.0))
    assert "Galactica: pinned" in text
    assert controller.session.state == "lobby"


def test_leaving_voids_a_running_check(controller:GameController) -> None:
    lobby(controller)
    controller.handle("kerl", "!start", now=2.0)
    text = texts(controller.handle("Galactica", "!leave", now=2.5))
    assert "start check is void" in text
    assert not controller.ready.active()

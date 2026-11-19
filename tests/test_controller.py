from cursed_descent.controller import GameController
from cursed_descent.models import Player

from tests.ready import confirm


def texts(messages) -> str:
    return "\n".join(message.text for message in messages)


def test_text_without_prefix_is_ignored(controller:GameController) -> None:
    assert controller.handle("kerl", "hello there") == []


def test_unknown_command_is_ignored(controller:GameController) -> None:
    assert controller.handle("kerl", "!nonsense") == []


def test_help_is_private(controller:GameController) -> None:
    messages = controller.handle("kerl", "!help")
    assert messages and all(message.is_private for message in messages)


def test_commands_need_a_profile(controller:GameController) -> None:
    messages = controller.handle("stranger", "!profile")
    assert "[create]" in texts(messages)


def test_profile_shows_player(controller:GameController) -> None:
    assert "kerl" in texts(controller.handle("kerl", "!profile")).lower()


def test_create_via_chat_saves_player(controller:GameController) -> None:
    controller.handle("Lyra", "!create")
    controller.handle("Lyra", "Lyra Dawn")
    controller.handle("Lyra", "female")
    controller.handle("Lyra", "ok")
    controller.handle("Lyra", "rest")
    controller.handle("Lyra", "ok")
    controller.handle("Lyra", "4 2 2 2")
    messages = controller.handle("Lyra", "yes")
    assert "Character saved" in texts(messages)
    assert controller.repository.exists("Lyra")


def test_create_twice_is_refused(controller:GameController) -> None:
    assert "already have" in texts(controller.handle("kerl", "!create"))


def test_add_points_spends_free_points(controller:GameController) -> None:
    player = controller.repository.load("kerl")
    player.free_points = 3
    before = player.stats["strength"]
    controller.handle("kerl", "!add str 2")
    assert player.stats["strength"] == before + 2
    assert player.free_points == 1


def test_add_points_rejects_overspending(
        controller:GameController) -> None:
    player = controller.repository.load("kerl")
    player.free_points = 1
    messages = controller.handle("kerl", "!add str 5")
    assert "free points" in texts(messages)
    assert player.free_points == 1


def test_lobby_flow_and_surrender(controller:GameController) -> None:
    controller.handle("kerl", "!lobby")
    controller.handle("galactica", "!join")
    assert controller.session.state == "lobby"
    controller.handle("kerl", "!start", now=0.0)
    confirm(controller, 0.0)
    assert controller.session.state == "combat"
    controller.handle("kerl", "!surrender", now=1.0)
    assert controller.session.state == "idle"
    assert controller.leaderboard.entries()


def test_second_lobby_opens_its_own_slot(controller:GameController) -> None:
    controller.handle("kerl", "!lobby")
    assert "opens the gate" in texts(
        controller.handle("galactica", "!lobby"))
    assert controller.lobbies.of("kerl") is not controller.lobbies.of(
        "Galactica")


def test_shop_is_closed_during_a_run(controller:GameController) -> None:
    controller.handle("kerl", "!lobby")
    controller.handle("kerl", "!start", now=0.0)
    messages = controller.handle("kerl", "!shop")
    assert controller.session.in_run("kerl")
    assert messages and messages[0].is_private


def test_body_sync_updates_player(data_path) -> None:
    controller = GameController(data_path, debug=True)
    messages = controller.set_body("kerl", "height 190")
    assert "Body set" in texts(messages)
    assert controller.repository.load("kerl").body["height"] == 190


def test_body_set_reports_invalid_values(data_path) -> None:
    controller = GameController(data_path, debug=True)
    messages = controller.set_body("kerl", "height 5")
    assert "outside the start range" in texts(messages)


def test_body_sync_blocked_in_run(controller:GameController) -> None:
    controller.handle("kerl", "!lobby")
    controller.handle("kerl", "!start", now=0.0)
    assert "middle of a run" in texts(controller.set_body("kerl", "height 190"))


def test_top_with_empty_leaderboard(controller:GameController) -> None:
    assert "Nobody has fallen" in texts(controller.handle("kerl", "!top"))


def test_body_sync_is_refused_without_debug(
        controller:GameController) -> None:
    before = dict(controller.repository.load("kerl").body)
    messages = controller.set_body("kerl", "height 190")
    assert "clinic" in texts(messages)
    assert controller.repository.load("kerl").body == before

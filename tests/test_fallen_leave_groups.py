from cursed_descent.config import CAFE_LOCK
from cursed_descent.controller import GameController


def texts(messages) -> str:
    return "\n".join(message.text for message in messages)


def lobby(controller:GameController) -> None:
    controller.handle("kerl", "!lobby", now=0.0)
    controller.handle("Galactica", "!join", now=1.0)


def kill_in_town(controller:GameController, name:str) -> None:
    player = controller.repository.load(name)
    player.records[CAFE_LOCK] = 1
    player.last_fate = "engulfed"
    controller.repository.save(player)


def test_a_dead_member_is_removed_by_the_tick(
        controller:GameController) -> None:
    lobby(controller)
    kill_in_town(controller, "Galactica")
    text = texts(controller.tick(now=5.0))
    assert "Galactica is dead and leaves the party" in text
    assert [p.name for p in controller.session.party] == ["kerl"]


def test_the_leadership_passes_to_the_next_player(
        controller:GameController) -> None:
    lobby(controller)
    kill_in_town(controller, "kerl")
    text = texts(controller.tick(now=5.0))
    assert "Galactica leads the party now" in text
    assert controller.session.party[0].name == "Galactica"
    assert controller.session.state == "lobby"


def test_the_lobby_disbands_when_only_the_dead_were_in_it(
        controller:GameController) -> None:
    controller.handle("kerl", "!lobby", now=0.0)
    kill_in_town(controller, "kerl")
    controller.tick(now=5.0)
    assert controller.session.state == "idle"
    assert "opens the gate" in texts(
        controller.handle("Galactica", "!lobby", now=6.0))


def test_a_dead_hero_cannot_open_or_join_a_lobby(
        controller:GameController) -> None:
    kill_in_town(controller, "Galactica")
    controller.handle("kerl", "!lobby", now=0.0)
    text = texts(controller.handle("Galactica", "!join", now=1.0))
    assert "dead" in text
    assert controller.session.member("Galactica") is None


def test_group_sleep_does_not_wait_for_the_dead(
        controller:GameController) -> None:
    lobby(controller)
    kill_in_town(controller, "kerl")
    text = texts(controller.handle("Galactica", "!home sleep", now=3.0))
    assert "Waiting for" not in text
    assert "Nobody sleeps yet" not in text


def test_a_running_start_check_is_voided_when_a_member_falls(
        controller:GameController) -> None:
    lobby(controller)
    controller.handle("kerl", "!start", now=2.0)
    assert controller.ready.active()
    kill_in_town(controller, "Galactica")
    controller.tick(now=3.0)
    assert not controller.ready.active()

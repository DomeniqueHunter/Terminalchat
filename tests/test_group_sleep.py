from cursed_descent.commands import Command
from cursed_descent.controller import GameController
from tests.test_houses import texts


def form_party(controller:GameController, names:tuple[str, ...]) -> None:
    session = controller.session
    session.party = [controller.repository.load(name) for name in names]


def home_sleep(controller:GameController, name:str):
    return controller.execute_raw(name, Command("home", ("sleep",)), 0.0)


def test_a_lone_player_sleeps_without_asking(
        controller:GameController) -> None:
    kerl = controller.repository.load("kerl")
    kerl.hp = 1
    controller.repository.save(kerl)
    form_party(controller, ("kerl",))
    reply = texts(home_sleep(controller, "kerl"))
    assert "wants everyone" not in reply


def test_group_sleep_needs_everyones_yes(
        controller:GameController) -> None:
    form_party(controller, ("kerl", "galactica"))
    reply = home_sleep(controller, "kerl")
    assert "Waiting for Galactica" in texts(reply)
    assert controller.repository.load("galactica").profile["sleep_offer"]
    yes = controller.execute_raw("galactica", Command("sleep", ("yes",)),
                                 1.0)
    assert "Everyone agrees" in texts(yes)
    assert "sleep_offer" not in controller.repository.load(
        "galactica").profile


def test_a_no_cancels_the_group_sleep(controller:GameController) -> None:
    form_party(controller, ("kerl", "galactica"))
    home_sleep(controller, "kerl")
    reply = texts(controller.execute_raw(
        "galactica", Command("sleep", ("no",)), 1.0))
    assert "decline" in reply.lower()
    assert controller.group_sleep.pending is None


def test_someone_busy_blocks_everyone(controller:GameController) -> None:
    form_party(controller, ("kerl", "galactica"))
    galactica = controller.repository.load("galactica")
    galactica.profile["home_sex"] = "kerl"
    controller.repository.save(galactica)
    reply = texts(home_sleep(controller, "kerl"))
    assert "Nobody sleeps yet" in reply and "private scene" in reply
    assert controller.group_sleep.pending is None


def test_an_old_request_expires(controller:GameController) -> None:
    form_party(controller, ("kerl", "galactica"))
    home_sleep(controller, "kerl")
    reply = texts(controller.execute_raw(
        "galactica", Command("sleep", ("yes",)), 9999.0))
    assert "Nobody is asking" in reply


def test_autopilot_members_do_not_have_to_answer(
        controller:GameController) -> None:
    form_party(controller, ("kerl", "galactica"))
    controller.session.autopilot.add("Galactica")
    reply = texts(home_sleep(controller, "kerl"))
    assert "wants everyone" not in reply


def test_dungeon_sleep_in_a_hut_asks_the_group(
        controller:GameController) -> None:
    form_party(controller, ("kerl", "galactica"))
    session = controller.session
    session.state = "event"
    session.events.event = {"phase": "hut", "used": set(), "data": {}}
    reply = texts(controller.execute_raw("kerl", Command("sleep"), 0.0))
    assert "Waiting for Galactica" in reply
    assert controller.group_sleep.pending["kind"] == "dungeon"

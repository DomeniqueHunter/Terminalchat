from cursed_descent.controller import GameController
from cursed_descent.dungeon import grant_exp
from cursed_descent.events.maid.event import make_companion
from cursed_descent.main_char import MainChar
from tests.test_enter_buildings import texts
from tests.test_maid import start_pair


def with_connie(controller:GameController):
    start_pair(controller)
    session = controller.session
    connie = make_companion(1)
    session.repository.add(connie)
    session.party.append(connie)
    return session, connie


def test_connie_stays_in_the_party_through_the_town_pause(
        controller:GameController) -> None:
    session, connie = with_connie(controller)
    session.pause_run("last_light")
    assert session.state == "paused"
    assert session.member("Connie") is not None
    assert session.repository.exists("Connie")


def test_connie_gets_her_bonus_on_every_level_up(
        controller:GameController) -> None:
    session, connie = with_connie(controller)
    vit, strength, level = (connie.stats["vitality"],
                            connie.stats["strength"], connie.level)
    grant_exp(connie, 10 ** 6)
    gained = connie.level - level
    assert gained > 1
    assert connie.stats["vitality"] == vit + gained * 4
    assert connie.stats["strength"] == strength + gained * 2


def test_other_companions_get_no_connie_bonus(
        controller:GameController) -> None:
    session, connie = with_connie(controller)
    kerl = session.member("kerl")
    vit = kerl.stats["vitality"]
    grant_exp(kerl, 10 ** 6)
    assert kerl.stats["vitality"] == vit


def test_hand_over_in_the_school_while_the_run_waits(
        controller:GameController) -> None:
    session, connie = with_connie(controller)
    session.pause_run("last_light")
    reply = texts(controller.handle("kerl", "!maidschool handover"))
    assert "Brunhild" in reply
    assert session.member("Connie") is None
    assert not session.repository.exists("Connie")
    assert session.buster_ledger.meta["handed_over"] == 1


def test_hand_over_without_connie_does_nothing(
        controller:GameController) -> None:
    start_pair(controller)
    controller.session.pause_run("last_light")
    reply = texts(controller.handle("kerl", "!maidschool handover"))
    assert "not with your party" in reply


def test_main_char_is_remembered_and_moves_on_when_it_is_gone(
        tmp_path) -> None:
    main = MainChar(tmp_path)
    main.set("Beverley")
    assert MainChar(tmp_path).name == "Beverley"
    assert main.resolve(["Claudia", "Beverley"]) == "Beverley"
    assert main.resolve(["Claudia", "Galactica"]) == "Claudia"
    assert MainChar(tmp_path).name == "Claudia"
    assert main.resolve([]) == ""

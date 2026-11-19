from pathlib import Path

from cursed_descent.config import MAID_PRICE_FACTOR, NPC_HIRE_PRICE
from cursed_descent.npcs.hire import hire_price, is_maid
from tests.npc_factory import maid, merc
from cursed_descent.towns.last_light_humans.maidschool.school import (
    Record, SchoolLedger, school,
)
from cursed_descent.models import Player


def hero() -> Player:
    player = Player(name="Hero")
    player.gold = 1000
    return player


def text(messages) -> str:
    return "\n".join(message.text for message in messages)


def test_course_takes_three_attended_days_then_grants_the_bonus() -> None:
    player, record = hero(), Record()
    before = player.stats["strength"]
    butt = player.body["butt"]
    school(player, record, ["learn", "fagsquat"], False)
    assert player.gold == 850 and record.course == "fagsquat"
    first = text(school(player, record, ["day"], False))
    assert "Day 1" in first and record.days_done == 1
    school(player, record, ["day"], False)
    assert player.stats["strength"] == before
    last = text(school(player, record, ["day"], False))
    assert "Day 3" in last and "learned" in last
    assert player.stats["strength"] == before + 3
    assert player.body["butt"] == butt + 4
    assert record.learned == ["fagsquat"] and record.course == ""


def test_days_do_not_pass_by_themselves() -> None:
    player, record = hero(), Record()
    school(player, record, ["learn", "manners"], False)
    player.records["runs"] += 5
    school(player, record, [], False)
    assert record.course == "manners" and record.days_done == 0


def test_every_course_has_one_lesson_per_day() -> None:
    from cursed_descent.towns.last_light_humans.maidschool.content import COURSES, LESSONS
    from cursed_descent.config import COURSE_DAYS
    assert set(LESSONS) == set(COURSES)
    assert all(len(lessons) == COURSE_DAYS for lessons in LESSONS.values())


def test_quit_forfeits_the_course() -> None:
    player, record = hero(), Record()
    school(player, record, ["learn", "manners"], False)
    school(player, record, ["day"], False)
    reply = text(school(player, record, ["quit"], False))
    assert "fee is gone" in reply and record.course == ""
    assert player.gold == 850 and record.learned == []


def test_attending_without_a_course_does_nothing() -> None:
    assert "not enrolled" in text(school(hero(), Record(), ["day"], False))


def test_training_locks_the_character_in_the_school(controller) -> None:
    controller.handle("Kerl", "!maidschool learn manners")
    for command in ("!lobby", "!join", "!bank", "!tavern", "!job tavern "
                    "waiter", "!shop", "!clinic", "!smith", "!book classic"):
        reply = text(controller.handle("Kerl", command))
        assert "training" in reply and "Maid School" in reply, command
    assert controller.session.state == "idle"
    assert "Meals" in text(controller.handle("Kerl", "!maidschool day"))
    assert "In training" in text(controller.handle("Kerl", "!maidschool"))
    assert "Last Light" in text(controller.handle("Kerl", "!town"))
    controller.handle("Kerl", "!maidschool day")
    controller.handle("Kerl", "!maidschool day")
    assert controller.session.state == "idle"
    assert "training" not in text(controller.handle("Kerl", "!bank"))


def test_ledger_persists(tmp_path:Path) -> None:
    player = hero()
    ledger = SchoolLedger(tmp_path)
    record = ledger.record(player)
    record.learned.append("manners")
    ledger.save()
    assert SchoolLedger(tmp_path).record(player).learned == ["manners"]


def test_maids_are_hireable_in_uniform_for_double() -> None:
    lotte = maid("Lotte")
    assert is_maid(lotte) and lotte.equipment["chest"] == "maid_uniform"
    brom = merc("Brom")
    assert not is_maid(brom) and hire_price(lotte) == 2 * hire_price(brom)


def test_enroll_needs_confirmation_and_makes_a_graduate(controller) -> None:
    warning = text(controller.handle("Kerl", "!maidschool enroll"))
    assert "confirm" in warning
    assert controller.repository.path("Kerl").exists()
    player = controller.repository.load("Kerl")
    player.inventory = ["potion_small"]
    player.equipment["weapon"] = None
    controller.handle("Kerl", "!maidschool enroll confirm")
    assert not controller.repository.path("Kerl").exists()
    maid = controller.repository.load("Kerl")
    assert maid.npc == "maid" and maid.inventory == []
    assert maid.equipment["chest"] == "maid_uniform"
    assert "kerl" not in [n.casefold() for n in controller.repository.names()]
    assert [g.name.casefold() for g in controller.repository.graduates()] == [
        "kerl"]


def test_buyback_returns_the_character(controller) -> None:
    buyer = controller.repository.load("Galactica")
    buyer.gold = 5000
    controller.repository.save(buyer)
    controller.handle("Kerl", "!maidschool enroll")
    controller.handle("Kerl", "!maidschool enroll confirm")
    reply = text(controller.handle("Galactica", "!maidschool buyback Kerl"))
    assert "free adventurer" in reply
    freed = controller.repository.load("Kerl")
    assert freed.npc == "" and controller.repository.path("Kerl").exists()
    assert not controller.repository.npc_path("Kerl").exists()
    assert "kerl" in [n.casefold() for n in controller.repository.names()]


def test_party_members_cannot_enroll(controller) -> None:
    controller.handle("Kerl", "!lobby")
    assert "Leave the lobby" in text(
        controller.handle("Kerl", "!maidschool enroll confirm"))



def test_graduates_can_be_hired_as_companions(controller) -> None:
    controller.handle("Kerl", "!maidschool enroll")
    controller.handle("Kerl", "!maidschool enroll confirm")
    buyer = controller.repository.load("Galactica")
    buyer.gold = 5000
    controller.repository.save(buyer)
    controller.handle("Galactica", "!lobby")
    assert "kerl (Lv" in text(controller.handle("Galactica", "!hire"))
    price = hire_price(controller.repository.load("Kerl"))
    assert price == NPC_HIRE_PRICE * controller.repository.load(
        "Kerl").level * MAID_PRICE_FACTOR
    reply = text(controller.handle("Galactica", "!hire Kerl"))
    assert "joins the party" in reply
    assert [m.name for m in controller.session.party] == ["Galactica", "kerl"]
    assert controller.session.is_auto(controller.session.party[1])
    assert controller.repository.load("Galactica").gold == 5000 - price
    assert controller.repository.load("Kerl").npc == "maid"
    assert "leaves the party" in text(controller.handle("Galactica",
                                                         "!dismiss Kerl"))


def test_graduate_hire_needs_the_gold(controller) -> None:
    controller.handle("Kerl", "!maidschool enroll")
    controller.handle("Kerl", "!maidschool enroll confirm")
    broke = controller.repository.load("Galactica")
    broke.gold = 0
    controller.repository.save(broke)
    controller.handle("Galactica", "!lobby")
    assert "wants" in text(controller.handle("Galactica", "!hire Kerl"))


def test_the_enroll_confirmation_expires(controller) -> None:
    from cursed_descent.towns.last_light_humans.maidschool import building
    services = controller.town
    controller.handle("Kerl", "!maidschool enroll")
    assert building.armed(services, "kerl")
    services.enroll_armed["kerl"] -= building.ARM_SECONDS + 1
    assert not building.armed(services, "kerl")
    reply = text(controller.handle("Kerl", "!maidschool enroll confirm"))
    assert "too long" in reply
    assert controller.repository.path("Kerl").exists()


def test_a_dead_hired_maid_dissolves_but_a_graduate_stays(
        controller) -> None:
    session = controller.session
    repository = controller.repository
    hired = Player(name="Hanna", first_name="Hanna", npc="maid")
    hired.profile = {"owner": "kerl"}
    graduate = Player(name="Grete", first_name="Grete", npc="maid")
    graduate.profile = {"graduate": True}
    for maid in (hired, graduate):
        repository.add(maid)
        session.party.append(maid)
    for maid in (hired, graduate):
        session.kill_outside(maid, "paddle_popped", "x", "test", "test")
    assert hired not in session.party and not repository.exists("Hanna")
    assert graduate in session.party and repository.exists("Grete")

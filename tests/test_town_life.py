import random

from cursed_descent.town_buildings.locals import meet, rumors
from cursed_descent.models import Player
from cursed_descent.npcs.seed import resident_player
from cursed_descent.npcs.store import find_local
from cursed_descent.towns import START_TOWN, TOWNS, town_text


TOWN = TOWNS[START_TOWN]


def text(messages) -> str:
    return "\n".join(message.text for message in messages)


def test_every_resident_is_an_adult_with_a_complete_profile() -> None:
    assert {r.building for r in TOWN.residents} >= set(TOWN.buildings)
    for resident in TOWN.residents:
        assert resident.age >= 18 and resident.personality and resident.look
        assert len(resident.quotes) >= 3
        sheet = resident_player(resident)
        assert sheet.age == resident.age and sheet.gender == resident.gender


def test_meet_lists_and_describes_locals() -> None:
    hero = Player(name="Hero")
    locals_ = [resident_player(r) for r in TOWN.residents]
    listing = text(meet(TOWN, hero, "", random.Random(1), locals_))
    assert "Hilda" in listing and "Madame of the Rose Chamber" in listing
    report = text(meet(TOWN, hero, "rose", random.Random(1), locals_))
    assert "Age: 41" in report and "Personality:" in report
    assert "Bust:" in report
    assert "Nobody" in text(meet(TOWN, hero, "nobody", random.Random(1), locals_))
    assert find_local(locals_, "Rose Valmont").npc == "rose"


def test_rumors_give_three_lines_and_mention_the_record() -> None:
    hero = Player(name="Hero")
    hero.records["deepest_stage"] = 12
    reply = text(rumors(TOWN, hero, random.Random(2)))
    assert reply.count("•") == 4 and "stage 12" in reply


def test_town_text_shows_happening_and_locals() -> None:
    shown = town_text(TOWN, "A cat sits in a window.")
    assert "✦ A cat sits" in shown and "Locals" in shown and "rumors" in shown


def test_commands_through_the_controller(controller) -> None:
    assert "✦" in text(controller.handle("Kerl", "!town"))
    assert "Brunhild" in text(controller.handle("Kerl", "!meet brunhild"))
    assert "•" in text(controller.handle("Kerl", "!rumors"))


def test_incidents_can_add_tips_to_a_shift() -> None:
    from cursed_descent.town_buildings.shifts import work
    seen = False
    for seed in range(40):
        player = Player(name="Hero", gender="Male")
        reply = text(work(player, "tavern", "waiter", False, {},
                          random.Random(seed)))
        seen = seen or "✦" in reply
    assert seen


def test_chat_warms_up_over_time_and_persists(tmp_path) -> None:
    from cursed_descent import GameController
    controller = GameController(tmp_path)
    controller.repository.save(Player(name="Hero"))
    first = text(controller.handle("Hero", "!chat hilda work"))
    assert "New face" in first and "'" in first
    assert "Hilda" in text(controller.handle("Hero", "!chat"))
    controller.handle("Hero", "!chat hilda")
    third = text(controller.handle("Hero", "!chat hilda"))
    assert "now counts you as: acquaintance" in third
    again = GameController(tmp_path)
    assert "Back again" in text(again.handle("Hero", "!chat hilda town"))
    assert "Nobody" in text(again.handle("Hero", "!chat zzz"))
    assert "Nobody" in text(again.handle("Hero", "!chat astrid"))


def test_every_resident_has_all_three_topics() -> None:
    for resident in TOWN.residents:
        assert {topic for topic, _ in resident.topics} == {
            "work", "town", "self"}

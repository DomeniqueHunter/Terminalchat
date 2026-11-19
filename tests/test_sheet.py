from cursed_descent.migrations import migrate_player
from cursed_descent.models import Player
from tests.npc_factory import maid, merc
from cursed_descent.sheet import sheet_lines


def text(messages) -> str:
    return "\n".join(message.text for message in messages)


def test_age_and_personality_are_saved_and_default_to_adult() -> None:
    player = Player(name="Hero")
    assert player.age == 21 and player.personality == ""
    player.age, player.personality = 34, "dry and stubborn"
    again = Player.from_dict(player.to_dict())
    assert again.age == 34 and again.personality == "dry and stubborn"


def test_old_saves_get_age_and_personality() -> None:
    data = Player(name="Hero").to_dict()
    del data["age"], data["personality"]
    data["schema_version"] = 3
    migrated, changed = migrate_player(data)
    assert changed and migrated["age"] == 21 and migrated["personality"] == ""


def test_every_generated_npc_is_an_adult_with_a_personality() -> None:
    import random
    from cursed_descent.npcs.generator import make_maid, make_mercenary
    rng = random.Random(3)
    for _ in range(200):
        for npc in (make_maid(rng, set()), make_mercenary(rng, set())):
            assert npc.age >= 18 and npc.personality


def test_sheet_shows_age_personality_and_anatomy() -> None:
    player = Player(name="Hero", gender="Male", age=30,
                    personality="bold")
    lines = "\n".join(sheet_lines(player))
    for part in ("Age: 30", "Personality: bold", "Bust:", "Cock:",
                 "Balls:", "Build:"):
        assert part in lines
    female = "\n".join(sheet_lines(Player(name="Ann", gender="Female")))
    assert "Cock: none" in female


def test_age_command_validates(controller) -> None:
    assert "years old" in text(controller.handle("Kerl", "!age 30"))
    assert controller.repository.load("Kerl").age == 30
    assert "must be" in text(controller.handle("Kerl", "!age 17"))
    assert controller.repository.load("Kerl").age == 30
    assert "must be" in text(controller.handle("Kerl", "!age abc"))


def test_personality_command(controller) -> None:
    controller.handle("Kerl", "!personality shy but curious")
    assert controller.repository.load("Kerl").personality == (
        "shy but curious")
    controller.handle("Kerl", "!personality " + "x" * 200)
    assert len(controller.repository.load("Kerl").personality) == 80


def test_profile_and_sheet_show_it_for_chars_and_npcs(controller) -> None:
    controller.handle("Kerl", "!age 33")
    assert "Age: 33" in text(controller.handle("Kerl", "!profile"))
    assert "Age: 33" in text(controller.handle("Kerl", "!sheet"))
    lotte = maid("Lotte")
    controller.repository.add(lotte)
    report = text(controller.handle("Kerl", "!profile Lotte"))
    assert "Age: 24" in report
    assert "Personality: hard-working" in report and "NPC" in report


def test_npcs_cannot_change_their_age(controller) -> None:
    lotte = maid("Lotte")
    controller.repository.add(lotte)
    assert "keep" in text(controller.handle("Lotte", "!age 40"))

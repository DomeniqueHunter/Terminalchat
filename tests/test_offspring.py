import random

from cursed_descent.births import age_offspring, child_label, give_birth
from cursed_descent.config import GROWN_UP_RUNS
from cursed_descent.models import Player


def carrier(kind:str="party") -> Player:
    player = Player(name="Nick Morningwood", id="n", gender="Male", age=30)
    player.first_name = "Nick"
    player.last_name = "Morningwood"
    player.pregnant = kind
    return player


def test_child_gets_the_surname_of_the_birthing_person() -> None:
    nick = carrier()
    text = give_birth(nick, random.Random(1))
    child = nick.offspring[0]
    assert child["surname"] == "Morningwood" and child["species"] == "human"
    assert "Morningwood" in text and "human" in child_label(child)


def test_ogre_child_is_listed_as_ogre() -> None:
    nick = carrier("ogre")
    give_birth(nick, random.Random(1))
    assert nick.offspring[0]["species"] == "ogre"


def test_children_grow_up_after_twenty_runs_and_leave() -> None:
    nick = carrier()
    give_birth(nick, random.Random(1))
    for _ in range(GROWN_UP_RUNS - 1):
        assert age_offspring(nick) == []
    lines = age_offspring(nick)
    assert "adventurer" in lines[0] and not nick.offspring
    ogre = carrier("ogre")
    give_birth(ogre, random.Random(1))
    for _ in range(GROWN_UP_RUNS - 1):
        age_offspring(ogre)
    assert "an ogre" in age_offspring(ogre)[0]


def test_grown_children_are_kept_as_temp_monsters_until_they_die(
        repository, empty_data_path) -> None:
    store = repository.temp_monsters
    ogre = carrier("ogre")
    give_birth(ogre, random.Random(1))
    for _ in range(GROWN_UP_RUNS):
        age_offspring(ogre, store)
    (entry,) = store.all()
    assert entry["role"] == "grown_child" and entry["species"] == "ogre"
    assert (empty_data_path / "temp_monster" / f"{entry['id']}.json").exists()
    assert store.die(entry["id"], "slain on stage 5")
    assert store.all() == [] and not store.die(entry["id"], "again")
    buried = list((empty_data_path / "graveyard").glob("monster_*.json"))
    assert len(buried) == 1


def test_grown_children_meet_the_party_and_are_buried_when_slain(
        controller, monkeypatch, data_path) -> None:
    from cursed_descent import session as session_module
    from cursed_descent.dungeon import spawn_stage
    game = controller.session
    store = controller.repository.temp_monsters
    ogre = carrier("ogre")
    give_birth(ogre, random.Random(1))
    for _ in range(GROWN_UP_RUNS):
        age_offspring(ogre, store)
    monkeypatch.setattr(session_module, "TEMP_MONSTER_CHANCE", 1.0)
    game.stage = 3
    game.enemies = spawn_stage(3)
    lines = game.add_temp_monster()
    enemy = game.enemies[-1]
    assert enemy.temp_id and "grown-up ogre" in lines[0]
    assert game.add_temp_monster() == [] or len(game.enemies) > 1
    enemy.killed_by = "kerl"
    assert "graveyard" in game.fell_temp_monster(enemy)[0]
    assert store.all() == []
    assert list((data_path / "graveyard").glob("monster_*.json"))

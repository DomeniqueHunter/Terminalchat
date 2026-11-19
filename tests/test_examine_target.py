from pathlib import Path

from cursed_descent import GameController
from cursed_descent.examine_target import (
    bulge_word, enemy_report, find_enemy, visible_anatomy,
)
from cursed_descent.models import Enemy, Player
from tests.npc_factory import add_merc
from tests.npc_files import npc_file, npc_keys


def make_enemy() -> Enemy:
    return Enemy(uid=1, template_id="rat", name="Giant Rat", max_hp=18,
                 hp=18, attack=5, defense=0, agility=6, exp=6,
                 fates=["eaten"], actions=[("attack", 100)],
                 melee_mult=0.5, tribe="monsters")


def say(controller:GameController, sender:str, text:str) -> str:
    return "\n".join(m.text for m in controller.handle(sender, text))


def test_enemy_report_lists_stats_and_traits() -> None:
    text = "\n".join(enemy_report(make_enemy()))
    assert "Giant Rat" in text and "attack 5" in text
    assert "shrugs off melee" in text and "eaten" in text


def test_find_enemy_by_uid_and_name_skips_dead() -> None:
    rat = make_enemy()
    assert find_enemy([rat], "1") is rat
    assert find_enemy([rat], "rat") is rat
    rat.hp = 0
    assert find_enemy([rat], "rat") is None


def test_crotch_gear_turns_the_cock_into_a_bulge_but_a_bra_does_not() -> None:
    player = Player(name="Brom", gender="Male")
    player.body["endowment"] = 25
    player.equipment["lingerie"] = "maid_uniform"
    assert any("25 cm long" in line for line in visible_anatomy(player))
    player.equipment["crotch"] = "maid_uniform"
    lines = visible_anatomy(player)
    assert any("heavy bulge" in line for line in lines)
    assert not any("25 cm" in line for line in lines)
    assert bulge_word(40) == "an enormous"


def test_examine_a_resident_a_mercenary_and_nobody(tmp_path:Path) -> None:
    controller = GameController(tmp_path)
    hero = Player(name="Hero")
    controller.repository.save(hero)
    assert "Madame" in say(controller, "Hero", "!examine rose")
    assert "Age:" in say(controller, "Hero", "!examine hero")
    assert "nobody called" in say(controller, "Hero", "!examine zzz")


def test_story_npcs_and_recruitable_npcs_live_in_separate_folders(
        tmp_path:Path) -> None:
    controller = GameController(tmp_path)
    story = npc_keys(tmp_path, True)
    recruits = npc_keys(tmp_path, False)
    assert {"hilda", "rose", "astrid", "sir_reginald", "madame_vesper",
            "queen_isolde", "hamhock", "old_trotter"} <= story
    assert recruits == set()
    assert not story & recruits
    for npc in controller.repository.npc_players():
        assert npc.age >= 18 and npc.personality and npc.npc
        assert npc.profile.get("kind")
    assert controller.repository.names() == []


def test_examine_astrid_and_edited_json_wins(tmp_path:Path) -> None:
    controller = GameController(tmp_path)
    controller.repository.save(Player(name="Hero"))
    assert "Age: 54" in say(controller, "Hero", "!examine astrid")
    npc = controller.repository.load("Astrid")
    npc.age = 60
    controller.repository.save(npc)
    again = GameController(tmp_path)
    assert "Age: 60" in say(again, "Hero", "!examine astrid")


def test_a_player_can_become_an_npc_and_back(tmp_path:Path) -> None:
    controller = GameController(tmp_path)
    repo = controller.repository
    repo.add(Player(name="Wanderer"))
    assert repo.convert("Wanderer", "custom")
    assert not repo.path("Wanderer").exists()
    assert repo.npc_path("Wanderer").exists()
    assert "Wanderer" not in repo.names()
    assert repo.convert("Wanderer", "")
    assert repo.path("Wanderer").exists()
    assert not repo.npc_path("Wanderer").exists()
    assert "Wanderer" in repo.names()


def test_rose_and_astrid_are_hung_far_beyond_the_normal() -> None:
    from cursed_descent.npcs.seed import default_npcs
    npcs = {npc.npc: npc for npc in default_npcs()}
    assert npcs["astrid"].body["endowment"] >= 50
    assert npcs["astrid"].body["balls"] >= 15
    assert npcs["rose"].body["endowment"] >= 30
    for key in ("astrid", "rose"):
        assert npcs[key].gender in ("Shemale", "Herm", "Male")


def test_astrid_and_velvet_count_the_kills_they_make(tmp_path:Path) -> None:
    controller = GameController(tmp_path)
    session = controller.session
    victim = Player(name="Victim")
    controller.repository.save(victim)
    session.kill_outside(victim, "brewed", "text", "Astrid", "brewers")
    session.kill_outside(victim, "brewed", "text", "Astrid", "brewers")
    session.kill_outside(victim, "fashion", "text", "Velvet", "designers")
    session.kill_outside(victim, "farmed", "text", "Farm", "pigmen")
    repo = GameController(tmp_path).repository
    assert repo.load("Astrid").records["kills"] == 2
    assert repo.load("Velvet").records["kills"] == 1
    assert repo.load("Hilda").records["kills"] == 0
    reply = say(controller, "Victim", "!examine astrid")
    assert "Kills: 2" in reply


def test_astrid_sometimes_leaves_a_pubic_hair_in_the_cup(
        monkeypatch) -> None:
    from types import SimpleNamespace
    from cursed_descent.locations.brewery import location
    from cursed_descent.locations.brewery.location import BreweryMixin

    class Stub(BreweryMixin):
        def __init__(self) -> None:
            self.event = {"kind": "brewery", "data": {"fresh_left": 5}}
            self.session = SimpleNamespace(
                repository=SimpleNamespace(save=lambda player: None))

        def brewery_options_line(self) -> str:
            return ""

    def pour(roll:float) -> str:
        monkeypatch.setattr(location.random, "random", lambda: roll)
        player = Player(name="Hero")
        player.gold = 10_000
        return "\n".join(m.text for m in Stub().brewery_fresh(player))

    assert "pubic hair" in pour(0.0)
    assert "pubic hair" not in pour(0.99)


def test_named_event_figures_have_npc_files_and_show_up_in_examine(
        tmp_path:Path) -> None:
    controller = GameController(tmp_path)
    controller.repository.save(Player(name="Hero"))
    files = npc_keys(tmp_path, True)
    assert {"sir_reginald", "madame_vesper", "queen_isolde", "hamhock",
            "old_trotter"} <= files
    assert "Age: 58" in say(controller, "Hero", "!examine reginald")
    assert "Age: 71" in say(controller, "Hero", "!examine trotter")
    assert "Hamhock" not in say(controller, "Hero", "!meet")


def test_examining_the_hunter_in_combat_adds_his_sheet(
        tmp_path:Path) -> None:
    controller = GameController(tmp_path)
    hero = Player(name="Hero")
    controller.repository.save(hero)
    session = controller.session
    session.open_lobby(hero)
    hunter = make_enemy()
    hunter.name = "Sir Reginald Thornbury"
    session.enemies = [hunter]
    session.state = "combat"
    reply = say(controller, "Hero", "!examine reginald")
    assert "Age: 58" in reply


def test_every_fate_with_shemale_or_herm_texts_also_has_male_texts() -> None:
    from cursed_descent.content import FATES
    gaps = [fate for fate, pool in FATES.items()
            if ("Shemale" in pool or "Herm" in pool) and "Male" not in pool]
    assert gaps == []


def test_no_mercenary_or_maid_is_created_until_hired(
        tmp_path:Path) -> None:
    controller = GameController(tmp_path)
    assert npc_keys(tmp_path, False) == set()
    hero = Player(name="Hero", gold=1000)
    controller.repository.save(hero)
    add_merc(controller, "Brom")
    say(controller, "Hero", "!lobby")
    say(controller, "Hero", "!hire brom")
    assert controller.repository.npc_path("Brom").exists()
    assert not controller.repository.npc_path("Mara").exists()
    assert controller.repository.load("Brom").profile["kind"] == "mercenary"

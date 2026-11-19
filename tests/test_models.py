from cursed_descent.config import AFFINITY_NAMES
from cursed_descent.models import Enemy, Message, Player


def test_player_roundtrip_keeps_persisted_fields() -> None:
    player = Player(name="Lyra", gender="Female", level=4, gold=99)
    player.stats["strength"] = 12
    player.inventory.append("potion_small")
    player.pregnant = "orc"
    clone = Player.from_dict(player.to_dict())
    assert clone.to_dict() == player.to_dict()


def test_title_is_novice_without_affinity(hero:Player) -> None:
    assert hero.title == "Novice"


def test_title_uses_top_affinity(hero:Player) -> None:
    hero.affinity["melee"] = 100
    assert hero.title != "Novice"


def test_combo_title_when_second_affinity_is_close(hero:Player) -> None:
    hero.affinity["melee"] = 100
    hero.affinity["magic"] = 80
    single = Player(name="Solo")
    single.affinity["melee"] = 100
    assert hero.title != single.title


def test_fix_equipment_drops_unknown_items(hero:Player) -> None:
    hero.equipment["weapon"] = "does_not_exist"
    hero.fix_equipment()
    assert hero.equipment["weapon"] is None


def test_legacy_goblin_deaths_become_breeding() -> None:
    data = Player(name="Old").to_dict()
    data["schema_version"] = 1
    data["deaths"] = {"goblins": 2, "breeding": 1}
    player = Player.from_dict(data)
    assert player.deaths == {"breeding": 3}


def test_add_affinity_accumulates(hero:Player) -> None:
    hero.add_affinity("magic", 3)
    hero.add_affinity("magic")
    assert hero.affinity["magic"] == 4
    assert set(hero.affinity) == set(AFFINITY_NAMES)


def test_message_privacy_depends_on_recipient() -> None:
    assert Message("hi", "Lyra").is_private
    assert not Message("hi").is_private


def test_enemy_alive_and_label() -> None:
    enemy = Enemy(uid=3, template_id="rat", name="Rat", max_hp=5, hp=5,
                  attack=1, defense=0, agility=1, exp=1, fates=[],
                  actions=[("attack", 100)])
    assert enemy.alive and enemy.label == "[3] Rat"
    enemy.hp = 0
    assert not enemy.alive


def test_unknown_legacy_affinity_is_folded_in() -> None:
    from cursed_descent.models import Player
    data = Player(name="Old", gender="Male").to_dict()
    data["affinity"] = {"fire": 7, "mystery": 3}
    player = Player.from_dict(data)
    assert set(player.affinity) == {"melee", "magic", "dodge", "guard",
                                    "heal"}
    assert player.affinity["magic"] == 7

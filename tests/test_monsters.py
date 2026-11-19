import importlib
from pathlib import Path

from cursed_descent.content import ENEMIES
from cursed_descent.monster.order import ENEMY_ORDER


MONSTER_DIR = Path(__file__).parent.parent / "cursed_descent" / "monster"


def group_names() -> list[str]:
    return sorted(path.name for path in MONSTER_DIR.iterdir()
                  if path.is_dir() and path.name != "__pycache__")


def test_every_enemy_lives_in_exactly_one_group() -> None:
    seen: list[str] = []
    for group in group_names():
        module = importlib.import_module(
            f"cursed_descent.monster.{group}.content")
        seen += list(module.ENEMIES)
    assert sorted(seen) == sorted(ENEMY_ORDER) == sorted(ENEMIES)


def test_enemy_order_is_kept() -> None:
    assert list(ENEMIES) == list(ENEMY_ORDER)


def test_every_enemy_declares_its_stage_range() -> None:
    for template in ENEMIES.values():
        assert "min_stage" in template and "max_stage" in template

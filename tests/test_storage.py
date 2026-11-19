from pathlib import Path

from cursed_descent.config import LEADERBOARD_SIZE
from cursed_descent.models import Player
from cursed_descent.storage import (
    Leaderboard, PlayerRepository, read_json, write_json,
)


def test_write_json_is_atomic_and_readable(tmp_path:Path) -> None:
    target = tmp_path / "nested" / "data.json"
    write_json(target, {"ä": [1, 2]})
    assert read_json(target, None) == {"ä": [1, 2]}
    assert not list(target.parent.glob("*.tmp"))


def test_read_json_returns_default_for_missing_file(tmp_path:Path) -> None:
    assert read_json(tmp_path / "missing.json", ["x"]) == ["x"]


def test_repository_key_is_filesystem_safe() -> None:
    assert PlayerRepository.key("  Lyra O'Neil/../x ") == "lyra_o_neil____x"


def test_repository_add_load_exists(repository:PlayerRepository) -> None:
    assert not repository.exists("Lyra")
    repository.add(Player(name="Lyra", gold=5))
    assert repository.exists("lyra")
    assert repository.load("LYRA").gold == 5


def test_repository_persists_between_instances(
        repository:PlayerRepository) -> None:
    repository.add(Player(name="Lyra", gold=5))
    fresh = PlayerRepository(repository.data_path)
    assert fresh.load("Lyra").gold == 5


def test_repository_returns_none_for_unknown_player(
        repository:PlayerRepository) -> None:
    assert repository.load("nobody") is None


def test_leaderboard_ranks_and_trims(empty_data_path:Path) -> None:
    board = Leaderboard(empty_data_path)
    assert board.add_run(5, ["a"]) == 1
    assert board.add_run(9, ["b"]) == 1
    assert board.add_run(7, ["c"]) == 2
    for stage in range(10, 10 + LEADERBOARD_SIZE):
        board.add_run(stage, ["x"])
    assert len(board.entries()) == LEADERBOARD_SIZE
    assert board.add_run(1, ["last"]) == 0

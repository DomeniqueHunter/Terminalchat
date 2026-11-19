import shutil
from pathlib import Path

import pytest

from tests.fixture_data import build

from cursed_descent.controller import GameController
from cursed_descent.models import Player
from cursed_descent.storage import PlayerRepository


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "game_data"


@pytest.fixture
def data_path(tmp_path:Path) -> Path:
    target = tmp_path / "game_data"
    build(target)
    return target


@pytest.fixture
def empty_data_path(tmp_path:Path) -> Path:
    target = tmp_path / "empty_data"
    target.mkdir()
    return target


@pytest.fixture
def controller(data_path:Path) -> GameController:
    game = GameController(data_path)
    game.town.ambient_on = False
    game.town.visits_on = False
    return game


@pytest.fixture
def repository(empty_data_path:Path) -> PlayerRepository:
    return PlayerRepository(empty_data_path)


@pytest.fixture
def hero() -> Player:
    return Player(name="Hero", gender="Male")


@pytest.fixture(autouse=True)
def no_operator_drop_ins(monkeypatch) -> None:
    from cursed_descent.town_buildings.brothel import shift
    monkeypatch.setattr(shift, "ROSE_MID_CHANCE", 0.0)
    monkeypatch.setattr(shift, "ROSE_MID_SUB_CHANCE", 0.0)

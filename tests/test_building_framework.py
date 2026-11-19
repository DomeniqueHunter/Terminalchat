import shutil
import sys
from pathlib import Path

import pytest

from cursed_descent.town_buildings import Building, discovery, registry
from cursed_descent.towns import TOWNS, town_text


TOWN_DIR = discovery.TOWNS_DIR / "mudgate_goblins"
MINIMAL = '''from ....town_buildings import Building


class Hut(Building):
    key = "{name}"
    title = "Test Hut"
    blurb = "A hut for testing."
    greeting = "Welcome to the hut."


BUILDING = Hut()
'''


def reset() -> None:
    discovery._MOUNTED.clear()
    registry._SPECS.clear()


@pytest.fixture
def hut():
    folders = []

    def make(name:str, source:str="") -> Path:
        folder = TOWN_DIR / name
        folder.mkdir()
        folders.append(folder)
        (folder / "__init__.py").write_text(
            source or MINIMAL.format(name=name), encoding="utf-8")
        reset()
        return folder

    yield make
    for folder in folders:
        shutil.rmtree(folder, ignore_errors=True)
        for module in [m for m in sys.modules
                       if m.endswith(f"mudgate_goblins.{folder.name}")]:
            del sys.modules[module]
    reset()


def test_a_folder_with_a_building_is_mounted(hut) -> None:
    hut("testhut")
    town = TOWNS["mudgate"]
    assert "testhut" in town.buildings
    entry = next(item for item in town.building_list()
                 if item.key == "testhut")
    assert (entry.title, entry.command) == ("Test Hut", "testhut")
    assert "Test Hut – A hut for testing." in town_text(town)
    assert registry.get("testhut").greeting == "Welcome to the hut."
    assert "testhut" not in TOWNS["last_light"].buildings


def test_removing_the_folder_unmounts_the_building() -> None:
    reset()
    assert "testhut" not in TOWNS["mudgate"].buildings


def test_folder_name_and_key_must_match(hut) -> None:
    hut("wronghut", MINIMAL.format(name="otherhut"))
    with pytest.raises(ValueError, match="must match"):
        discovery.mounted("mudgate_goblins")


def test_a_folder_without_building_is_refused(hut) -> None:
    hut("emptyhut", "X = 1\n")
    with pytest.raises(TypeError, match="BUILDING"):
        discovery.mounted("mudgate_goblins")


def test_every_town_folder_is_a_valid_building() -> None:
    reset()
    for folder in discovery.town_folders():
        found = discovery.mounted(folder)
        assert found
        for building in found:
            assert isinstance(building, Building)
            assert building.key == building.__module__.split(".")[-1]
            assert building.title and building.blurb
            assert building.town == folder


def test_towns_derive_their_lists_from_the_folders() -> None:
    for town in TOWNS.values():
        folders = discovery.building_folders(town.folder)
        assert set(town.buildings) == set(folders)
        assert len(town.buildings) == len(set(town.buildings))
    assert TOWNS["dusk_hollow"].buildings[0] == "station"
    assert TOWNS["dusk_hollow"].buildings[-1] == "post_office"


def test_shared_kinds_are_derived_per_town() -> None:
    red = registry.get("tavern", "dusk_hollow")
    gilded = registry.get("tavern", "last_light")
    assert red.title != gilded.title and red.renamed
    assert type(red).__mro__[1] is type(gilded)
    assert red.commands is gilded.commands


def test_command_names_are_the_same_in_all_towns() -> None:
    names = {}
    for folder in discovery.town_folders():
        for building in discovery.mounted(folder):
            names.setdefault(building.key, set()).add(
                tuple(sorted(building.commands)))
    assert all(len(variants) == 1 for variants in names.values())


def test_residents_come_from_the_building_folders() -> None:
    for town in TOWNS.values():
        keys = {person.key for person in town.residents}
        found = {key for building in town.buildings
                 for key in discovery.npc_keys(town.folder, building)}
        assert keys == found
        assert all(person.building in town.buildings
                   for person in town.residents)


def guide_examples() -> list[str]:
    lines = (Path(__file__).parent.parent / "readme" / "buildings.md"
             ).read_text(encoding="utf-8").splitlines()
    blocks, current = [], None
    for line in lines:
        if current is None and line.startswith("    from ...."):
            current = []
        if current is not None:
            if line and not line.startswith("    "):
                blocks.append("\n".join(current).rstrip() + "\n")
                current = None
            else:
                current.append(line[4:])
    return blocks


def test_the_guide_examples_work(hut) -> None:
    examples = [text for text in guide_examples() if "smokehouse" in text]
    assert len(examples) == 2
    minimal, full = examples
    hut("smokehouse", minimal)
    assert "smokehouse" in TOWNS["mudgate"].buildings
    assert registry.get("smokehouse").greeting.startswith("Welcome in")
    shutil.rmtree(TOWN_DIR / "smokehouse")
    (TOWN_DIR / "smokehouse").mkdir()
    (TOWN_DIR / "smokehouse" / "__init__.py").write_text(full,
                                                       encoding="utf-8")
    for module in [m for m in sys.modules if m.endswith("goblins.smokehouse")]:
        del sys.modules[module]
    reset()
    spec = registry.get("smokehouse")
    assert "smokehouse" in registry.commands()
    assert "smokehouse" in registry.place_of()
    panel = spec.ui(None, None)
    assert panel.buttons[0].command == "!smokehouse ham"
    assert spec.commands["smokehouse"](None, type("P", (), {"name": "x"}),
                                       [])[0].text.startswith("The smoker")

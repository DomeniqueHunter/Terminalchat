import importlib
import pkgutil
import subprocess
import sys
from pathlib import Path

import pytest

import cursed_descent


ROOT = Path(__file__).parent.parent
MODULES = [info.name for info in pkgutil.walk_packages(
    cursed_descent.__path__, prefix="cursed_descent.")]


def test_only_start_script_lives_outside_the_package() -> None:
    code = {path.name for path in ROOT.glob("*.py")}
    assert code == set()
    assert (ROOT / "start.sh").exists()


def test_modules_were_discovered() -> None:
    assert "cursed_descent.content.items" in MODULES
    assert "cursed_descent.locations.brewery.location" in MODULES


@pytest.mark.parametrize("name", MODULES)
def test_module_imports(name:str) -> None:
    importlib.import_module(name)


def test_import_has_no_item_registration_side_effect() -> None:
    code = (
        "from cursed_descent.content import ITEMS\n"
        "import cursed_descent.controller\n"
        "print(sum(key.startswith('brew_fresh_') for key in ITEMS))"
    )
    result = subprocess.run([sys.executable, "-I", "-c",
                             f"import sys; sys.path.insert(0, '.')\n{code}"],
                            cwd=ROOT, capture_output=True, text=True,
                            check=True)
    assert result.stdout.strip() == "0"


def test_no_legacy_package_name_left() -> None:
    offenders = [
        str(path.relative_to(ROOT)) for path in ROOT.rglob("*.py")
        if "cursed_decent" in path.read_text(encoding="utf-8")
        and "tests" not in path.parts
    ]
    assert offenders == []


BLOCK_DIRS = sorted(
    path for parent in ("locations", "events", "monster")
    for path in (ROOT / "cursed_descent" / parent).iterdir()
    if path.is_dir() and path.name != "__pycache__")
DATA_FILES = ("content.py", "fates.py")


def test_blocks_are_discovered() -> None:
    names = {path.name for path in BLOCK_DIRS}
    assert {"farm", "brewery", "shop", "ogre", "wanderer"} <= names


@pytest.mark.parametrize("block", BLOCK_DIRS, ids=lambda p: p.name)
def test_block_is_a_closed_package(block:Path) -> None:
    assert (block / "__init__.py").read_text(encoding="utf-8") == ""
    files = {path.name for path in block.glob("*.py")} - {"__init__.py"}
    assert files, block
    allowed = {"location.py", "event.py", "npc.py", "content.py",
               "events.py", "fates.py", "spawn.py", "items.py",
               "enchantments.py", "config.py", "ledger.py", "ui.py"}
    assert files <= allowed, files


@pytest.mark.parametrize("block", BLOCK_DIRS, ids=lambda p: p.name)
def test_block_data_modules_have_no_imports(block:Path) -> None:
    for name in DATA_FILES:
        path = block / name
        if path.exists():
            text = path.read_text(encoding="utf-8")
            assert "import " not in text, path

import json
import re
from pathlib import Path

from tests.npc_files import npc_file, npc_records

from cursed_descent.settings import (
    PROTOTYPES, REGISTRY, ensure_loaded, fill,
)


ROOT = Path(__file__).parent.parent
PACKAGE = ROOT / "cursed_descent"
TOKEN = re.compile(r"<<([a-z_]+)\.([a-z_]+)>>")


def test_every_token_in_the_code_has_a_default() -> None:
    ensure_loaded()
    for path in PACKAGE.rglob("*.py"):
        if path.name == "settings.py":
            continue
        for scope, key in TOKEN.findall(path.read_text(encoding="utf-8")):
            assert key in REGISTRY[scope], f"{path}: {scope}.{key}"


def test_defaults_keep_the_original_names() -> None:
    assert fill("<<boutique.owner>>") == "Madame Blackhide"
    assert fill("<<boutique.shop>>") == "Maison Blackhide"


def test_renaming_the_npc_json_renames_the_figure_everywhere(
        tmp_path:Path) -> None:
    from cursed_descent.content import ITEMS
    from cursed_descent.controller import GameController
    from cursed_descent.models import Message
    controller = GameController(tmp_path)
    path = npc_file(tmp_path, "Madame Vesper")
    data = json.loads(path.read_text(encoding="utf-8"))
    data.update(name="Madame Noir", first_name="Madame Noir",
                last_name="Noir")
    path.write_text(json.dumps(data), encoding="utf-8")
    renamed = GameController(tmp_path)
    assert renamed.repository.load("Madame Noir").npc == "vesper"
    assert renamed.repository.load("Madame Vesper").npc == "vesper"
    assert len([p for p, d in npc_records(tmp_path)
                if d.get("npc") == "vesper"]) == 1
    assert Message("<<boutique.owner>> / <<boutique.shop>>").text == (
        "Madame Noir / Maison Noir")
    assert ITEMS["couture_gown"]["name"] == "Noir Couture Gown"
    GameController(tmp_path / "other")
    assert Message("<<boutique.owner>>").text == "Madame Blackhide"


def test_every_npc_prototype_lives_in_a_block_config() -> None:
    from cursed_descent.npcs.seed import default_npcs
    ensure_loaded()
    keys = {npc.npc for npc in default_npcs()}
    assert keys == set(PROTOTYPES) and len(keys) > 40
    for record in PROTOTYPES.values():
        assert {"name", "age", "personality", "profile", "body", "stats",
                "gold", "inventory", "gender"} <= set(record)


def test_any_npc_can_be_renamed_in_its_json(tmp_path:Path) -> None:
    from cursed_descent.controller import GameController
    from cursed_descent.models import Message
    GameController(tmp_path)
    path = npc_file(tmp_path, "Hamhock")
    data = json.loads(path.read_text(encoding="utf-8"))
    data.update(name="Porkins", first_name="Porkins")
    path.write_text(json.dumps(data), encoding="utf-8")
    controller = GameController(tmp_path)
    assert Message("<<npc.hamhock_first>> grins").text == "Porkins grins"
    assert controller.repository.load("Hamhock").name == "Porkins"
    GameController(tmp_path / "fresh")
    assert Message("<<npc.hamhock_first>>").text == "Hamhock"

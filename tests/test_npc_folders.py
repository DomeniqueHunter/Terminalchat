import json
import random
from pathlib import Path

from cursed_descent.controller import GameController
from cursed_descent.npcs.generator import make_maid, make_mercenary
from cursed_descent.config import MAID_SEARCH_FEE, MAID_SEARCH_MAX
from cursed_descent.npcs.hire import hire_price

from tests.npc_factory import add_merc
from tests.npc_files import npc_keys


def text(messages) -> str:
    return "\n".join(message.text for message in messages)


def test_no_preset_npcs_are_created_at_start(
        data_path:Path) -> None:
    GameController(data_path)
    assert npc_keys(data_path, False) == set()
    assert npc_keys(data_path, True)


def test_generated_people_are_unique_adults_with_a_focus() -> None:
    rng = random.Random(5)
    taken: set[str] = set()
    for _ in range(25):
        maid = make_maid(rng, taken)
        taken.add(maid.name.casefold())
        assert maid.npc == "maid" and maid.age >= 18
        assert maid.profile["kind"] == "maid"
        assert maid.equipment["chest"] == "maid_uniform"
        assert len(maid.profile["focus"]) == 2
    merc = make_mercenary(rng, taken, "Male")
    assert merc.npc == "mercenary" and merc.gender == "Male"


def test_maids_and_mercs_save_into_the_npc_folder(
        controller:GameController, data_path:Path) -> None:
    rng = random.Random(1)
    maid = make_maid(rng, set())
    controller.repository.add(maid)
    add_merc(controller, "Brom")
    assert controller.repository.npc_path(maid.name).exists()
    assert controller.repository.npc_path("Brom").exists()
    assert "Brom" not in controller.repository.names()


def test_search_next_costs_a_fee_and_stops_at_five(
        controller:GameController) -> None:
    kerl = controller.repository.load("Kerl")
    kerl.gold = 1000
    first = text(controller.handle("Kerl", "!maidschool look"))
    assert "Maid 1/" in first
    before = kerl.gold
    second = text(controller.handle("Kerl", "!maidschool next"))
    assert "Maid 2/" in second and kerl.gold == before - MAID_SEARCH_FEE
    for _ in range(MAID_SEARCH_MAX):
        controller.handle("Kerl", "!maidschool next")
    assert len(controller.town.maid_search["kerl"].maids) == MAID_SEARCH_MAX
    spent = kerl.gold
    reply = text(controller.handle("Kerl", "!maidschool next"))
    assert "every maid" in reply and kerl.gold == spent
    controller.handle("Kerl", "!maidschool prev")
    assert controller.town.maid_search["kerl"].index == MAID_SEARCH_MAX - 2
    free = kerl.gold
    controller.handle("Kerl", "!maidschool next")
    assert kerl.gold == free


def test_search_next_needs_the_gold(controller:GameController) -> None:
    kerl = controller.repository.load("Kerl")
    kerl.gold = 0
    controller.handle("Kerl", "!maidschool look")
    assert "wants" in text(controller.handle("Kerl", "!maidschool next"))


def test_recruiting_creates_the_maid_file_and_she_joins_free(
        controller:GameController, data_path:Path) -> None:
    kerl = controller.repository.load("Kerl")
    kerl.gold = 1000
    controller.handle("Kerl", "!maidschool look")
    maid = controller.town.maid_search["kerl"].maids[0]
    price = hire_price(maid)
    reply = text(controller.handle("Kerl", "!maidschool recruit"))
    assert "one of your maids" in reply and kerl.gold == 1000 - price
    assert controller.repository.npc_path(maid.name).exists()
    assert controller.town.maid_search["kerl"].maids == []
    controller.handle("Kerl", "!lobby", now=0.0)
    listing = text(controller.handle("Kerl", "!hire"))
    assert "Your maids" in listing and maid.full_name in listing
    gold = kerl.gold
    assert "joins the party" in text(
        controller.handle("Kerl", f"!hire {maid.name}"))
    assert kerl.gold == gold


def test_recruiting_needs_a_candidate_and_gold(
        controller:GameController) -> None:
    assert "first" in text(controller.handle("Kerl", "!maidschool recruit"))
    controller.repository.load("Kerl").gold = 0
    controller.handle("Kerl", "!maidschool look")
    assert "costs" in text(controller.handle("Kerl", "!maidschool recruit"))


def test_story_npcs_cannot_be_hired(controller:GameController) -> None:
    controller.handle("kerl", "!lobby", now=0.0)
    reply = text(controller.handle("kerl", "!hire Astrid"))
    assert "Nobody called" in reply

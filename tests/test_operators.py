import random

from cursed_descent.settings import fill
from cursed_descent.controller import GameController
from cursed_descent.town_buildings.brothel import shift as brothel
from cursed_descent.towns import TOWNS
from cursed_descent.towns.localize import localize_text, operator_of


def texts(messages) -> str:
    return "\n".join(message.text for message in messages)


def test_every_town_has_its_own_operators() -> None:
    for building in ("tavern", "brothel", "shop", "smith", "clinic", "bank"):
        found = [operator_of(town, building) for town in TOWNS.values()]
        names = {person.first_name for person in found if person}
        assert len(names) == len([person for person in found if person])
        assert len(names) >= 4


def test_localize_swaps_last_light_operators() -> None:
    text = "Madame Rose smiles. Hilda pours at the Gilded Tankard."
    local = localize_text(text, TOWNS["cogsworth"])
    assert "Rose" not in local and "Hilda" not in local
    assert "Madame Zinnia" in local and "Mabel" in local
    assert localize_text(text, TOWNS["last_light"]) == text
    gloves = localize_text("Velvet Evening Gloves", TOWNS["mudgate"])
    assert gloves == "Velvet Evening Gloves"


def test_operator_drop_in_pays_a_bonus(monkeypatch) -> None:
    monkeypatch.setattr(brothel, "ROSE_MID_CHANCE", 1.0)
    monkeypatch.setattr(brothel, "ROSE_MID_SUB_CHANCE", 1.0)

    class Player:
        name = "kerl"
        gold = 0
        profile: dict = {}

    for mode, pool in (("", brothel.ROSE_MID_WORKING),
                       ("sub", brothel.ROSE_MID_SUB)):
        shift = brothel.Shift("brothel", None, 3, mode=mode)
        messages = brothel.operator_drop_in(Player(), shift,
                                            random.Random(1))
        assert any(line.split(" +")[0] in [fill(text) for text in pool]
                   for line in [messages[0].text])
        assert shift.earned == brothel.ROSE_MID_BONUS


def test_keepers_greet_and_offer_something(controller) -> None:
    from cursed_descent.town_buildings.greeting import greeting_for
    kerl = controller.repository.load("kerl")
    clinic = greeting_for(kerl, "clinic", random.Random(1))
    assert "Vane" in clinic and "Let me look" in clinic
    assert "job brothel" in greeting_for(kerl, "brothel")
    kerl.profile["town"] = "ironhold"
    assert "Hjalmar" in greeting_for(kerl, "clinic")
    assert greeting_for(kerl, "town") == ""

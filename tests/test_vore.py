import random

from cursed_descent.content import FATES, FATE_LABELS
from cursed_descent.house_visit import state_of
from cursed_descent.towns.last_light_humans.cafe.guests import DEADLY, Guest
from cursed_descent.towns.last_light_humans.cafe.seat import fate_for
from cursed_descent.towns.last_light_humans.cafe.vore import (
    OUTCOME_FATE, outcome_from, vore_roll,
)
from tests.test_cafe import text
from tests.test_house_visit import lady


def test_vore_fates_are_registered_with_texts() -> None:
    for fate in OUTCOME_FATE.values():
        assert FATES[fate]["any"]
        assert fate in FATE_LABELS


def test_outcome_comes_from_the_prefs_tag() -> None:
    assert outcome_from({"prefs": {"outcomes": ["vore"]}}) == "vored"
    assert outcome_from({"prefs": {"outcomes": ["anal_vore"]}}) == (
        "anal_vored")
    assert outcome_from({"prefs": {}}) == ""
    assert outcome_from({}) == ""


def test_a_vore_guest_turns_death_into_vore() -> None:
    guest = Guest("Bertha", 150, 150, outcome="vored")
    assert fate_for(None, guest, random.Random(1)) == "vored"


def test_vore_roll_is_certain_when_deadly() -> None:
    rng = random.Random(1)
    assert vore_roll("vored", rng, True) == "vored"
    assert vore_roll("", rng, True) == ""


def test_house_session_with_a_vore_host_ends_in_a_bad_end(controller) -> None:
    kerl, store = lady(controller)
    store.set("cafe", "Mrs. Fenwick", {"prefs": {
        "role": "dom", "positions": [], "flow": {},
        "outcomes": ["vore"]}})
    controller.handle("Kerl", "!visit Fenwick")
    controller.handle("Kerl", "!house sex Fenwick")
    DEADLY["on"] = True
    try:
        reply = text(controller.handle(
            "Kerl", "!house practice Fenwick oral give"))
    finally:
        DEADLY["on"] = False
    after = controller.repository.load("Kerl")
    assert "BAD END" in reply
    assert after.last_fate == "vored" and after.deaths["vored"] == 1
    assert state_of(after) is None

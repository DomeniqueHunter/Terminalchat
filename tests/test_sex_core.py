import random

from cursed_descent import home_scene
from cursed_descent.config import SEX_CONTENT_MAX, SEX_HEAT_MAX
from cursed_descent.sex_core import (
    HEAT, content_of, mercy, obedience, outcome_of, shift_content, tier_of,
)
from cursed_descent.sex_texts import BOTH, CONTENT_LINES, ORGASM
from cursed_descent.town_buildings.brothel.practices_content import (
    ACT_LABELS,
)
from tests.test_home_scene import pulse, setup_pair
from tests.test_houses import texts


def test_every_act_has_a_heat_entry_and_no_massage_or_thighjob() -> None:
    assert set(HEAT) == set(ACT_LABELS)
    assert "massage" not in ACT_LABELS and "thighjob" not in ACT_LABELS


def test_heat_table_follows_the_spec() -> None:
    assert HEAT["oral"] == (0, 1) and HEAT["anal"] == (1, 1)
    assert HEAT["facesitting"] == (1, 2) and HEAT["foot"] == (1, 2)
    assert HEAT["scat"] == (1, 1) and HEAT["watersports"] == (0, 1)
    assert HEAT["spanking"] == (1, 1) and HEAT["bdsm"] == (1, 1)


def test_text_pools_have_enough_variants() -> None:
    for tiers in CONTENT_LINES.values():
        for pool in tiers.values():
            assert len(pool) >= 3
    assert all(len(pool) >= 3 for pool in ORGASM.values())
    assert len(BOTH) >= 3


def test_contentment_stays_between_zero_and_twenty(controller) -> None:
    kerl, galactica = setup_pair(controller)
    shift_content(kerl, galactica, -5)
    assert content_of(kerl, galactica) == 0
    shift_content(kerl, galactica, 99)
    assert content_of(kerl, galactica) == SEX_CONTENT_MAX
    assert content_of(galactica, kerl) == SEX_CONTENT_MAX
    assert tier_of(0) == "cold" and tier_of(20) == "devoted"


def test_outcomes_follow_the_spec() -> None:
    wish = {"act": "oral"}
    assert outcome_of(wish, "oral", False) == "met"
    assert outcome_of(wish, "anal", False) == "ignored"
    assert outcome_of(wish, "anal", True) == "dislike_asked"
    assert outcome_of(None, "anal", False) == "free"
    assert outcome_of(None, "anal", True) == "dislike_free"


def test_a_granted_wish_gives_both_plus_two(controller) -> None:
    kerl, galactica = setup_pair(controller)
    controller.handle("galactica", "!home practice kerl oral receive")
    controller.handle("kerl", "!home practice galactica oral give")
    reply = texts(pulse(controller))
    assert "(♥ 2/20, +2)" in reply
    assert content_of(controller.repository.load("kerl"),
                      controller.repository.load("galactica")) == 2


def test_an_unasked_act_gives_plus_one_and_a_disliked_one_minus_one(
        controller) -> None:
    kerl, galactica = setup_pair(controller)
    controller.handle("kerl", "!home practice galactica oral give")
    assert "(♥ 1/20, +1)" in texts(pulse(controller))
    galactica = controller.repository.load("galactica")
    galactica.profile["prefs"] = {"role": "sub", "positions": [],
                                  "flow": {"anal": "T"}}
    controller.repository.save(galactica)
    controller.handle("kerl", "!home practice galactica spanking give")
    assert "(♥ 0/20, -1)" in texts(pulse(controller, 1, 100))


def test_a_wish_that_is_ignored_gives_nothing_and_a_disliked_one_costs_two(
        controller) -> None:
    kerl, galactica = setup_pair(controller)
    shift_content(kerl, galactica, 5)
    controller.handle("galactica", "!home practice kerl oral receive")
    controller.handle("kerl", "!home practice galactica spanking give")
    assert "±0" in texts(pulse(controller))
    galactica = controller.repository.load("galactica")
    galactica.profile["prefs"] = {"role": "sub", "positions": [],
                                  "flow": {"oral": "T"}}
    controller.repository.save(galactica)
    controller.handle("galactica", "!home practice kerl oral receive")
    controller.handle("kerl", "!home practice galactica spanking give")
    assert ", -2)" in texts(pulse(controller, 1, 100))


def test_a_full_arousal_bar_comes_and_resets(controller) -> None:
    kerl, galactica = setup_pair(controller)
    out = ""
    for step in range(SEX_HEAT_MAX):
        controller.handle("kerl", "!home practice galactica spanking give")
        out += texts(pulse(controller, 1, 100 * step))
        if "💦" in out:
            break
    assert "💦" in out
    info = home_scene.scene_info(controller.repository.load("kerl"),
                                 controller.repository)
    assert info["heat"] < SEX_HEAT_MAX


def test_contentment_raises_obedience_and_mercy(controller) -> None:
    kerl, galactica = setup_pair(controller)
    low = (obedience(kerl, galactica), mercy(kerl, galactica))
    shift_content(kerl, galactica, 20)
    high = (obedience(kerl, galactica), mercy(kerl, galactica))
    assert high[0] > low[0] and high[1] > low[1]
    assert high[0] == 1.0


def test_titfuck_give_is_active_with_a_cock_receive_is_passive_breasts(
        ) -> None:
    from cursed_descent.town_buildings.brothel.practices import can_do
    body = {"bust": 600}
    assert can_do("Shemale", "titfuck", "give", body)
    assert can_do("Shemale", "titfuck", "receive", body)
    assert can_do("Male", "titfuck", "give", body)
    assert not can_do("Male", "titfuck", "receive", body)
    assert can_do("Female", "titfuck", "receive", body)
    assert not can_do("Female", "titfuck", "give", body)


def test_orgasm_names_where_the_load_goes(controller) -> None:
    from cursed_descent.sex_core import destination_kind, destination_text
    kerl, galactica = setup_pair(controller)
    assert destination_kind("anal", True, "in") == "pen_in"
    assert destination_kind("anal", True, "on") == "pen_on"
    assert destination_kind("oral", False, "on") == "face"
    rng = random.Random(1)
    text = destination_text("anal", kerl, galactica, True, "in", rng)
    assert "Galactica" in text or "inside" in text
    scene = {"heat": {kerl.id: 9, galactica.id: 0}}
    from cursed_descent.sex_core import add_heat
    lines = "\n".join(add_heat(scene, "anal", "give", kerl, galactica, rng))
    assert "💦" in lines and "goes" in lines


def test_facesitting_goes_on_after_the_bottom_was_allowed_to_breathe(
        controller) -> None:
    kerl, galactica = setup_pair(controller)
    controller.handle("kerl", "!home practice galactica facesitting give")
    pulse(controller)
    controller.handle("kerl", "!home act raise")
    pulse(controller, 1, 100)
    info = home_scene.scene_info(controller.repository.load("kerl"),
                                 controller.repository)
    assert info["overlay"]["act"] == "facesitting" and info["air"]
    assert {"clench", "shift"} <= set(info["overlay"]["actions"])
    controller.handle("kerl", "!home act clench")
    assert "squeezes" in texts(pulse(controller, 1, 200))


def test_titfuck_heats_up_the_giver_too() -> None:
    from cursed_descent.sex_core import HEAT
    assert HEAT["titfuck"] == (2, 1)

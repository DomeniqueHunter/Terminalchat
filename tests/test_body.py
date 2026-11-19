import pytest

from cursed_descent.body import (
    BUST_CC, apply_body_mods, default_body, body_effect, body_text,
    bust_cm, bust_label, bust_tier, growth_effect, muscle_baseline,
    muscle_tier, normalize_body,
)
from cursed_descent.body_creation import body_question, parse_body_input
from cursed_descent.models import Player


def legacy(build:str="Average", breasts:str="Medium") -> dict:
    return {"height": 170, "weight": 65, "build": build, "breasts": breasts}


@pytest.mark.parametrize("tier,cc", list(BUST_CC.items()))
def test_bust_tiers_roundtrip(tier:str, cc:int) -> None:
    assert bust_tier(cc) == tier
    assert normalize_body(legacy(breasts=tier))["bust"] == cc


def test_normalize_fills_numeric_defaults_from_legacy_tiers() -> None:
    body = normalize_body(legacy("Muscular", "Large"))
    assert body["bust"] == 500 and body["muscle"] == 70
    assert body["breasts"] == "Large" and body["breasts_real"] == "Large"
    assert body["fake"] == {}


def test_normalize_is_idempotent() -> None:
    once = normalize_body(legacy("Curvy", "Huge"))
    assert normalize_body(dict(once)) == once


def test_implants_do_not_count_for_the_real_tier() -> None:
    body = normalize_body({**legacy(breasts="Small"), "bust": 900,
                           "fake": {"bust": 800}})
    assert body["breasts"] == "Huge" and body["breasts_real"] == "Flat"


def test_fake_amount_cannot_exceed_the_part() -> None:
    body = normalize_body({**legacy(), "bust": 100, "fake": {"bust": 500}})
    assert body["fake"] == {"bust": 100}


def test_defaults_have_no_growth_effects() -> None:
    for build in ("Thin", "Average", "Muscular", "Curvy", "Heavy"):
        body = normalize_body(legacy(build, "Massive"))
        for key in ("hp", "melee", "dodge", "discount", "allure"):
            assert growth_effect(body, key) == 0


def test_growth_beyond_the_old_limits_still_matters() -> None:
    base = normalize_body(legacy())
    huge = normalize_body({**base, "bust": 4800})
    assert body_effect(huge, "allure") > body_effect(base, "allure")
    assert body_effect(huge, "dodge") < body_effect(base, "dodge")
    tall = {**base, "height": 800}
    assert body_effect(tall, "hp") > body_effect(base, "hp")


def test_growth_has_diminishing_returns() -> None:
    base = normalize_body(legacy())
    gains = [body_effect({**base, "muscle": value}, "melee")
             for value in (25, 125, 225, 325, 425)]
    steps = [b - a for a, b in zip(gains, gains[1:])]
    assert steps == sorted(steps, reverse=True) and gains[-1] < 0.12


def test_bust_label_extends_beyond_massive() -> None:
    assert bust_label(1200) == "Massive"
    assert bust_label(2000) == "Colossal"
    assert bust_label(10000) == "Planetary"


def test_bust_circumference_keeps_growing() -> None:
    sizes = [bust_cm(normalize_body({**legacy(), "bust": cc}))
             for cc in (300, 1200, 2400, 4800)]
    assert sizes == sorted(sizes) and len(set(sizes)) == 4


def test_extra_muscle_raises_the_muscle_tier() -> None:
    stats = {"strength": 12}
    plain = normalize_body(legacy())
    strong = {**plain, "muscle": 100}
    assert muscle_tier(stats, strong) != muscle_tier(stats, plain)
    assert muscle_tier(stats, "Average") == muscle_tier(stats, plain)


def test_body_text_shows_numbers() -> None:
    text = body_text(normalize_body(legacy(breasts="Large")))
    assert "500 cc" in text and "butt 95 cm" in text


def test_default_body_is_normalized() -> None:
    body = default_body()
    assert body["bust"] == BUST_CC[body["breasts"]]
    assert body["muscle"] == muscle_baseline(body["build"])


def test_mods_override_the_body_and_convert_legacy_tiers() -> None:
    body = default_body()
    apply_body_mods(body, {"breasts": "Massive"})
    assert body["bust"] == 1200 and body["breasts"] == "Massive"
    mods = {"bust": 2000, "fake": {"bust": 500}}
    apply_body_mods(body, mods)
    assert body["bust"] == 2000 and body["breasts_real"] == "Massive"


def test_player_body_is_always_normalized() -> None:
    player = Player(name="Fresh")
    assert {"bust", "muscle", "butt", "girth", "balls", "fake"} <= set(
        player.body)


def test_legacy_player_data_keeps_its_bust_tier() -> None:
    data = Player(name="Old").to_dict()
    data["body"] = {"height": 300, "weight": 200, "build": "Muscular",
                    "breasts": "Massive"}
    player = Player.from_dict(data)
    assert player.body["bust"] == 1200 and player.body["muscle"] == 70


def test_creation_input_changes_the_body() -> None:
    body = normalize_body(legacy())
    result = parse_body_input("height 185 bust 600 fake 200 muscle 40 "
                              "butt 105 build toned", body, "Female")
    assert not isinstance(result, str)
    assert result["height"] == 185 and result["bust"] == 600
    assert result["fake"] == {"bust": 200}
    assert result["breasts_real"] == "Medium"


def test_creation_build_resets_baselines_unless_overridden() -> None:
    body = normalize_body(legacy())
    result = parse_body_input("build muscular", body, "Male")
    assert result["muscle"] == 70
    result = parse_body_input("build muscular muscle 20", body, "Male")
    assert result["muscle"] == 20


@pytest.mark.parametrize("text", [
    "height", "height abc", "height 20", "build nonsense", "weird 5",
    "bust 100 fake 200", "shape cat",
])
def test_creation_rejects_bad_input(text:str) -> None:
    assert isinstance(parse_body_input(text, normalize_body(legacy()),
                                       "Male"), str)


def test_creation_blocks_parts_the_character_lacks() -> None:
    result = parse_body_input("cock 20", normalize_body(legacy()), "Female")
    assert isinstance(result, str) and "doesn't apply" in result


def test_creation_sets_cock_values_and_scales_girth() -> None:
    body = normalize_body(legacy())
    result = parse_body_input("cock 25 shape equine", body, "Male")
    assert result["endowment"] == 25 and result["girth"] == 20
    assert result["endowment_shape"] == "Equine"


def test_body_question_lists_cock_keys_only_when_hung() -> None:
    body = normalize_body(legacy())
    assert "cock" in body_question(body, "Male")
    assert "cock" not in body_question(body, "Female")

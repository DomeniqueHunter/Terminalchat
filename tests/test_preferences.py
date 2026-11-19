import random
from unittest.mock import MagicMock

from cursed_descent.controller import GameController
from cursed_descent.preferences import (
    brothel_mode, pick_likes, prefs_of, scene_defaults,
)


def texts(messages) -> str:
    return "\n".join(message.text for message in messages)


def test_prefs_default_to_switch_and_toggle(
        controller:GameController) -> None:
    kerl = controller.repository.load("kerl")
    assert prefs_of(kerl)["role"] == "switch"
    controller.handle("kerl", "!prefs role dom")
    controller.handle("kerl", "!prefs position rider")
    controller.handle("kerl", "!prefs practice facesitting")
    kerl = controller.repository.load("kerl")
    prefs = prefs_of(kerl)
    assert prefs["role"] == "dom" and prefs["positions"] == ["rider"]
    assert prefs["practices"] == ["facesitting"]
    controller.handle("kerl", "!prefs position rider")
    assert prefs_of(controller.repository.load("kerl"))["positions"] == []
    assert "cleared" in texts(controller.handle("kerl", "!prefs clear"))
    assert prefs_of(controller.repository.load("kerl"))["role"] == "switch"


def test_unknown_prefs_show_the_overview(
        controller:GameController) -> None:
    assert "Your preferences" in texts(controller.handle(
        "kerl", "!prefs position nonsense"))


def test_prefs_steer_scene_defaults_and_brothel_mode(
        controller:GameController) -> None:
    kerl = controller.repository.load("kerl")
    assert scene_defaults(kerl)["role"] == "top"
    assert brothel_mode(kerl, "") == ""
    controller.handle("kerl", "!prefs role sub")
    controller.handle("kerl", "!prefs position spoon")
    kerl = controller.repository.load("kerl")
    options = scene_defaults(kerl)
    assert options["role"] == "bottom" and options["position"] == "spoon"
    assert brothel_mode(kerl, "") == "sub"
    assert brothel_mode(kerl, "domina") == "domina"


def test_preferred_practices_narrow_the_client_wishes(
        controller:GameController) -> None:
    controller.handle("kerl", "!prefs practice oral")
    kerl = controller.repository.load("kerl")
    pool = [("oral", "give"), ("anal", "give"), ("oral", "receive"),
            ("vaginal", "give")]
    for seed in range(20):
        likes = pick_likes(kerl, pool, random.Random(seed))
        assert all(act == "oral" for act, _ in likes)


def test_foot_smothering_has_aliases_and_a_full_label(
        controller:GameController) -> None:
    for word in ("footsmothering", "foot", "foot_smothering"):
        controller.handle("kerl", "!prefs clear")
        reply = texts(controller.handle("kerl", f"!prefs practice {word}"))
        assert "foot smothering" in reply
        assert prefs_of(controller.repository.load("kerl"))[
            "practices"] == ["foot"]


def test_practice_flow_cycles_and_narrows_likes(controller) -> None:
    from cursed_descent.preferences import pick_likes, prefs_of
    import random
    kerl = controller.repository.load("kerl")
    for expected in ("G", "T", "GT", ""):
        controller.handle("kerl", "!prefs practice oral")
        kerl = controller.repository.load("kerl")
        assert prefs_of(kerl)["flow"].get("oral", "") == expected
    controller.handle("kerl", "!prefs practice oral t")
    kerl = controller.repository.load("kerl")
    assert prefs_of(kerl)["flow"] == {"oral": "T"}
    pool = [("oral", "give"), ("oral", "receive"), ("anal", "give")]
    likes = pick_likes(kerl, pool, random.Random(1))
    assert likes == (("oral", "receive"),)

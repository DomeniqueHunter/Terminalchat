from cursed_descent.endowment import (
    endowment_geometry, preview_caption, preview_scale,
)


BODY = {"endowment": 20, "girth": 12, "balls": 6, "height": 180,
        "endowment_shape": "Equine"}


def test_no_geometry_for_genders_without_a_cock() -> None:
    assert endowment_geometry(BODY, "Female", 1.0) is None
    assert endowment_geometry(BODY, "None", 1.0) is None


def test_geometry_scales_with_the_body() -> None:
    small = endowment_geometry(BODY, "Male", 1.0, hang=1.0)
    large = endowment_geometry(BODY, "Male", 2.0, hang=1.0)
    assert large["length"] == 2 * small["length"]
    assert small["length"] == 20
    assert round(small["diameter"], 1) == 3.8
    assert small["shape"] == "Equine"


def test_hanging_length_is_limited_by_the_figure() -> None:
    huge = dict(BODY, endowment=400)
    geo = endowment_geometry(huge, "Male", 1.0, limit=100)
    assert geo["length"] == 40


def test_caption_and_scale() -> None:
    assert "20 cm long" in preview_caption(BODY, "Male")
    assert "No endowment" in preview_caption(BODY, "Female")
    assert 0.5 <= preview_scale(BODY, 150, 220) <= 9.0
    assert preview_scale(dict(BODY, endowment=1, girth=1, balls=1),
                         150, 220) == 9.0

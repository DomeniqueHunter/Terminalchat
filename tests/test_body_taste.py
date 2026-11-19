from cursed_descent.models import Player
from cursed_descent.town_buildings.body_taste import (
    HINTS, taste_factor, taste_hints, taste_of, tally,
)


def lady(**body) -> Player:
    player = Player(name="Dame", id="d", gender="Female", age=30)
    player.body.update({"breasts": "Large", "bust": 800, "butt": 140,
                        "endowment": 0, "fake": {}})
    player.body.update(body)
    return player


def test_taste_is_stable_per_client() -> None:
    assert taste_of("Gerald") == taste_of("Gerald")
    assert any(value != ("any", "any")
               for value in taste_of("Gerald").values())


def test_hints_are_subtle_and_never_state_the_preference() -> None:
    for name in ("Gerald", "Hugo", "Fenwick", "Lorenz", "Otto"):
        for line in taste_hints(lady(), name):
            assert "prefer" not in line.lower() and "{" not in line


def test_matching_taste_pays_more_and_missing_pays_less() -> None:
    found = {}
    for name in ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J"):
        found[name] = taste_factor(lady(), name)
    assert max(found.values()) > 1.0
    assert min(found.values()) < 1.0 or all(v >= 1 for v in found.values())
    assert min(found.values()) >= 0.7


def test_fake_and_real_are_told_apart() -> None:
    from cursed_descent.town_buildings.body_taste import player_traits
    real = player_traits(lady())
    fake = player_traits(lady(fake={"bust": 500}))
    assert real["bust"][1] == "real" and fake["bust"][1] == "fake"
    assert "bust" not in player_traits(lady(breasts="None"))
    assert HINTS and tally(lady(), "A")[0] is not None

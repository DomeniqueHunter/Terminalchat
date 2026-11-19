from cursed_descent.config import STAT_NAMES
from cursed_descent.locations.boutique.location import (
    build_garment, hunted_bonus, snapshot,
)
from cursed_descent.models import Player


def victim(source:str) -> dict:
    data = snapshot(Player(name="Hero", gender="Female"))
    data["source"] = source
    return data


def test_hunted_garments_get_four_to_nine_on_every_bonus() -> None:
    plain = build_garment(victim("sold"), "bra")
    hunted = build_garment(victim("hunted"), "bra")
    boost = hunted_bonus("Hero", "bra")
    assert 4 <= boost <= 9
    assert hunted["name"].endswith("★")
    assert set(hunted["bonus"]) == set(plain["bonus"]) <= set(STAT_NAMES)
    for stat, value in plain["bonus"].items():
        assert hunted["bonus"][stat] == value + boost


def test_hunted_bonus_is_stable_across_rebuilds() -> None:
    first = build_garment(victim("hunted"), "bra")
    again = build_garment(victim("hunted"), "bra")
    assert first["bonus"] == again["bonus"]
    rolls = {hunted_bonus(f"Victim{i}", "bra") for i in range(200)}
    assert rolls == set(range(4, 10))

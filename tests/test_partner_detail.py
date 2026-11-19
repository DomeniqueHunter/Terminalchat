import random

from cursed_descent.models import Player
from cursed_descent.partner_detail import cock_tier, partner_line


def make(name:str, gender:str, height:int, **body) -> Player:
    player = Player(name=name, id=f"id-{name}", gender=gender, age=30)
    player.body.update(height=height, **body)
    return player


def test_partner_line_mentions_gender_height_and_equipment() -> None:
    me = make("Me", "Female", 160)
    other = make("Titan", "Shemale", 200, endowment=40, weight=120)
    line = partner_line("anal", "receive", me, other, random.Random(1))
    assert "shemale" in line
    assert "40 cm" in line
    assert "40 cm taller" in line or "taller" in line


def test_partner_line_adapts_to_a_shorter_flat_partner() -> None:
    me = make("Me", "Female", 190)
    other = make("Pip", "Female", 150, bust=0)
    line = partner_line("vaginal", "give", me, other, random.Random(2))
    assert "female" in line and "shorter" in line


def test_cock_tiers_rise_with_size() -> None:
    assert [cock_tier(cm) for cm in (8, 15, 25, 50)] == [
        "modest", "solid", "heavy", "huge"]

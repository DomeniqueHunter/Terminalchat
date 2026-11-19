
from cursed_descent.config import CONDITION_STEPS
from cursed_descent.models import Player
from cursed_descent.orientation import fits, likes_of, reaction, traits_of


def person(name:str, gender:str, npc:str="") -> Player:
    return Player(name=name, id=f"id-{name}", first_name=name,
                  gender=gender, npc=npc)


def test_futas_carry_both_traits() -> None:
    assert traits_of("Herm") == {"penis", "vagina"}
    assert traits_of("Male") == {"penis"}
    assert traits_of("Female") == {"vagina"}


def test_players_default_to_both_and_npcs_are_stable() -> None:
    assert likes_of(person("P", "Male")) == "both"
    host = person("Anna", "Female", "anna")
    assert likes_of(host) == likes_of(person("Anna", "Female", "anna"))


def test_herm_guest_fits_every_orientation() -> None:
    herm = person("H", "Herm")
    for likes in ("penis", "vagina", "both"):
        host = person("N", "Male", "n")
        host.profile["orientation"] = likes
        assert fits(host, herm)


def test_a_mismatch_warms_up_after_a_few_sessions() -> None:
    host = person("Gay", "Male", "gay")
    host.profile["orientation"] = "penis"
    guest = person("She", "Female")
    deltas = []
    for _ in range(CONDITION_STEPS + 1):
        lines, delta = reaction(host, guest, False)
        deltas.append(delta)
    assert deltas == [-1, -1, -1, 0]
    assert "come around" in lines[0]


def test_a_dominant_host_reeducates_the_player() -> None:
    host = person("Dom", "Female", "dom")
    host.profile["orientation"] = "both"
    guest = person("Gay", "Male")
    guest.profile["orientation"] = "penis"
    for _ in range(CONDITION_STEPS):
        lines, _ = reaction(host, guest, True)
    assert guest.profile["orientation"] == "both"
    assert "taught you" in lines[-1]

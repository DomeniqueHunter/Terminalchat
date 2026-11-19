import random

from cursed_descent.controller import GameController
from cursed_descent.models import Player
from cursed_descent.towns.last_light_humans.cafe.guests import (
    Guest, hung_drain, hung_pay_factor, is_hung, pity_of, smell_drain,
)
from cursed_descent.town_buildings.family import link
from tests.test_cafe import setup_pair, text
from tests.test_houses import befriend, rich, texts


def test_heavy_futa_mother_gets_extra_dialogue(
        controller:GameController) -> None:
    setup_pair(controller)
    kerl = controller.repository.load("Kerl")
    mother = controller.repository.load("Galactica")
    mother.gender = "Shemale"
    mother.body["weight"] = 165
    mother.body["butt"] = 164
    link(mother, kerl, "son")
    controller.repository.save(kerl)
    controller.repository.save(mother)
    controller.handle("Kerl", "!job cafe seat")
    sit = text(controller.handle("Galactica", "!sit Kerl"))
    assert "Mommy" in sit
    look = text(controller.handle("Kerl", "!examine lady"))
    assert "Your own mother is sitting" in look or "Mom is a mountain" in look
    rise = text(controller.handle("Galactica", "!rise"))
    assert "sweetheart" in rise


def test_slim_or_unrelated_riders_get_no_kin_text(
        controller:GameController) -> None:
    setup_pair(controller)
    controller.handle("Kerl", "!job cafe seat")
    assert "Mommy" not in text(controller.handle("Galactica", "!sit Kerl"))


def test_young_ladies_pity_more_than_old_ones() -> None:
    young = Guest("A", 100, 120, age=22)
    middle = Guest("B", 100, 120, age=45)
    old = Guest("C", 100, 120, age=70)
    assert pity_of(young) > pity_of(middle) > pity_of(old) == 0


def test_hung_guests_drain_air_and_pay_more() -> None:
    plain = Guest("A", 100, 120, gender="Female")
    hung = Guest("B", 100, 120, gender="Shemale", endowment=40)
    short = Guest("C", 100, 120, gender="Shemale", endowment=10)
    assert is_hung(hung) and not is_hung(plain) and not is_hung(short)
    assert hung_drain(hung) > 0 == hung_drain(plain)
    assert smell_drain(hung) > smell_drain(plain)
    assert hung_pay_factor(hung) > 1 == hung_pay_factor(plain)


def test_home_seat_can_kill_the_host(controller:GameController,
                                     monkeypatch) -> None:
    rich(controller)
    controller.handle("kerl", "!home buy hut")
    befriend(controller, "hilda", 30)
    controller.handle("kerl", "!home invite hilda")
    monkeypatch.setattr("cursed_descent.house_modes.home_sittings",
                        lambda *args, **kwargs: (["It is over."], 0,
                                                 "smothered"))
    reply = texts(controller.handle("kerl", "!home romance hilda seat"))
    assert "💀" in reply
    assert controller.repository.load("kerl").deaths.get("smothered") == 1


def test_mother_swallows_her_son_with_extra_text(
        controller:GameController) -> None:
    setup_pair(controller)
    kerl = controller.repository.load("Kerl")
    mother = controller.repository.load("Galactica")
    mother.gender = "Shemale"
    mother.body["weight"] = 300
    mother.body["butt"] = 300
    link(mother, kerl, "son")
    controller.repository.save(kerl)
    controller.repository.save(mother)
    controller.handle("Kerl", "!job cafe seat")
    controller.handle("Galactica", "!sit Kerl")
    reply = text(controller.handle("Galactica", "!swallow"))
    assert "Mom" in reply
    assert "You rock your hips and let" not in reply


def test_swallowing_makes_the_lady_fatter_for_good_and_bellied_for_a_night(
        controller:GameController) -> None:
    from cursed_descent.towns.last_light_humans.cafe.swallow import clear_belly
    setup_pair(controller)
    lady = controller.repository.load("Galactica")
    lady.body["weight"] = 250
    lady.body["butt"] = 250
    controller.repository.save(lady)
    controller.handle("Kerl", "!job cafe seat")
    controller.handle("Galactica", "!sit Kerl")
    reply = text(controller.handle("Galactica", "!swallow"))
    assert "swallowed company" in reply
    lady = controller.repository.load("Galactica")
    assert lady.body["weight"] == 252 and lady.body["butt"] == 251
    assert lady.profile["swallow_belly"] > 0
    assert lady.profile["swallows"] == 1
    assert "overnight" in clear_belly(lady)
    assert "swallow_belly" not in lady.profile


def test_growth_is_capped_like_bertha(controller:GameController) -> None:
    from cursed_descent.config import CAFE_BERTHA_MAX
    from cursed_descent.towns.last_light_humans.cafe.swallow import grow_player
    player = Player(name="Big", id="big", gender="Female", age=40)
    player.body["weight"] = CAFE_BERTHA_MAX[0]
    player.body["butt"] = CAFE_BERTHA_MAX[1]
    grow_player(player, "Someone")
    assert player.body["weight"] == CAFE_BERTHA_MAX[0]
    assert player.body["butt"] == CAFE_BERTHA_MAX[1]


def test_a_mother_answers_licks_and_kisses_of_her_child() -> None:
    import random
    from cursed_descent.towns.last_light_humans.cafe.guests import Guest
    from cursed_descent.towns.last_light_humans.cafe.kin_seat import (
        KISS, LICK, kin_text,
    )
    guest = Guest("Lady Volena", 140, 200)
    guest.kin = "son"
    rng = random.Random(1)
    text = kin_text(KISS, guest, "Nick", rng)
    assert "{" not in text and ("son" in text or "Mommy" in text)
    assert len(LICK) >= 6 and len(KISS) >= 5

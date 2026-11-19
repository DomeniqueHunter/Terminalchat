import random

from cursed_descent.towns.last_light_humans.cafe.home_seat import (
    HOME_SEAT_SITS, WARNING, guest_of, home_sittings,
)
from cursed_descent.models import Player


def record(**values) -> dict:
    base = {"name": "Mrs. Fenwick", "weight": 120, "butt": 160, "cruel": 2,
            "age": 45, "height": 170, "kills": 0}
    base.update(values)
    return base


def seat() -> Player:
    player = Player(name="Seat", gender="Male")
    player.stats["vitality"] = 1
    player.stats["strength"] = 1
    return player


def test_the_warning_names_the_missing_safeword() -> None:
    text = WARNING.format(place="her home", name="Mrs. Fenwick",
                          sits=HOME_SEAT_SITS, chosen="normal, long",
                          command="visit")
    assert "no safeword" in text and "confirm" in text


def test_guest_comes_from_the_regular_record() -> None:
    guest = guest_of(record())
    assert guest.weight == 120 and guest.cruel == 2


def test_a_weak_seat_can_die_at_her_home(monkeypatch) -> None:
    rng = random.Random(1)
    monkeypatch.setattr(rng, "random", lambda: 0.0)
    lines, earned, fate = home_sittings(seat(), record(weight=200,
                                                       butt=200), rng)
    assert fate in ("smothered", "engulfed")
    assert any("cannot move" in line for line in lines)


def test_a_strong_seat_survives_every_sitting(monkeypatch) -> None:
    player = seat()
    player.stats["vitality"] = 60
    player.stats["strength"] = 60
    player.level = 40
    rng = random.Random(2)
    lines, earned, fate = home_sittings(player, record(), rng)
    assert fate == "" and earned == 0
    assert sum(1 for line in lines if "settles for the next" in line) == (
        HOME_SEAT_SITS - 1)


def test_there_is_no_way_to_stop_the_scene() -> None:
    rng = random.Random(3)
    player = seat()
    player.stats["vitality"] = 60
    lines, _, _ = home_sittings(player, record(), rng)
    assert not any("safeword" in line.casefold() and "[" in line
                   for line in lines)


def test_options_parse_in_any_order_and_leave_the_name() -> None:
    from cursed_descent.towns.last_light_humans.cafe.training import parse_options
    options, rest = parse_options(["Mrs.", "hard", "Fenwick", "short",
                                   "confirm"])
    assert (options.intensity, options.length) == ("hard", "short")
    assert rest == ["Mrs.", "Fenwick", "confirm"]
    assert options.sits == 1 and options.points() == 3


def test_training_cut_is_capped_and_never_makes_a_seat_invulnerable() -> None:
    from cursed_descent.config import TRAIN_CUT_MAX, TRAIN_MAX
    from cursed_descent.towns.last_light_humans.cafe.guests import crush_chance
    from cursed_descent.towns.last_light_humans.cafe.training import (
        add_training, train_cut, training_of)
    player = seat()
    for _ in range(20):
        add_training(player, "Mrs. Fenwick", 3)
    assert training_of(player, "Mrs. Fenwick") == TRAIN_MAX
    assert train_cut(TRAIN_MAX) == TRAIN_CUT_MAX < 1
    assert crush_chance(200, 200, 3) * (1 - TRAIN_CUT_MAX) > 0


def test_gentle_training_is_safer_than_hard_over_many_visits() -> None:
    from cursed_descent.towns.last_light_humans.cafe.training import VisitOptions
    deaths = {}
    for intensity in ("gentle", "hard"):
        count = 0
        for seed in range(200):
            _, _, fate = home_sittings(
                seat(), record(weight=180, butt=180), random.Random(seed),
                None, VisitOptions(intensity=intensity))
            count += bool(fate)
        deaths[intensity] = count
    assert deaths["gentle"] <= deaths["hard"]


def test_private_visits_never_move_money(controller) -> None:
    from tests.test_cafe import setup_pair
    setup_pair(controller)
    kerl = controller.repository.load("Kerl")
    store = controller.town.regulars_of(kerl)
    store.add("cafe", {"name": "Mrs. Fenwick", "age": 50, "weight": 90,
                       "butt": 110, "cruel": 0, "address_known": True,
                       "home": "No. 5 Elm Terrace"})
    store.set("cafe", "Mrs. Fenwick", {"address_known": True})
    kerl.stats["vitality"] = 40
    kerl.stats["strength"] = 40
    controller.repository.save(kerl)
    gold = kerl.gold
    controller.town.rng.random = lambda: 0.5
    controller.handle("Kerl", "!visit Fenwick")
    warning = controller.handle("Kerl", "!house seat gentle short")
    assert "gentle, short" in warning[0].text
    reply = controller.handle("Kerl", "!house seat gentle short confirm")
    assert controller.town.shifts["kerl"].mode == "home"
    for _ in range(12):
        if "kerl" not in controller.town.shifts:
            break
        reply += controller.handle("Kerl", "!hold")
    after = controller.repository.load("Kerl")
    assert after.gold == gold
    assert "Seat training with Mrs. Fenwick" in " ".join(
        message.text for message in reply)
    assert "gold" not in " ".join(m.text for m in reply
                                  if "+0" in m.text)
    assert after.profile["seat_training"]["mrs. fenwick"] == 1


def test_invite_needs_a_cafe_regular_and_can_be_declined(controller) -> None:
    from tests.test_cafe import setup_pair
    setup_pair(controller)
    kerl = controller.repository.load("Kerl")
    store = controller.town.regulars_of(kerl)
    store.add("cafe", {"name": "Mrs. Fenwick", "age": 50})
    nobody = controller.handle("Kerl", "!invite Nobody")
    assert "Invite whom" in nobody[0].text
    warning = controller.handle("Kerl", "!invite Fenwick")
    assert "your own home" in warning[0].text
    store.set("cafe", "Mrs. Fenwick", {"happiness": 0})
    controller.town.rng.random = lambda: 0.99
    declined = controller.handle("Kerl", "!invite Fenwick confirm")
    assert "declines" in declined[0].text


def test_an_accepted_invite_trains_at_the_seats_own_home(controller) -> None:
    from tests.test_cafe import setup_pair
    setup_pair(controller)
    kerl = controller.repository.load("Kerl")
    kerl.stats["vitality"] = 40
    kerl.stats["strength"] = 40
    controller.repository.save(kerl)
    store = controller.town.regulars_of(kerl)
    store.add("cafe", {"name": "Mrs. Fenwick", "age": 50, "weight": 90,
                       "butt": 110, "cruel": 0})
    store.set("cafe", "Mrs. Fenwick", {"happiness": 10})
    controller.town.rng.random = lambda: 0.0
    reply = controller.handle("Kerl", "!invite Fenwick gentle short confirm")
    for _ in range(12):
        if "kerl" not in controller.town.shifts:
            break
        reply += controller.handle("Kerl", "!hold")
    text = " ".join(message.text for message in reply)
    assert "your door" in text or "your place" in text
    assert "Seat training with Mrs. Fenwick: 1/" in text

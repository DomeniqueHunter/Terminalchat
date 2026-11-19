from cursed_descent.towns.last_light_humans.cafe.service import ambient
from cursed_descent.house_visit import (
    dynamic_of, pick_for, present, state_of,
)
from tests.test_cafe import setup_pair, text


def lady(controller, **extra):
    setup_pair(controller)
    kerl = controller.repository.load("Kerl")
    store = controller.town.regulars_of(kerl)
    store.add("cafe", {"name": "Mrs. Fenwick", "age": 50, "gender": "Female",
                       "weight": 90, "butt": 110, "cruel": 0,
                       "address_known": True, "home": "No. 5 Elm Terrace",
                       **extra})
    store.set("cafe", "Mrs. Fenwick", {"address_known": True})
    controller.town.rng.random = lambda: 0.5
    return kerl, store


def test_visit_goes_to_the_house_and_leave_ends_it(controller) -> None:
    lady(controller)
    reply = text(controller.handle("Kerl", "!visit Fenwick"))
    assert "No. 5 Elm Terrace" in reply
    kerl = controller.repository.load("Kerl")
    state = state_of(kerl)
    assert state["host"] == "Mrs. Fenwick"
    assert [e["kind"] for e in state["present"]] == ["owner"]
    assert "already visiting" in text(controller.handle(
        "Kerl", "!visit Fenwick"))
    assert "walk back" in text(controller.handle("Kerl", "!house leave"))
    assert state_of(controller.repository.load("Kerl")) is None


def test_nobody_may_be_home(controller) -> None:
    lady(controller)
    controller.town.rng.random = lambda: 0.99
    reply = text(controller.handle("Kerl", "!visit Fenwick"))
    assert "Nobody answers" in reply or "out" in reply
    kerl = controller.repository.load("Kerl")
    assert state_of(kerl)["present"] == []


def test_house_actions_feed_and_rest(controller) -> None:
    kerl, _ = lady(controller)
    kerl.needs["hunger"] = 80
    kerl.needs["sleep"] = 80
    kerl.sweat = 30
    controller.repository.save(kerl)
    controller.handle("Kerl", "!visit Fenwick")
    controller.handle("Kerl", "!house eat")
    controller.handle("Kerl", "!house sleep")
    controller.handle("Kerl", "!house bathe")
    after = controller.repository.load("Kerl")
    assert after.needs["hunger"] < 80 and after.needs["sleep"] < 80
    assert after.sweat == 0


def test_look_and_talk_work_at_the_house(controller) -> None:
    lady(controller)
    controller.handle("Kerl", "!visit Fenwick")
    look = text(controller.handle("Kerl", "!house look"))
    assert "Present: Mrs. Fenwick" in look and "Elm Terrace" in look
    assert "Mrs. Fenwick" in text(controller.handle(
        "Kerl", "!house talk Fenwick"))
    assert "Nobody called" in text(controller.handle(
        "Kerl", "!house talk Nobody"))


def test_sex_opens_and_back_closes_the_sex_state(controller) -> None:
    lady(controller)
    controller.handle("Kerl", "!visit Fenwick")
    controller.handle("Kerl", "!house sex Fenwick")
    state = state_of(controller.repository.load("Kerl"))
    assert state["sex_with"] == "Mrs. Fenwick"
    controller.handle("Kerl", "!house back")
    assert state_of(controller.repository.load("Kerl"))["sex_with"] == ""


def test_house_commands_need_a_visit(controller) -> None:
    setup_pair(controller)
    assert "not at anybody's house" in text(
        controller.handle("Kerl", "!house eat"))


def test_other_players_show_up_in_the_house(controller) -> None:
    kerl, _ = lady(controller)
    controller.handle("Kerl", "!visit Fenwick")
    other = controller.repository.load("Kerl")
    names = [e["name"] for e in present(other, controller.repository,
                                        state_of(other))]
    assert names == ["Mrs. Fenwick"]


def test_dom_sub_dynamic_decides_who_chooses(controller) -> None:
    kerl, _ = lady(controller)
    controller.handle("Kerl", "!visit Fenwick")
    kerl = controller.repository.load("Kerl")
    state = state_of(kerl)
    from cursed_descent.house_regulars import regular_player
    host = regular_player("cafe", {"name": "Mrs. Fenwick", "age": 50})
    assert dynamic_of(kerl, host, state) == ""
    kerl.profile["prefs"] = {"role": "sub", "flow": {}}
    assert dynamic_of(kerl, host, state) == "npc"
    host.profile["prefs"] = {"role": "sub", "flow": {}}
    kerl.profile["prefs"] = {"role": "dom", "flow": {}}
    assert dynamic_of(kerl, host, state) == "player"
    assert pick_for(kerl, host, controller.town.rng, False) is not None


def test_npc_dom_overrides_the_choice(controller) -> None:
    kerl, _ = lady(controller)
    kerl.profile["prefs"] = {"role": "sub", "flow": {}}
    controller.repository.save(kerl)
    controller.handle("Kerl", "!visit Fenwick")
    controller.handle("Kerl", "!house sex Fenwick")
    reply = text(controller.handle(
        "Kerl", "!house practice Fenwick oral give"))
    assert "decides" in reply


def test_npc_dom_demands_a_title_from_a_sub_player(controller) -> None:
    kerl, _ = lady(controller)
    kerl.profile["prefs"] = {"role": "sub", "flow": {}}
    controller.repository.save(kerl)
    reply = text(controller.handle("Kerl", "!visit Fenwick"))
    after = controller.repository.load("Kerl")
    title = next(iter(after.profile["i_call"].values()))
    assert title in ("mistress", "herrin", "goddess", "madam", "mommy",
                     "queen")
    assert title.capitalize() in reply
    controller.handle("Kerl", "!house sex Fenwick")
    answer = text(controller.handle(
        "Kerl", "!house practice Fenwick oral give"))
    assert title.capitalize() in answer


def test_dom_player_can_order_a_title_from_a_sub_npc(controller) -> None:
    kerl, store = lady(controller)
    kerl.profile["prefs"] = {"role": "dom", "flow": {}}
    controller.repository.save(kerl)
    store.set("cafe", "Mrs. Fenwick", {"prefs": {
        "role": "sub", "positions": [], "flow": {}}})
    controller.handle("Kerl", "!visit Fenwick")
    reply = text(controller.handle(
        "Kerl", "!house order Fenwick goddess"))
    assert "Goddess" in reply
    after = controller.repository.load("Kerl")
    assert list(after.profile["calls_me"].values()) == ["Goddess"]


def test_order_needs_a_dominant_player(controller) -> None:
    lady(controller)
    controller.handle("Kerl", "!visit Fenwick")
    assert "Only a dominant player" in text(controller.handle(
        "Kerl", "!house order Fenwick queen"))


def test_no_cafe_ambient_text_while_visiting_a_house(controller) -> None:
    lady(controller)
    town = controller.town
    town.ambient_on = True
    town.cafe_seen["Kerl"] = town.now
    controller.handle("Kerl", "!visit Fenwick")
    town.cafe_seen["Kerl"] = town.now
    town.ambient_due["Kerl"] = 0
    assert ambient(town, town.now + 1) == []


def test_a_pinned_visitor_leaves_only_when_the_host_decides(
        controller) -> None:
    kerl, store = lady(controller)
    kerl.profile["prefs"] = {"role": "sub", "flow": {}}
    controller.repository.save(kerl)
    store.set("cafe", "Mrs. Fenwick", {"prefs": {
        "role": "dom", "positions": [], "flow": {"facesitting": "G"}}})
    controller.handle("Kerl", "!visit Fenwick")
    controller.handle("Kerl", "!house sex Fenwick")
    controller.handle("Kerl", "!house practice Fenwick facesitting give")
    state = state_of(controller.repository.load("Kerl"))
    assert state["held_by"]
    controller.town.rng.random = lambda: 0.99
    import cursed_descent.house_visit as module
    module_random = module.random
    try:
        blocked = text(controller.handle("Kerl", "!house leave"))
        assert "decide" in blocked or "Not yet" in blocked
        assert state_of(controller.repository.load("Kerl")) is not None
    finally:
        module.random = module_random


def test_pin_releases_after_enough_attempts(controller) -> None:
    from cursed_descent.house_visit import pinned
    kerl, _ = lady(controller)
    controller.handle("Kerl", "!visit Fenwick")
    kerl = controller.repository.load("Kerl")
    state = state_of(kerl)
    state["held_by"] = "Fenwick"

    class Always:
        def random(self) -> float:
            return 0.0

    reply = pinned(kerl, state, controller.repository, Always())
    assert "lifts" in reply[0].text and state["held_by"] == ""


def test_the_host_releases_a_pinned_visitor_by_time(controller) -> None:
    import time
    kerl, store = lady(controller)
    kerl.profile["prefs"] = {"role": "sub", "flow": {}}
    controller.repository.save(kerl)
    store.set("cafe", "Mrs. Fenwick", {"prefs": {
        "role": "dom", "positions": [], "flow": {"facesitting": "G"}}})
    controller.handle("Kerl", "!visit Fenwick")
    controller.handle("Kerl", "!house sex Fenwick")
    controller.handle("Kerl", "!house practice Fenwick facesitting give")
    town = controller.town
    until = state_of(controller.repository.load("Kerl"))["held_until"]
    assert until > time.time()
    assert "pinned" in controller.handle("Kerl", "!join")[0].text
    assert "enjoy it" in controller.handle("Kerl", "!shop")[0].text
    start = time.time()
    town.tick_pins(town.now, start)
    pulse = town.tick_pins(town.now + 3, start + 11)
    assert len(pulse) == 1 and "lifts" not in pulse[0].text
    reply = town.tick_pins(town.now + 6, until + 1)
    assert "lifts" in reply[0].text
    assert not state_of(controller.repository.load("Kerl"))["held_by"]


def test_a_pin_from_an_older_save_still_gets_a_release_time(
        controller) -> None:
    import time
    kerl, _ = lady(controller)
    controller.handle("Kerl", "!visit Fenwick")
    kerl = controller.repository.load("Kerl")
    state_of(kerl)["held_by"] = "Fenwick"
    controller.repository.save(kerl)
    town = controller.town
    town.tick_pins(town.now, time.time())
    assert "held_until" in state_of(controller.repository.load("Kerl"))


def test_rider_can_raise_for_a_moment_and_stay_seated(controller) -> None:
    setup_pair(controller)
    controller.handle("Kerl", "!job cafe seat")
    controller.handle("Galactica", "!sit Kerl")
    shift = controller.town.shifts["kerl"]
    shift.air = 40
    shift.client.squeeze = 2
    reply = text(controller.handle("Galactica", "!raise"))
    assert "hand's breadth" in reply
    assert shift.air == 75 and shift.client.squeeze == 1
    assert shift.client.rider == "Galactica"
    assert "catching breath" in text(controller.handle(
        "Galactica", "!raise"))
    controller.handle("Galactica", "!rise")
    assert "not sitting" in text(controller.handle("Galactica", "!raise"))


def test_look_at_a_person_describes_body_clothes_and_doing(
        controller) -> None:
    lady(controller)
    controller.handle("Kerl", "!visit Fenwick")
    reply = text(controller.handle("Kerl", "!house look Fenwick"))
    assert "👁 Mrs. Fenwick" in reply
    assert "wears" in reply and "Right now" in reply
    assert "years" in reply and "cm" in reply
    assert "Nobody called" in text(controller.handle(
        "Kerl", "!house look Nobody"))

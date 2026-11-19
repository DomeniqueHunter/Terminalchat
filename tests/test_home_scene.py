import random
import time

from cursed_descent import home_scene
from cursed_descent.config import HOUSE_AIR_DRAIN, HOUSE_SCENE_PULSE
from cursed_descent.controller import GameController
from cursed_descent.sex_core import shift_content
from tests.test_houses import agree, rich, texts


def setup_pair(controller:GameController, dom:str="kerl",
               sub:str="galactica") -> tuple:
    rich(controller)
    controller.handle("kerl", "!home buy row")
    controller.handle("kerl", "!home invite galactica")
    controller.handle("galactica", "!home accept")
    for name, role in ((dom, "dom"), (sub, "sub")):
        hero = controller.repository.load(name)
        hero.profile["prefs"] = {"role": role, "positions": [], "flow": {}}
        controller.repository.save(hero)
    controller.repository.load("galactica").gender
    for name in ("kerl", "galactica"):
        hero = controller.repository.load(name)
        hero.gender = "Female"
        controller.repository.save(hero)
    agree(controller, "galactica", "kerl")
    agree(controller, "kerl", "galactica")
    controller.handle("kerl", "!home sex galactica")
    return (controller.repository.load("kerl"),
            controller.repository.load("galactica"))


def pulse(controller:GameController, count:int=1, start:float=0.0
          ) -> list:
    messages = []
    wall = time.time() + 1000 + start
    for step in range(count):
        wall += HOUSE_SCENE_PULSE + 1
        messages += home_scene.tick_scenes(controller.repository,
                                           random.Random(2), wall)
    return messages


def test_a_sub_choice_is_only_a_wish_the_dom_decides(
        controller:GameController) -> None:
    setup_pair(controller)
    reply = texts(controller.handle(
        "galactica", "!home practice kerl watersports receive"))
    assert "Only" in reply and "decides" in reply
    assert "★" in reply
    assert "watersports" not in texts(pulse(controller)).lower()


def test_the_dom_choice_is_registered_at_the_next_pulse(
        controller:GameController) -> None:
    setup_pair(controller)
    reply = texts(controller.handle(
        "kerl", "!home practice galactica spanking give"))
    assert "registered in" in reply
    assert controller.town.timer_text(
        controller.repository.load("kerl")).startswith("Next interaction")
    assert "💞" in texts(pulse(controller))


def test_smothering_drains_air_and_ends_with_a_knock_out(
        controller:GameController) -> None:
    setup_pair(controller)
    controller.handle("kerl", "!home practice galactica facesitting give")
    steps = 100 // HOUSE_AIR_DRAIN + 2
    first = texts(pulse(controller))
    assert "Air" in first
    later = texts(pulse(controller, steps, 100))
    assert "out cold" in later
    galactica = controller.repository.load("galactica")
    assert galactica.alive
    assert galactica.profile["ko_until"] > time.time()
    assert not galactica.profile.get("home_sex")
    reply = texts(controller.handle("kerl", "!home practice galactica "
                                            "spanking give"))
    assert "out cold" in reply


def test_the_dom_can_lift_and_the_sub_can_plead(
        controller:GameController) -> None:
    setup_pair(controller)
    controller.handle("kerl", "!home practice galactica foot give")
    pulse(controller)
    assert "Tap out" in texts(controller.handle("galactica",
                                                "!home breathe"))
    assert "Lift foot" in texts(controller.handle("kerl", "!home lift"))
    out = texts(pulse(controller, 1, 100))
    assert "Air" in out
    assert "permits" not in out


def test_the_sub_has_to_answer_a_demanded_title(
        controller:GameController) -> None:
    setup_pair(controller)
    reply = texts(controller.handle("kerl",
                                    "!home order galactica mistress"))
    assert "Mistress" in reply and "!home answer" in reply
    answer = texts(controller.handle("galactica", "!home answer"))
    assert "Mistress" in answer
    assert "silent" not in texts(pulse(controller))


def test_a_silent_sub_is_noticed_at_the_next_pulse(
        controller:GameController) -> None:
    setup_pair(controller)
    controller.handle("kerl", "!home order galactica mistress")
    assert "silent" in texts(pulse(controller))


def test_an_autopilot_dom_acts_like_an_npc(
        controller:GameController) -> None:
    setup_pair(controller)
    controller.session.autopilot.add("kerl")
    controller.handle("galactica", "!home practice kerl spanking receive")
    assert "💞" in texts(pulse(controller, 2))


def test_an_autopilot_sub_answers_at_once(
        controller:GameController) -> None:
    kerl, galactica = setup_pair(controller)
    shift_content(kerl, galactica, 20)
    controller.session.autopilot.add("Galactica")
    reply = texts(controller.handle("kerl",
                                    "!home order galactica mistress"))
    assert "!home answer" not in reply
    assert reply.count("Mistress") >= 3


def test_the_sub_cannot_end_the_scene_but_the_dom_can(
        controller:GameController) -> None:
    setup_pair(controller)
    reply = texts(controller.handle("galactica", "!home back"))
    assert "decides when this is over" in reply
    assert controller.repository.load("galactica").profile["home_sex"]
    controller.handle("kerl", "!home back")
    assert not controller.repository.load("galactica").profile.get(
        "home_sex")


def test_an_autopilot_dom_ends_the_scene_after_a_while(
        controller:GameController, monkeypatch) -> None:
    monkeypatch.setattr(home_scene, "HOUSE_AUTO_BEATS", 1)
    monkeypatch.setattr(home_scene, "HOUSE_AUTO_END", 1.0)
    setup_pair(controller)
    controller.session.autopilot.add("kerl")
    text = texts(pulse(controller, 3))
    assert "ends it" in text
    assert not controller.repository.load("galactica").profile.get(
        "home_sex")


def test_a_demanded_title_replaces_the_mom_lines(
        controller:GameController) -> None:
    from cursed_descent.town_buildings.family import relations
    setup_pair(controller)
    kerl = controller.repository.load("kerl")
    galactica = controller.repository.load("galactica")
    relations(kerl)[galactica.id] = {"role": "son", "name": galactica.name}
    relations(galactica)[kerl.id] = {"role": "mother", "name": kerl.name}
    controller.repository.save(kerl)
    controller.repository.save(galactica)
    controller.handle("kerl", "!home order galactica mistress")
    controller.handle("galactica", "!home answer")
    controller.handle("kerl", "!home practice galactica spanking give")
    text = texts(pulse(controller))
    assert "Mom" not in text


def test_overlay_actions_are_limited_to_the_side_and_registered(
        controller:GameController) -> None:
    kerl, galactica = setup_pair(controller)
    controller.handle("kerl", "!home practice galactica facesitting give")
    pulse(controller)
    info = home_scene.scene_info(controller.repository.load("galactica"),
                                 controller.repository)
    assert info["overlay"]["side"] == "receiver"
    assert "breath" in info["overlay"]["actions"]
    assert "lean" not in info["overlay"]["actions"]
    reply = texts(controller.handle("galactica", "!home act lean"))
    assert "not possible" in reply
    reply = texts(controller.handle("galactica", "!home act breath"))
    assert "registered in" in reply
    out = texts(pulse(controller, 1, 100))
    assert "Air" in out


def test_a_granted_plea_gives_contentment(controller) -> None:
    from cursed_descent.sex_core import content_of
    kerl, galactica = setup_pair(controller)
    controller.handle("kerl", "!home practice galactica facesitting give")
    pulse(controller)
    controller.handle("galactica", "!home act tap")
    pulse(controller, 1, 100)
    controller.handle("kerl", "!home act raise")
    pulse(controller, 1, 200)
    assert content_of(controller.repository.load("kerl"),
                      controller.repository.load("galactica")) >= 2


def test_penetration_and_ballbusting_have_their_own_actions(
        controller) -> None:
    kerl, galactica = setup_pair(controller)
    for name in ("kerl", "galactica"):
        hero = controller.repository.load(name)
        hero.gender = "Shemale" if name == "kerl" else "Male"
        controller.repository.save(hero)
    controller.handle("kerl", "!home practice galactica anal give")
    pulse(controller)
    info = home_scene.scene_info(controller.repository.load("kerl"),
                                 controller.repository)
    assert set(info["overlay"]["actions"]) == {"thrust", "spank", "stop"}
    info = home_scene.scene_info(controller.repository.load("galactica"),
                                 controller.repository)
    assert set(info["overlay"]["actions"]) == {"moan", "more", "mercy"}
    controller.handle("kerl", "!home act stop")
    pulse(controller, 1, 100)
    assert home_scene.scene_info(
        controller.repository.load("kerl"),
        controller.repository)["overlay"] == {}
    controller.handle("kerl", "!home practice galactica ballbusting give")
    pulse(controller, 1, 200)
    info = home_scene.scene_info(controller.repository.load("kerl"),
                                 controller.repository)
    assert "kick" in info["overlay"]["actions"]


def test_every_overlay_action_has_a_text_with_enough_variants() -> None:
    from cursed_descent import sex_overlays
    from cursed_descent.sex_overlay_texts import LINES
    for kind, sides in sex_overlays.SIDES.items():
        acts = [act for act, owner in sex_overlays.KIND_OF.items()
                if owner == kind]
        for side in sides.values():
            for action in side:
                for act in acts:
                    key = next(candidate for candidate in (
                        (act, action), (kind, action), ("any", action))
                        if candidate in LINES)
                    assert len(LINES[key]) >= 3, key


def test_every_act_has_an_overlay_with_buttons_and_keeps_going(
        controller) -> None:
    from cursed_descent import sex_overlays
    from cursed_descent.town_buildings.brothel.practices_content import (
        ACT_LABELS,
    )
    assert set(ACT_LABELS) <= set(sex_overlays.KIND_OF)
    for kind, owner in sex_overlays.DEFAULT_GIVER.items():
        assert owner in sex_overlays.SIDES[kind]["giver"]
    assert set(sex_overlays.DEFAULT_GIVER) == set(sex_overlays.SIDES)


def test_every_overlay_action_has_a_button_label_and_an_effect() -> None:
    from cursed_descent import sex_overlays
    for sides in sex_overlays.SIDES.values():
        for side in sides.values():
            for action in side:
                assert action in sex_overlays.LABELS, action
                assert action in sex_overlays.FX, action


def test_an_unanswered_act_continues_with_its_default_beat(
        controller) -> None:
    setup_pair(controller)
    controller.handle("kerl", "!home practice galactica oral give")
    pulse(controller)
    scene_info = home_scene.scene_info(controller.repository.load("kerl"),
                                       controller.repository)
    assert scene_info["overlay"]["kind"] == "service"
    assert "deeper" in scene_info["overlay"]["actions"]
    out = texts(pulse(controller, 1, 20))
    assert out
    still = home_scene.scene_info(controller.repository.load("kerl"),
                                  controller.repository)
    assert still["overlay"]["kind"] == "service"


def test_clenching_at_home_can_crush_into_a_long_knock_out(
        controller) -> None:
    import random
    from cursed_descent import sex_overlays
    setup_pair(controller)
    kerl = controller.repository.load("kerl")
    galactica = controller.repository.load("galactica")
    kerl.body.update(butt=260, weight=180)
    scene = {"overlay": {"kind": "smother", "act": "facesitting",
                         "giver": kerl.id, "receiver": galactica.id,
                         "plea": "", "where": "in"},
             "air": 100, "smothered": galactica.id, "acts": {
                 kerl.id: "clench"}, "heat": {}}
    class Lucky(random.Random):
        def random(self) -> float:
            return 0.0

    lines, out = sex_overlays.resolve(scene, kerl, galactica, Lucky(1))
    assert out and scene.get("crushed") == galactica.id
    assert any("whimper" in line or "clamps down" in line
               or "creaks" in line for line in lines)


def test_a_small_lady_does_not_crush_and_the_victim_whimpers_first() -> None:
    from cursed_descent.towns.last_light_humans.cafe.guests import (
        crush_chance, crush_tier,
    )
    assert crush_chance(100, 60, 3, 0, 30) == 0.0
    assert crush_tier(0.0) == 0
    assert crush_tier(0.05) == 1 and crush_tier(0.15) == 2
    assert crush_tier(0.3) == 3


def test_an_autopilot_dom_can_smother_a_sub_into_a_knock_out(
        controller) -> None:
    kerl, galactica = setup_pair(controller)
    controller.session.autopilot.add("kerl")
    controller.handle("galactica", "!home practice kerl facesitting receive")
    text = texts(pulse(controller, 12))
    assert "Air" in text


def sole_scene(controller, acts:dict[str, str], sweat:int=0) -> tuple:
    setup_pair(controller)
    kerl = controller.repository.load("kerl")
    galactica = controller.repository.load("galactica")
    scene = {"overlay": {"kind": "sole", "act": "foot", "giver": kerl.id,
                         "receiver": galactica.id, "plea": "",
                         "where": "in"},
             "air": 100, "smothered": galactica.id, "heat": {},
             "sweat": sweat, "acts": {kerl.id: acts.get("giver"),
                                      galactica.id: acts.get("receiver")}}
    scene["acts"] = {key: value for key, value in scene["acts"].items()
                     if value}
    return scene, kerl, galactica


def test_foot_smothering_has_its_own_options_without_clench(
        controller) -> None:
    from cursed_descent import sex_overlays
    sides = sex_overlays.SIDES["sole"]
    assert "clench" not in sides["giver"] and "order" in sides["giver"]
    assert {"rub", "pinch", "toes", "lift"} <= set(sides["giver"])
    assert {"worship", "suck"} <= set(sides["receiver"])


def test_rubbing_raises_the_foot_sweat_and_the_smell_steps_up(
        controller) -> None:
    from cursed_descent import sex_overlays
    scene, kerl, galactica = sole_scene(controller, {"giver": "rub"}, 20)
    lines, _ = sex_overlays.resolve(scene, kerl, galactica,
                                    random.Random(1))
    assert scene["sweat"] == 30
    assert any("stronger" in line for line in lines)


def test_an_obeyed_lick_order_tastes_worse_with_more_sweat(
        controller) -> None:
    from cursed_descent import sex_overlays
    scene, kerl, galactica = sole_scene(controller, {"giver": "order"}, 80)
    sex_overlays.resolve(scene, kerl, galactica, random.Random(1))
    assert scene["order"] is True
    scene["acts"] = {galactica.id: "worship"}
    air = scene["air"]
    lines, _ = sex_overlays.resolve(scene, kerl, galactica,
                                    random.Random(1))
    assert not scene.get("order")
    assert any("retch" in line or "gag" in line or "choke" in line
               for line in lines)
    assert scene["air"] < air - 15


def test_a_refused_lick_order_costs_contentment(controller) -> None:
    from cursed_descent import sex_overlays
    from cursed_descent.sex_core import content_of
    scene, kerl, galactica = sole_scene(controller, {"giver": "order"})
    sex_overlays.resolve(scene, kerl, galactica, random.Random(1))
    before = content_of(kerl, galactica)
    scene["acts"] = {galactica.id: "struggle"}
    lines, _ = sex_overlays.resolve(scene, kerl, galactica,
                                    random.Random(1))
    assert content_of(kerl, galactica) <= before
    assert any("lick" in line.lower() or "obey" in line for line in lines)


def test_a_foot_drains_less_air_than_a_facesitter(controller) -> None:
    from cursed_descent import sex_overlays
    scene, kerl, galactica = sole_scene(controller, {})
    sex_overlays.resolve(scene, kerl, galactica, random.Random(1))
    sole_loss = 100 - scene["air"]
    assert 0 < sole_loss < sex_overlays.air_drain(
        kerl.body.get("weight", 80))


def test_a_started_foot_scene_shows_the_sweat_value(controller) -> None:
    setup_pair(controller)
    controller.handle("kerl", "!home practice galactica foot give")
    pulse(controller)
    info = home_scene.scene_info(controller.repository.load("kerl"),
                                 controller.repository)
    assert info["overlay"]["kind"] == "sole"
    assert info["overlay"]["sweat"] is not None
    assert info["air"] is not None


def test_the_ordered_lick_has_a_lick_button_for_the_receiver(
        controller) -> None:
    from cursed_descent import sex_overlays
    assert sex_overlays.LABELS["worship"] == "Lick sole"
    scene, kerl, galactica = sole_scene(controller, {"giver": "order"})
    sex_overlays.resolve(scene, kerl, galactica, random.Random(1))
    info = home_scene.overlay_info(scene, galactica)
    assert info["order"] is True
    assert "worship" in info["actions"] and "suck" in info["actions"]


def test_an_npc_partner_gets_a_continuous_scene_with_buttons_and_heat(
        controller) -> None:
    from tests.test_houses import befriend, rich
    rich(controller)
    controller.handle("kerl", "!home buy row")
    befriend(controller, "hilda", 30)
    controller.handle("kerl", "!home invite hilda")
    kerl = controller.repository.load("kerl")
    kerl.gender = "Male"
    controller.repository.save(kerl)
    reply = texts(controller.handle(
        "kerl", "!home practice hilda anal give"))
    assert "registered" in reply or "wish" in reply
    out = texts(pulse(controller, 4))
    info = home_scene.scene_info(controller.repository.load("kerl"),
                                 controller.repository)
    assert out and info is not None
    assert info["overlay"] and info["overlay"]["actions"]
    assert info["mate_heat"] > 0 or info["heat"] > 0

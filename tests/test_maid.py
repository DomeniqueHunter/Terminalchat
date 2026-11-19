import random

import pytest

from cursed_descent.combat import fate_text
from cursed_descent.content import BUFFS, FATES
from cursed_descent.controller import GameController
from cursed_descent.events.maid.event import FATE_KEYS, first_hit_death
from cursed_descent.spawns import load_rules
from tests.test_enter_buildings import texts

from tests.ready import confirm


def start_pair(controller:GameController) -> None:
    lady = controller.repository.load("galactica")
    lady.gender = "Female"
    controller.repository.save(lady)
    controller.handle("kerl", "!lobby", now=0.0)
    controller.handle("galactica", "!join", now=0.5)
    controller.handle("kerl", "!start", now=1.0)
    confirm(controller, 1.0)
    controller.session.stage = 8


def offer(controller:GameController) -> None:
    controller.session.events.trigger("buster_maid", 2.0)


def test_maid_is_an_event_with_a_spawn_rule() -> None:
    rule = next(rule for rule in load_rules()
                if rule.kind == "buster_maid")
    assert rule.slot == "event" and rule.once_per_run


def test_maid_is_offered_only_once_per_run(
        controller:GameController) -> None:
    start_pair(controller)
    events = controller.session.events
    rule = next(rule for rule in load_rules() if rule.kind == "buster_maid")
    kinds = []
    for _ in range(60):
        kind, _ = events.pick_kind(8)
        kinds.append(kind)
        events.once_seen -= {rule2.kind for rule2 in load_rules()
                             if rule2.kind != "buster_maid"}
    assert kinds.count("buster_maid") <= 1


def test_options_need_a_lady_and_a_free_slot(
        controller:GameController) -> None:
    start_pair(controller)
    offer(controller)
    events = controller.session.events
    assert events.available() == ["history", "volunteer", "examine", "depart"]
    events.maid_free = lambda: False
    assert events.available() == ["history", "examine", "depart"]


def test_a_man_cannot_volunteer(controller:GameController) -> None:
    start_pair(controller)
    offer(controller)
    reply = texts(controller.handle("kerl", "!volunteer", now=3.0))
    assert "needs a lady" in reply or "reference needs a lady" in reply
    assert controller.session.member("kerl").alive


def test_surviving_all_hundred_hits_recruits_connie(
        controller:GameController, monkeypatch:pytest.MonkeyPatch) -> None:
    start_pair(controller)
    offer(controller)
    monkeypatch.setattr(random, "random", lambda: 0.99)
    reply = texts(controller.handle("galactica", "!volunteer", now=3.0))
    assert "[smack]" in reply
    assert controller.session.events.available() == ["examine", "smack"]
    assert "Only" in texts(controller.handle("kerl", "!smack", now=3.1))
    for index in range(10):
        reply = texts(controller.handle("galactica", "!smack",
                                        now=4.0 + index))
        if index < 9:
            assert "💬" in reply and f"{(index + 1) * 10} of 100" in reply
    assert "Hits 91-100" in reply and "Connie" in reply
    lady = controller.session.member("galactica")
    assert lady.alive and "red_cheeks" in " ".join(lady.buffs)
    connie = controller.session.member("Connie")
    assert connie is not None and connie.npc == "mercenary"
    assert controller.repository.exists("Connie")
    assert controller.session.events.event == {} or (
        controller.session.events.event.get("kind") != "buster_maid")


def test_a_deadly_hit_kills_with_one_of_six_fates(
        controller:GameController, monkeypatch:pytest.MonkeyPatch) -> None:
    start_pair(controller)
    offer(controller)
    monkeypatch.setattr(random, "random", lambda: 0.0)
    texts(controller.handle("galactica", "!volunteer", now=3.0))
    reply = texts(controller.handle("galactica", "!smack", now=4.0))
    assert "Hit 1" in reply
    assert not controller.session.member("galactica").alive
    entry = controller.session.remains.entries[-1]
    assert entry["fate"] in FATE_KEYS
    assert controller.session.member("Connie") is None


def test_a_taken_maid_does_not_come_back(
        controller:GameController, monkeypatch:pytest.MonkeyPatch) -> None:
    start_pair(controller)
    offer(controller)
    monkeypatch.setattr(random, "random", lambda: 0.99)
    controller.handle("galactica", "!volunteer", now=3.0)
    for index in range(10):
        controller.handle("galactica", "!smack", now=4.0 + index)
    events = controller.session.events
    assert events.maid_taken()


def test_one_percent_per_hit_is_mostly_deadly() -> None:
    rng = random.Random(5)
    deaths = sum(1 for _ in range(400) if first_hit_death(rng, 100))
    assert 0.55 < deaths / 400 < 0.72


@pytest.mark.parametrize("fate", FATE_KEYS)
def test_every_death_has_text_and_no_open_braces(fate:str) -> None:
    assert fate in FATES
    from cursed_descent.models import Player
    text = fate_text(Player(name="Probe", gender="Female"), fate, None)
    assert "Probe" in text or "{" not in text
    assert "{" not in text


def test_red_cheeks_buff_exists() -> None:
    assert "red_cheeks" in BUFFS


def test_trigger_starts_grill_and_maid(controller:GameController) -> None:
    start_pair(controller)
    events = controller.session.events
    assert events.trigger("grill", 2.0) is not None
    assert events.event.get("kind") == "grill"
    events.reset()
    assert events.trigger("buster_maid", 3.0) is not None
    assert events.event.get("kind") == "buster_maid"


def test_debug_trigger_shows_the_maid_even_when_connie_exists(
        controller:GameController, monkeypatch:pytest.MonkeyPatch) -> None:
    start_pair(controller)
    offer(controller)
    monkeypatch.setattr(random, "random", lambda: 0.99)
    controller.handle("galactica", "!volunteer", now=3.0)
    for index in range(10):
        controller.handle("galactica", "!smack", now=4.0 + index)
    assert controller.session.events.maid_taken()
    lines = controller.session.events.trigger("buster_maid", 20.0)
    assert any("paddle" in line for line in lines)
    assert controller.session.events.event["kind"] == "buster_maid"


def test_connie_leaves_the_roster_when_the_run_ends(
        controller:GameController, monkeypatch:pytest.MonkeyPatch) -> None:
    start_pair(controller)
    offer(controller)
    monkeypatch.setattr(random, "random", lambda: 0.99)
    controller.handle("galactica", "!volunteer", now=3.0)
    for index in range(10):
        controller.handle("galactica", "!smack", now=4.0 + index)
    assert controller.repository.exists("Connie")
    reply = "\n".join(controller.session.end_run())
    assert "Our paths part" in reply or "honour" in reply or "waltz" in reply
    assert not controller.repository.exists("Connie")
    assert not controller.session.events.maid_taken()


def test_connie_flatters_the_ladies_of_the_party(
        controller:GameController) -> None:
    start_pair(controller)
    reply = "\n".join(controller.session.events.trigger("buster_maid", 2.0))
    assert "Galactica" in reply and "ma'am" in reply


def test_connie_leaves_when_every_lady_is_smashed(
        controller:GameController, monkeypatch:pytest.MonkeyPatch) -> None:
    start_pair(controller)
    offer(controller)
    monkeypatch.setattr(random, "random", lambda: 0.0)
    controller.handle("galactica", "!volunteer", now=3.0)
    reply = texts(controller.handle("galactica", "!smack", now=4.0))
    assert any(word in reply for word in ("Too frail", "elsewhere",
                                              "not a household"))
    assert controller.session.events.event.get("kind") != "buster_maid"


def test_butt_buster_is_legendary_and_connie_is_dressed_classy() -> None:
    from cursed_descent.config import BUTT_BUSTER_DAMAGE
    from cursed_descent.content import ITEMS, RARITY_LABELS
    from cursed_descent.settings import PROTOTYPES, ensure_loaded
    ensure_loaded()
    buster = ITEMS["constance_butt_buster"]
    assert buster["rarity"] == "legendary" and "legendary" in RARITY_LABELS
    assert buster["damage"] == BUTT_BUSTER_DAMAGE == 3000
    worn = PROTOTYPES["constance"]["equipment"]
    assert all(worn[slot] for slot in ("weapon", "head", "chest", "gloves",
                                       "feet", "accessory", "lingerie"))
    assert "rubber" not in " ".join(item["id"] for item in worn.values()
                                    if item)


def test_connie_texts_have_variations() -> None:
    from cursed_descent.events.maid.content import (
        EVENT_TEXTS, NICKNAMES, ROUND_TEXTS, FLATTERY)
    texts_ = EVENT_TEXTS["buster_maid"]
    assert len(texts_["meet"]) >= 4 and len(texts_["died_after"]) >= 6
    assert len(NICKNAMES) == 16
    assert all(len(round_) >= 3 for round_ in ROUND_TEXTS)
    assert all(len(lines) >= 3 for lines in FLATTERY.values())
    assert all("{nick}" in meet for meet in texts_["meet"])


def test_maid_has_examine_and_can_be_talked_to(
        controller:GameController) -> None:
    start_pair(controller)
    offer(controller)
    options = controller.session.events.available()
    assert "examine" in options and "volunteer" in options
    reply = texts(controller.handle("galactica", "!examine", now=3.0))
    assert "Butt Buster" in reply and "Hell Boots" in reply
    talk = texts(controller.handle("galactica", "!talk Constance",
                                   now=3.5))
    assert "Constance" in talk


def test_connie_is_tough(controller:GameController) -> None:
    from cursed_descent.events.maid.event import make_companion
    from cursed_descent.formulas import max_hp
    connie = make_companion(20)
    assert connie.stats["vitality"] >= 20 * 4
    assert connie.hp == max_hp(connie) and max_hp(connie) > 1000


def test_no_fate_names_a_swing_number_or_flies() -> None:
    import re
    from cursed_descent.events.maid.fates import FATES
    for pool in FATES.values():
        for text in pool["any"]:
            assert not re.search(r"\d+(st|nd|rd|th) swing", text)
            assert "ball" not in text and "sky" not in text


def test_eighteen_deaths_all_have_text_label_and_remains() -> None:
    from cursed_descent.content import FATE_LABELS, FATES, REMAINS_TEXTS
    assert len(FATE_KEYS) == 18
    for fate in FATE_KEYS:
        assert FATES[fate]["any"] and FATE_LABELS[fate] and (
            "{dead}" in REMAINS_TEXTS[fate])
        assert "stuck to" not in FATE_LABELS[fate]


def test_old_paddle_fates_from_saved_remains_still_render() -> None:
    from cursed_descent.content import FATE_LABELS, FATES, REMAINS_TEXTS
    for old in ("paddle_splattered", "paddle_pancaked", "paddle_launched",
                "paddle_folded", "paddle_bounced", "paddle_flatpacked"):
        assert old in FATES and old in FATE_LABELS and old in REMAINS_TEXTS


def test_death_texts_never_name_a_body_part_that_is_not_hit() -> None:
    import re
    from cursed_descent.events.maid.fates import FATES, REMAINS_TEXTS
    forbidden = re.compile(r"belly|chest|(?<!her )head|skull|stomach|neck|face|throat",
                           re.IGNORECASE)
    for fate in FATE_KEYS:
        for text in FATES[fate]["any"] + [REMAINS_TEXTS[fate]]:
            assert not forbidden.search(text), (fate, text)


def test_cast_in_combat_reaches_the_fight(
        controller:GameController) -> None:
    start_pair(controller)
    reply = texts(controller.handle("galactica", "!cast fireball 1",
                                    now=3.0))
    assert "Nobody here wants anything" not in reply


def test_a_companion_without_an_action_never_stalls_the_round(
        controller:GameController) -> None:
    from cursed_descent.events.maid.event import make_companion
    start_pair(controller)
    session = controller.session
    connie = make_companion(1)
    session.repository.add(connie)
    session.party.append(connie)
    session.member("kerl").alive = False
    reply = texts(controller.handle("galactica", "!hit", now=3.0))
    assert "Resolving round" in reply


def test_companions_do_not_block_entering_the_city(
        controller:GameController) -> None:
    from cursed_descent.events.maid.event import make_companion
    from cursed_descent.town_buildings.station.rail_pass import (
        grant_pass, has_pass,
    )
    start_pair(controller)
    session = controller.session
    connie = make_companion(1)
    session.repository.add(connie)
    session.party.append(connie)
    session.events.trigger("citystop", 2.0)
    key = session.events.event["data"]["town"]
    for member in session.party:
        if not member.npc:
            grant_pass(member, key)
    assert "enter" in session.events.available()
    controller.handle("kerl", "!enter", now=3.0)
    assert has_pass(session.member("Connie"), key)


def test_a_party_with_only_a_companion_left_ends_the_run(
        controller:GameController) -> None:
    from cursed_descent.events.maid.event import make_companion
    start_pair(controller)
    session = controller.session
    connie = make_companion(1)
    session.repository.add(connie)
    session.party.append(connie)
    for name in ("kerl", "galactica"):
        session.member(name).alive = False
    controller.tick(5.0)
    assert session.state == "idle"
    assert session.member("Connie") is None



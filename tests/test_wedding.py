import pytest

from cursed_descent.settings import fill
from cursed_descent.controller import GameController
from cursed_descent.models import Player
from cursed_descent.npcs.places import place_residents
from cursed_descent.spawns import RULES_BY_KIND
from cursed_descent.web.run_panels import wedding_panel


def texts(messages) -> str:
    return "\n".join(message.text for message in messages)


def at_wedding(controller:GameController, inside:bool=True) -> None:
    controller.handle("kerl", "!lobby", now=0.0)
    controller.handle("galactica", "!join", now=0.5)
    controller.handle("kerl", "!start", now=1.0)
    controller.session.stage = 16
    controller.session.events.offer_location("wedding", 2.0)
    if inside:
        controller.handle("kerl", "!enter", now=2.5)


def test_the_wedding_starts_outside_with_enter_and_pass(
        controller:GameController) -> None:
    at_wedding(controller, inside=False)
    options = controller.session.events.available()
    assert options == ["enter", "examine", "pass"]


def test_entering_the_wedding_opens_the_actions(
        controller:GameController) -> None:
    at_wedding(controller)
    options = controller.session.events.available()
    assert options == ["eat", "congratulate", "examine", "depart"]


def test_the_wedding_panel_has_talk_buttons_for_every_guest(
        controller:GameController) -> None:
    at_wedding(controller)
    kerl = controller.session.member("kerl")
    panel = wedding_panel(controller.session.events, kerl)
    commands = [button.command for section in panel.sections[0].sections
                for button in section.buttons]
    for name in ("Ottilie", "Emmerich", "Brannock", "Merewyn", "Tobin"):
        assert f"!talk {name}" in commands
        assert f"!talk {name} work" in commands
        assert f"!examine {name}" in commands


def test_the_wedding_panel_outside_has_enter_and_pass(
        controller:GameController) -> None:
    at_wedding(controller, inside=False)
    kerl = controller.session.member("kerl")
    panel = wedding_panel(controller.session.events, kerl)
    assert [button.command for button in panel.buttons] == [
        "!enter", "!examine", "!pass"]


def test_eating_heals_once(controller:GameController) -> None:
    at_wedding(controller)
    kerl = controller.session.member("kerl")
    kerl.hp = 1
    texts(controller.handle("kerl", "!eat", now=3.0))
    assert kerl.hp > 1
    assert "eat" not in controller.session.events.available()


def test_congratulating_gives_gold_and_an_item_once(
        controller:GameController) -> None:
    at_wedding(controller)
    kerl = controller.session.member("kerl")
    gold = kerl.gold
    reply = texts(controller.handle("kerl", "!congratulate", now=3.0))
    assert kerl.gold > gold and "Emmerich" in reply
    assert "congratulate" not in controller.session.events.available()


@pytest.mark.parametrize("name", ["Ottilie", "Emmerich", "Brannock",
                                  "Merewyn", "Tobin"])
def test_every_guest_talks_by_topic(controller:GameController,
                                    name:str) -> None:
    at_wedding(controller)
    for topic in ("work", "town", "self"):
        reply = texts(controller.handle("kerl", f"!talk {name} {topic}",
                                        now=4.0))
        assert name in reply and "'" in reply


def test_the_guests_are_the_place_keepers(
        controller:GameController) -> None:
    at_wedding(controller)
    names = [resident.first_name for resident in
             place_residents(controller.session.events.event)]
    assert names == ["Ottilie", "Emmerich", "Brannock", "Merewyn", "Tobin"]


def test_the_couple_have_the_planned_ages_and_bodies() -> None:
    from cursed_descent.locations.wedding.npc import EMMERICH, OTTILIE
    assert OTTILIE.age == 58 and EMMERICH.age == 18
    assert dict(OTTILIE.body)["endowment"] == 55
    assert dict(EMMERICH.body)["height"] == 170


def test_ottilie_can_be_examined(controller:GameController) -> None:
    at_wedding(controller)
    assert "Aldric" in texts(controller.handle("kerl", "!examine Ottilie",
                                               now=4.0))


def test_the_spouse_field_survives_saving() -> None:
    player = Player(name="Ottilie")
    player.spouse = "Emmerich"
    assert Player.from_dict(player.to_dict()).spouse == "Emmerich"


def test_the_wedding_starts_on_stage_15() -> None:
    assert RULES_BY_KIND["wedding"].min_stage == 15


def test_the_aldric_items_exist() -> None:
    from cursed_descent.content import ITEMS
    assert all(ITEMS[key]["no_loot"] for key in
               ("aldric_boots", "aldric_corset", "aldric_gloves"))


def test_the_boot_smell_grows_with_the_feast(
        controller:GameController) -> None:
    at_wedding(controller)
    first = texts(controller.handle("kerl", "!examine", now=3.0))
    assert "polish" in first
    controller.handle("kerl", "!eat", now=4.0)
    second = texts(controller.handle("kerl", "!examine", now=5.0))
    assert "worn all day" in second
    controller.handle("kerl", "!congratulate", now=6.0)
    third = texts(controller.handle("kerl", "!examine", now=7.0))
    assert "the man they were made from" in third


def test_no_npc_shares_a_first_name_with_another() -> None:
    from cursed_descent.npcs.seed import default_npcs
    names = [npc.first_name.casefold() for npc in default_npcs()]
    assert len(names) == len(set(names))


def test_emmerich_gets_more_aroused_as_the_feast_goes_on(
        controller:GameController) -> None:
    at_wedding(controller)
    first = texts(controller.handle("kerl", "!examine Emmerich", now=3.0))
    assert "exactly what tonight is for" in first
    controller.handle("kerl", "!eat", now=4.0)
    second = texts(controller.handle("kerl", "!examine Emmerich", now=5.0))
    assert "taken for the first time" in second
    assert "night_ready" not in controller.session.events.event["data"]
    controller.handle("kerl", "!congratulate", now=6.0)
    third = texts(controller.handle("kerl", "!examine Emmerich", now=7.0))
    assert "Mom will make me hers" in third
    assert controller.session.events.event["data"]["night_ready"] is True


def test_examining_other_guests_still_uses_their_description(
        controller:GameController) -> None:
    at_wedding(controller)
    assert "tankard" in texts(controller.handle("kerl", "!examine Brannock",
                                                now=3.0))


@pytest.mark.parametrize("name", ["Ottilie", "Emmerich", "Brannock",
                                  "Merewyn", "Tobin"])
def test_every_guest_has_new_lines_at_each_stage(
        controller:GameController, name:str) -> None:
    from cursed_descent.locations.wedding.content import GUEST_STAGES
    at_wedding(controller)
    key = next(key for key in GUEST_STAGES if key.split("_")[0] in
               (name.lower(), "baroness", "old", "sister")
               and name.lower() in key)
    stage_lines = {stage: {line for lines in GUEST_STAGES[key][stage].values()
                           for line in lines} for stage in (1, 2)}
    assert stage_lines[1].isdisjoint(stage_lines[2])
    controller.handle("kerl", "!eat", now=3.0)
    reply = texts(controller.handle("kerl", f"!talk {name} self", now=4.0))
    assert any(fill(line) in reply for line in stage_lines[1])
    controller.handle("kerl", "!congratulate", now=5.0)
    reply = texts(controller.handle("kerl", f"!talk {name} self", now=6.0))
    assert any(fill(line) in reply for line in stage_lines[2])


def test_the_base_lines_come_back_after_leaving_the_stage_topics(
        controller:GameController) -> None:
    at_wedding(controller)
    controller.handle("kerl", "!eat", now=3.0)
    controller.handle("kerl", "!talk Ottilie self", now=4.0)
    npc = next(n for n in controller.repository.npc_players()
               if n.first_name == "Ottilie")
    assert len(npc.profile["topics"]["self"]) == 3


def test_the_cage_and_plug_hints_appear_with_the_progress(
        controller:GameController) -> None:
    at_wedding(controller)
    controller.handle("kerl", "!eat", now=3.0)
    first = texts(controller.handle("kerl", "!examine Emmerich", now=4.0))
    assert "careful steps" in first
    controller.handle("kerl", "!congratulate", now=5.0)
    second = texts(controller.handle("kerl", "!examine Emmerich", now=6.0))
    assert "steel cage" in second


def test_dance_and_night_unlock_in_order_and_end_the_event(
        controller:GameController) -> None:
    from cursed_descent.locations.wedding.content import DANCES, NIGHTS
    at_wedding(controller)
    options = controller.session.events.available()
    assert "dance" not in options and "night" not in options
    controller.handle("kerl", "!eat", now=3.0)
    controller.handle("kerl", "!congratulate", now=4.0)
    assert "dance" in controller.session.events.available()
    reply = texts(controller.handle("kerl", "!dance", now=5.0))
    assert any(fill(dance) in reply for dance in DANCES)
    options = controller.session.events.available()
    assert "night" in options and "dance" not in options
    kerl = controller.session.member("kerl")
    gold = kerl.gold
    reply = texts(controller.handle("kerl", "!night", now=6.0))
    assert any(fill(night) in reply for night in NIGHTS)
    assert kerl.gold > gold
    assert controller.session.state != "event" or (
        controller.session.events.event.get("phase") != "wedding")


def test_eating_adds_a_chalice_scene_and_a_guest_reaction(
        controller:GameController) -> None:
    from cursed_descent.locations.wedding.content import (
        EAT_CHALICE, EAT_REACTIONS,
    )
    at_wedding(controller)
    reply = texts(controller.handle("kerl", "!eat", now=3.0))
    assert any(fill(scene) in reply for scene in EAT_CHALICE)
    assert any(fill(line) in reply for line in EAT_REACTIONS)
    assert "shiny" in texts(controller.handle("kerl", "!examine Emmerich",
                                              now=4.0))


def test_ottilie_has_an_equine_endowment() -> None:
    from cursed_descent.locations.wedding.npc import OTTILIE
    assert dict(OTTILIE.body)["endowment_shape"] == "Equine"
    assert "equine" in OTTILIE.look


def test_ottilie_has_an_equine_endowment() -> None:
    from cursed_descent.npcs.seed import default_npcs
    ottilie = next(npc for npc in default_npcs()
                   if npc.first_name == "Ottilie")
    assert ottilie.body["endowment_shape"] == "Equine"


def test_the_wedding_night_marries_them_and_makes_emmerich_pregnant(
        controller:GameController) -> None:
    from cursed_descent.births import give_birth
    at_wedding(controller)
    for step, command in enumerate(("eat", "congratulate", "dance",
                                    "night")):
        reply = texts(controller.handle("kerl", f"!{command}",
                                        now=3.0 + step))
    assert "The heir" in reply
    people = {npc.npc: npc for npc in controller.repository.npc_players()}
    emmerich = people["emmerich_grimhold"]
    ottilie = people["baroness_ottilie"]
    assert emmerich.pregnant == "party"
    assert emmerich.profile["pregnant_by"] == "Ottilie"
    assert emmerich.profile["pregnant_by_id"] == ottilie.id
    assert emmerich.spouse == "Ottilie" and ottilie.spouse == "Emmerich"
    assert "Ottilie" in give_birth(emmerich) or emmerich.offspring



def test_the_wedding_comes_only_once_per_run(
        controller:GameController, monkeypatch:pytest.MonkeyPatch) -> None:
    from cursed_descent.spawn_rule import SpawnRule
    from cursed_descent import events
    at_wedding(controller)
    handler = controller.session.events
    only = [SpawnRule("wedding", 1, 1, once_per_run=True)]
    monkeypatch.setattr(events.handler, "eligible", lambda stage: only)
    handler.once_seen = set()
    handler.once_run = controller.session.run_id
    first, _ = handler.pick_kind(20)
    second, _ = handler.pick_kind(21)
    assert first == "wedding" and second == ""
    controller.session.run_id = "another-run"
    third, _ = handler.pick_kind(22)
    assert third == "wedding"


def test_the_smell_lines_come_with_eat_and_dance(
        controller:GameController) -> None:
    from cursed_descent.locations.wedding.content import (
        DANCE_SMELLS, DANCE_TEARS, DANCE_TEARS_OTTILIE, EAT_SMELLS,
    )
    at_wedding(controller)
    reply = texts(controller.handle("kerl", "!eat", now=3.0))
    assert any(fill(line) in reply for line in EAT_SMELLS)
    controller.handle("kerl", "!congratulate", now=4.0)
    reply = texts(controller.handle("kerl", "!dance", now=5.0))
    assert any(fill(line) in reply for line in DANCE_SMELLS)
    assert any(fill(line) in reply for line in DANCE_TEARS)
    assert fill(DANCE_TEARS_OTTILIE) in reply
    look = texts(controller.handle("kerl", "!examine Emmerich", now=6.0))
    assert "watering" in look and "chalice" in look


def test_an_existing_ottilie_file_gets_the_equine_shape(
        controller:GameController) -> None:
    from cursed_descent.npcs.seed import seed_npcs
    repository = controller.repository
    ottilie = next(npc for npc in repository.npc_players()
                   if npc.npc == "baroness_ottilie")
    ottilie.body["endowment_shape"] = "Human"
    repository.save(ottilie)
    seed_npcs(repository)
    again = next(npc for npc in repository.npc_players()
                 if npc.npc == "baroness_ottilie")
    assert again.body["endowment_shape"] == "Equine"


def test_ottilies_sweat_rises_with_the_feast_and_is_saved(
        controller:GameController) -> None:
    from cursed_descent.sweat import sweat_tier

    def ottilie():
        npc = next(npc for npc in controller.repository.npc_players()
                   if npc.npc == "baroness_ottilie")
        npc.sweat = npc.profile.get("sweat", 0)
        return npc

    at_wedding(controller)
    assert ottilie().sweat == 0
    controller.handle("kerl", "!eat", now=3.0)
    assert ottilie().sweat == 8
    controller.handle("kerl", "!congratulate", now=4.0)
    assert ottilie().sweat == 14
    reply = texts(controller.handle("kerl", "!dance", now=5.0))
    assert ottilie().sweat == 30 and sweat_tier(ottilie()) == 2
    assert "Ottilie" in reply
    look = texts(controller.handle("kerl", "!examine Ottilie", now=6.0))
    assert "Sweat:" in look and "Aldric" in look
    controller.handle("kerl", "!night", now=7.0)
    assert ottilie().sweat == 50 and sweat_tier(ottilie()) == 3


def test_a_new_wedding_starts_with_a_dry_ottilie(
        controller:GameController) -> None:
    at_wedding(controller)
    controller.handle("kerl", "!eat", now=3.0)
    controller.session.events.offer_location("wedding", 5.0)
    ottilie = next(npc for npc in controller.repository.npc_players()
                   if npc.npc == "baroness_ottilie")
    assert ottilie.profile["sweat"] == 0


def test_ottilie_wears_the_first_husbands_sheath(
        controller:GameController) -> None:
    at_wedding(controller)
    reply = texts(controller.handle("kerl", "!examine Ottilie", now=4.0))
    assert "once a husband" in reply
    ottilie = next(npc for npc in controller.repository.npc_players()
                   if npc.npc == "baroness_ottilie")
    assert ottilie.equipment["crotch"] == (
        "baroness_ottilie_first_husband_sheath")


def test_old_ottilie_gets_the_sheath_on_sync(
        controller:GameController) -> None:
    from cursed_descent.npcs.seed import default_npcs, sync_gear
    repository = controller.repository
    old = next(npc for npc in repository.npc_players()
               if npc.npc == "baroness_ottilie")
    old.equipment["crotch"] = None
    old.profile["gear"] = 2
    repository.save(old)
    sync_gear(repository, default_npcs())
    new = next(npc for npc in repository.npc_players()
               if npc.npc == "baroness_ottilie")
    assert new.equipment["crotch"].endswith("first_husband_sheath")


def test_the_family_history_is_told_by_the_guests(
        controller:GameController) -> None:
    at_wedding(controller)
    controller.handle("kerl", "!eat", now=3.0)
    lines = " ".join(texts(controller.handle(
        "kerl", f"!talk {name} self", now=4.0 + number))
        for number in range(6) for name in ("Brannock", "Merewyn",
                                            "Emmerich"))
    assert "first husband" in lines or "Aldric, too" in lines

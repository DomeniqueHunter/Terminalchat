import random
import re
import shutil
import sys
from pathlib import Path

import pytest

from cursed_descent import routines
from cursed_descent.routines import (
    ANY, Place, RoutineBoard, Schedule, Spot, Stop, Wander, discovery,
)
from cursed_descent.towns import TOWNS


HOME = Place("dusk_hollow", "brothel")
TOWNS_MAP = {"dusk_hollow": ("tavern", "shop", "brothel"),
             "last_light": ("tavern", "shop")}
README = Path(__file__).resolve().parent.parent / "readme" / "routines.md"


def test_a_stop_covers_hours_even_across_midnight() -> None:
    night = Stop("brothel", 22, 4)
    assert night.covers(23) and night.covers(2) and not night.covers(12)
    day = Stop("shop", 9, 17)
    assert day.covers(9) and not day.covers(17)


def test_schedule_follows_the_hour_and_returns_home_otherwise() -> None:
    plan = Schedule("x", (Stop("tavern", 18, 22),
                          Stop("shop", 9, 11, town="last_light")))
    rng = random.Random(1)
    assert plan.place(19, HOME, rng, {}, TOWNS_MAP) == Place(
        "dusk_hollow", "tavern")
    assert plan.place(24 * 5 + 10, HOME, rng, {}, TOWNS_MAP) == Place(
        "last_light", "shop")
    assert plan.place(14, HOME, rng, {}, TOWNS_MAP) == HOME


def test_wander_stays_for_its_time_then_moves() -> None:
    walk = Wander("x", spots=(Spot("tavern"), Spot("shop")), stay=(2, 2))
    rng, state = random.Random(3), {}
    first = walk.place(0, HOME, rng, state, TOWNS_MAP)
    assert walk.place(1.9, HOME, rng, state, TOWNS_MAP) == first
    seen = {walk.place(2 * step, HOME, rng, state, TOWNS_MAP)
            for step in range(1, 30)}
    assert seen == {Place("dusk_hollow", "tavern"),
                    Place("dusk_hollow", "shop")}


def test_wander_without_spots_uses_every_allowed_town() -> None:
    own = Wander("x")
    assert {place for place, _ in own.candidates(HOME, TOWNS_MAP)} == {
        Place("dusk_hollow", name) for name in TOWNS_MAP["dusk_hollow"]}
    world = Wander("x", towns=(ANY,))
    assert len(world.candidates(HOME, TOWNS_MAP)) == 5


def test_every_routine_file_in_the_game_is_valid() -> None:
    discovery.reset()
    homes = routines.board.homes()
    for key, routine in discovery.routines().items():
        assert key in homes


def test_npcs_without_a_routine_stay_home(monkeypatch) -> None:
    monkeypatch.setattr(discovery, "_FOUND", {})
    board = RoutineBoard(random.Random(1))
    board.tick(100.0)
    assert routines.PLACES == {}
    home = routines.board.homes()["camilla"]
    assert routines.present(home.town, home.building).count("camilla") == 1


def test_a_routine_moves_the_npc_and_the_panels_follow(monkeypatch) -> None:
    home = routines.board.homes()["camilla"]
    plan = Schedule("camilla", (Stop("tavern", 18, 22),))
    monkeypatch.setattr(discovery, "_FOUND", {"camilla": plan})
    board = RoutineBoard(random.Random(1))
    board.tick(19)
    assert routines.location_of("camilla") == Place(home.town, "tavern")
    assert "camilla" not in routines.present(home.town, home.building)
    assert "camilla" in routines.present(home.town, "tavern")
    names = [person.key for person in routines.people(home.town, "tavern")]
    assert "camilla" in names
    board.tick(23)
    assert routines.location_of("camilla") is None
    assert "camilla" in routines.present(home.town, home.building)
    routines.PLACES.clear()


def test_an_npc_in_another_town_is_gone_from_home_and_visits(monkeypatch) -> None:
    home = routines.board.homes()["camilla"]
    other = next(key for key in TOWNS if key != home.town)
    plan = Schedule("camilla", (Stop("shop", 0, 24, town=other),))
    monkeypatch.setattr(discovery, "_FOUND", {"camilla": plan})
    RoutineBoard(random.Random(1)).tick(5)
    assert routines.location_of("camilla") == Place(other, "shop")
    assert "camilla" in routines.present(other, "shop")
    routines.PLACES.clear()


def test_town_services_tick_moves_npcs(monkeypatch, tmp_path) -> None:
    from tests.test_cafe import setup_pair
    from cursed_descent.controller import GameController
    controller = GameController(data_path=tmp_path)
    plan = Schedule("camilla", (Stop("tavern", 0, 24),))
    monkeypatch.setattr(discovery, "_FOUND", {"camilla": plan})
    controller.town.tick(10.0)
    assert routines.location_of("camilla") is not None
    assert controller.town.visit_places()["camilla"] == "tavern"
    routines.PLACES.clear()


def test_duplicate_routines_are_refused(monkeypatch) -> None:
    folder = discovery.TOWNS_DIR / "mudgate_goblins" / "black_market"
    target = folder / "routines.py"
    target.write_text(
        "from ....routines import Schedule\n"
        "ROUTINES = (Schedule('a', ()), Schedule('a', ()))\n",
        encoding="utf-8")
    discovery.reset()
    try:
        with pytest.raises(ValueError, match="already has"):
            discovery.routines()
    finally:
        target.unlink()
        discovery.reset()
        for name in [m for m in sys.modules if m.endswith(".routines")
                     and "mudgate" in m]:
            del sys.modules[name]


def test_the_readme_example_is_a_working_routine_file() -> None:
    block = re.search(r"```python\n(.*?)```", README.read_text(),
                      re.S).group(1)
    folder = discovery.TOWNS_DIR / "dusk_hollow_vampires" / "brothel"
    target = folder / "routines.py"
    target.write_text(block, encoding="utf-8")
    discovery.reset()
    try:
        found = discovery.routines()
        assert {"camilla", "serafine"} <= set(found)
        assert isinstance(found["camilla"], Schedule)
        assert isinstance(found["serafine"], Wander)
    finally:
        target.unlink()
        discovery.reset()
        for name in [m for m in sys.modules if m.endswith(".routines")
                     and "dusk_hollow" in m]:
            del sys.modules[name]


def test_bertha_is_the_first_npc_with_a_routine() -> None:
    discovery.reset()
    plan = discovery.routines()["bertha"]
    assert isinstance(plan, Schedule)
    home = routines.board.homes()["bertha"]
    assert home == Place("last_light", "cafe")
    assert plan.place(10.5, home, random.Random(1), {}, {}) == Place(
        "last_light", "bank")
    assert plan.place(15, home, random.Random(1), {}, {}) == home


def test_an_npc_is_only_reachable_where_she_is(monkeypatch,
                                               controller) -> None:
    kerl = controller.repository.load("Kerl")
    kerl.profile["where"] = "cafe"
    plan = Schedule("bertha", (Stop("bank", 0, 24),))
    monkeypatch.setattr(discovery, "_FOUND", {"bertha": plan})
    RoutineBoard(random.Random(1)).tick(5)
    assert routines.reachable(kerl, "bertha") is False
    kerl.profile["where"] = "bank"
    assert routines.reachable(kerl, "bertha") is True
    assert routines.reachable(kerl, "someone_without_routine") is True
    kerl.profile["where"] = "cafe"
    reply = controller.town.do_chat(kerl, ["Bertha"])
    assert "not here" in reply[0].text
    kerl.profile["where"] = "bank"
    reply = controller.town.do_chat(kerl, ["Bertha"])
    assert "not here" not in reply[0].text
    routines.PLACES.clear()


def test_an_absent_npc_is_listed_greyed_out_with_a_note(monkeypatch) -> None:
    from cursed_descent.web.views import residents_panel
    town = TOWNS["last_light"]
    plan = Schedule("bertha", (Stop("bank", 0, 24),))
    monkeypatch.setattr(discovery, "_FOUND", {"bertha": plan})
    RoutineBoard(random.Random(1)).tick(5)
    panel = residents_panel(town, "cafe")
    section = next(item for item in panel.sections
                   if item.title.startswith("Madame Bertha"))
    assert section.lines and section.lines[0].startswith("away: at the")
    assert "Bank" in section.lines[0]
    assert section.buttons and not any(b.enabled for b in section.buttons)
    bank = residents_panel(town, "bank")
    here = next(item for item in bank.sections
                if item.title.startswith("Madame Bertha"))
    assert here.lines == () and all(b.enabled for b in here.buttons)
    routines.PLACES.clear()
    back = residents_panel(town, "cafe")
    home = next(item for item in back.sections
                if item.title.startswith("Madame Bertha"))
    assert home.lines == () and all(b.enabled for b in home.buttons)


def test_the_not_here_message_says_where_she_is(monkeypatch,
                                                controller) -> None:
    kerl = controller.repository.load("Kerl")
    kerl.profile["where"] = "cafe"
    controller.repository.save(kerl)
    plan = Schedule("bertha", (Stop("tavern", 0, 24),))
    monkeypatch.setattr(discovery, "_FOUND", {"bertha": plan})
    RoutineBoard(random.Random(1)).tick(5)
    for command in ("!examine bertha", "!talk bertha", "!chat bertha"):
        reply = controller.handle("Kerl", command)[0].text
        assert "Madame Bertha" in reply and "away: at the Tavern." in reply, reply
    assert routines.away_message(kerl, "nobody") == ""
    kerl.profile["where"] = "tavern"
    controller.repository.save(kerl)
    assert "away" not in controller.handle("Kerl", "!talk bertha")[0].text
    routines.PLACES.clear()


def test_routine_texts_are_filled_for_berthas_places() -> None:
    from cursed_descent.routines import texts
    texts.reset()
    found = texts.texts()["bertha"]
    for place in ("bank", "tavern"):
        assert found[place].examine and len(found[place].dialogues) >= 3


def test_examine_and_talk_use_the_place_texts(monkeypatch,
                                              controller) -> None:
    from cursed_descent.routines import texts
    texts.reset()
    kerl = controller.repository.load("Kerl")
    plan = Schedule("bertha", (Stop("tavern", 0, 24),))
    monkeypatch.setattr(discovery, "_FOUND", {"bertha": plan})
    RoutineBoard(random.Random(1)).tick(5)
    kerl.profile["where"] = "tavern"
    controller.repository.save(kerl)
    seen = controller.handle("Kerl", "!examine bertha")[0].text
    assert texts.texts()["bertha"]["tavern"].examine in seen
    said = controller.handle("Kerl", "!talk bertha")[0].text
    assert any(line in said for line in texts.texts()["bertha"][
        "tavern"].dialogues)
    chat = controller.handle("Kerl", "!chat bertha work")[0].text
    assert any(line in chat for line in texts.texts()["bertha"][
        "tavern"].dialogues)
    routines.PLACES.clear()


def test_empty_place_texts_grey_out_the_buttons(monkeypatch,
                                                controller) -> None:
    from cursed_descent.routines import texts
    from cursed_descent.web.views import residents_panel
    monkeypatch.setattr(texts, "_CACHE", {"bertha": {}})
    kerl = controller.repository.load("Kerl")
    plan = Schedule("bertha", (Stop("tavern", 0, 24),))
    monkeypatch.setattr(discovery, "_FOUND", {"bertha": plan})
    RoutineBoard(random.Random(1)).tick(5)
    kerl.profile["where"] = "tavern"
    controller.repository.save(kerl)
    panel = residents_panel(TOWNS["last_light"], "tavern")
    section = next(item for item in panel.sections
                   if item.title.startswith("Madame Bertha"))
    assert not any(button.enabled for button in section.buttons)
    assert "yet" in section.lines[0]
    assert "nothing to see yet" in controller.handle(
        "Kerl", "!examine bertha")[0].text
    assert "nothing to say here yet" in controller.handle(
        "Kerl", "!talk bertha")[0].text
    assert "nothing to say here yet" in controller.handle(
        "Kerl", "!chat bertha")[0].text
    routines.PLACES.clear()
    texts.reset()


def place_bertha(monkeypatch, uses, building="tavern"):
    plan = Schedule("bertha", (Stop(building, 0, 24),), uses=uses)
    monkeypatch.setattr(discovery, "_FOUND", {"bertha": plan})
    RoutineBoard(random.Random(1)).tick(5)


def test_a_routine_in_the_own_building_is_refused(monkeypatch) -> None:
    plan = Schedule("bertha", (Stop("cafe", 10, 11),))
    monkeypatch.setattr(discovery, "_FOUND", {"bertha": plan})
    with pytest.raises(ValueError, match="own building"):
        RoutineBoard(random.Random(1))
    spots = Wander("bertha", spots=(Spot("cafe"),))
    monkeypatch.setattr(discovery, "_FOUND", {"bertha": spots})
    with pytest.raises(ValueError, match="own building"):
        RoutineBoard(random.Random(1))


def test_the_tavern_lists_actions_with_needs() -> None:
    options = routines.actions.actions_for("last_light", "tavern")
    assert {"order_drink", "serve_order", "watch_dancer",
            "milk_barrel"} <= set(options)
    assert options["order_drink"].needs == ""
    assert options["milk_barrel"].needs == "milk"


def test_a_free_action_is_shown_to_those_in_the_building(
        monkeypatch, controller) -> None:
    kerl = controller.repository.load("Kerl")
    kerl.profile["where"] = "tavern"
    controller.repository.save(kerl)
    place_bertha(monkeypatch, ("order_drink",))
    board = routines.actions.ActionBoard(random.Random(2))
    lines = routines.actions.perform(controller.town, "bertha",
                                     routines.location_of("bertha"),
                                     random.Random(2))
    assert len(lines) >= 1
    assert all("Madame Bertha orders a mug" in line.text for line in lines)
    assert "kerl" in {line.recipient for line in lines}
    routines.PLACES.clear()


def test_an_action_with_needs_waits_for_a_worker_and_pays(
        monkeypatch, controller) -> None:
    from types import SimpleNamespace
    place_bertha(monkeypatch, ("serve_order",))
    rng = random.Random(3)
    place = routines.location_of("bertha")
    assert routines.actions.perform(controller.town, "bertha", place,
                                    rng) == []
    controller.town.shifts["Kerl"] = SimpleNamespace(
        building="tavern", job=SimpleNamespace(key="waiter"), client=None)
    before = controller.repository.load("Kerl").gold
    lines = routines.actions.perform(controller.town, "bertha", place, rng)
    assert len(lines) == 1 and "tip" in lines[0].text
    assert controller.repository.load("Kerl").gold > before
    routines.PLACES.clear()


def test_an_npc_only_uses_what_she_may_and_never_at_home(
        monkeypatch, controller) -> None:
    from types import SimpleNamespace
    place_bertha(monkeypatch, ("order_drink",))
    controller.town.shifts["Kerl"] = SimpleNamespace(
        building="tavern", job=SimpleNamespace(key="waiter"), client=None)
    lines = routines.actions.perform(
        controller.town, "bertha", routines.location_of("bertha"),
        random.Random(4))
    assert all("tip" not in line.text for line in lines)
    routines.PLACES.clear()
    board = routines.actions.ActionBoard(random.Random(1))
    assert board.tick(controller.town, 10_000.0) == []


def test_the_action_board_fires_on_its_timer(monkeypatch,
                                              controller) -> None:
    kerl = controller.repository.load("Kerl")
    kerl.profile["where"] = "tavern"
    controller.repository.save(kerl)
    place_bertha(monkeypatch, ("order_drink",))
    board = routines.actions.ActionBoard(random.Random(1))
    assert board.tick(controller.town, 0.0) == []
    assert board.tick(controller.town, 1000.0)
    routines.PLACES.clear()


def test_guest_npcs_join_the_visitors_of_a_building(monkeypatch,
                                                    controller) -> None:
    kerl = controller.repository.load("Kerl")
    controller.town.visits_on = True
    place_bertha(monkeypatch, ("guest",), building="brothel")
    assert routines.actions.guests_at("last_light", "brothel") == ["bertha"]
    records = controller.town.visitor_records(kerl, "brothel")
    assert any(record["npc"] == "bertha" for record in records)
    routines.PLACES.clear()


def test_debug_time_shows_the_clock_and_where_the_npcs_are(
        monkeypatch, controller) -> None:
    controller.debug = True
    reply = controller.handle("Kerl", "!time")[0].text
    assert "🕐" in reply and "Routine NPCs:" in reply
    assert "Madame Bertha Rump" in reply
    reply = controller.handle("Kerl", "!time 21")[0].text
    assert ", 21:0" in reply and "Tavern" in reply
    reply = controller.handle("Kerl", "!time 15:30")[0].text
    assert ", 15:3" in reply and "at home" in reply
    assert "Usage" in controller.handle("Kerl", "!time 99")[0].text
    controller.debug = False
    assert controller.handle("Kerl", "!time") == []
    routines.PLACES.clear()


def test_alexandra_has_a_routine_with_texts_for_every_place() -> None:
    from cursed_descent.routines import texts
    discovery.reset()
    texts.reset()
    plan = discovery.routines()["alexandra"]
    home = routines.board.homes()["alexandra"]
    assert home == Place("dusk_hollow", "castle")
    names = {stop.building for stop in plan.stops}
    assert names == {"blood_bank", "tavern", "salon", "brothel"}
    for name in names:
        found = texts.texts()["alexandra"][name]
        assert found.examine and len(found.dialogues) >= 3
    assert plan.place(21.5, home, random.Random(1), {}, {}) == Place(
        "dusk_hollow", "tavern")
    assert plan.place(0, home, random.Random(1), {}, {}) == Place(
        "dusk_hollow", "salon")
    assert plan.place(12, home, random.Random(1), {}, {}) == home
    RoutineBoard(random.Random(1))


def test_talk_works_in_every_town(controller) -> None:
    kerl = controller.repository.load("Kerl")
    kerl.profile["town"] = "dusk_hollow"
    kerl.profile["where"] = "castle"
    controller.repository.save(kerl)
    reply = controller.handle("Kerl", "!talk Alexandra")[0].text
    assert "Nobody called" not in reply and "Alexandra" in reply


def test_window_is_active_at_home_only() -> None:
    plan = Schedule("x", (Stop("tavern", 20, 22),),
                    windows=(routines.Window("sleep", 4, 6),
                             routines.Window("eat", 6, 7)))
    assert plan.window(5) == "sleep" and plan.window(6.5) == "eat"
    assert plan.window(12) == ""


def test_window_texts_replace_default_at_home(monkeypatch) -> None:
    from cursed_descent.routines import board, texts
    monkeypatch.setitem(board.WINDOWS, "alexandra", "sleep")
    monkeypatch.setattr(texts, "_CACHE", {"alexandra": {
        "@sleep": texts.Entry("She sleeps.", ())}})
    entry = texts.at_place("alexandra")
    assert entry.examine == "She sleeps." and not entry.dialogues


def test_slave_action_uses_you_form_hook_and_follows(controller,
                                                      monkeypatch) -> None:
    from cursed_descent import control
    from cursed_descent.control import ControlKind, discovery as cd
    from cursed_descent.routines import actions, board
    from cursed_descent.routines.actions import Action
    from cursed_descent.towns import TOWNS
    town = next(key for key, each in TOWNS.items()
                if any(person.key == "alexandra" for person in each.residents))
    monkeypatch.setattr(cd, "_FOUND", {
        "t": ControlKind(key="t", title="T")})
    kerl = controller.repository.load("Kerl")
    kerl.profile["town"] = "last_light_humans"
    control.start(controller.town, kerl, "t", "Alexandra", npc="alexandra")
    controller.town.routines.tick(12.0)
    actions.follow(controller.town)
    kerl = controller.repository.load("Kerl")
    assert kerl.profile["town"] == town
    assert kerl.profile["where"] == board.homes()["alexandra"].building
    calls = []
    hook = lambda services, npc, worker, place: calls.append(
        worker.name) or []
    monkeypatch.setattr(actions, "hook_for", lambda place, name: hook)
    monkeypatch.setitem(
        actions._CACHE, (TOWNS[town].folder, "castle"), {"cuddle": Action(
            "cuddle", 1, "slave", "{npc} holds {name} close.",
            text_slave="{npc} holds you close.", when="home", hook="x")})
    monkeypatch.setitem(actions.routines(), "alexandra", Schedule(
        "alexandra", (), uses=("cuddle",)))
    reply = actions.perform(controller.town, "alexandra",
                            board.homes()["alexandra"], random.Random(1))
    assert "holds you close" in "\n".join(m.text for m in reply)
    assert [c.casefold() for c in calls] == ["kerl"]

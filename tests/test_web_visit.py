import random
from pathlib import Path

from cursed_descent.house_visit import enter
from cursed_descent.web import views, visit
from cursed_descent.web.hub import Client, GameHub


def visiting(hub:GameHub):
    repository = hub.controller.repository
    kerl = repository.load("kerl")
    kerl.age = 30
    host = repository.load("Beverley Morningwood")
    for seed in range(200):
        _, home = enter(kerl, host, "house", "default", "1 Test Lane",
                        "Test Lane", "", repository, random.Random(seed))
        if home:
            break
    repository.save(kerl)
    return kerl, host


def test_visiting_a_house_adds_the_home_tab(data_path:Path) -> None:
    hub = GameHub(data_path)
    kerl, host = visiting(hub)
    state = visit.current_visit(hub.controller, kerl)
    panel = visit.visit_panel(hub.controller, kerl, state)
    titles = [section.title for section in panel.sections]
    assert {"Examine", "Present", "Talk to:", "Do:", "Sex with:"} <= set(
        titles)
    page = hub.panels_for(Client(None, "kerl"))
    assert 'id="tabbtn-visit"' in page and "Leave the house" in page
    assert f"Home – {host.name}" in page


def test_the_sex_tab_lists_acts_with_scene_fields(data_path:Path) -> None:
    hub = GameHub(data_path)
    kerl, host = visiting(hub)
    host.profile.setdefault("friends", {})[kerl.id] = 10 ** 4
    hub.controller.repository.save(host)
    hub.controller.handle("kerl", f"!house sex {host.name}")
    kerl = hub.controller.repository.load("kerl")
    panel = visit.sex_panel(hub.controller, kerl)
    assert panel is not None and panel.title.startswith("💞 Sex")
    names = [section.title for section in panel.sections]
    assert "Your role" in names and "Scene" in names
    act_rows = [s for s in panel.sections if s.rows][0].rows
    assert act_rows and act_rows[0].buttons[0].command.startswith(
        f"!house practice {host.name} ")
    page = hub.panels_for(Client(None, "kerl"))
    assert 'name="s_amount"' in page


def test_practice_and_seat_commands_take_the_scene_fields(
        data_path:Path) -> None:
    hub = GameHub(data_path)
    send = hub.command_text
    assert send({"text": "!house practice Rose oral give",
                 "s_amount": "much", "s_where": "on"}
                ) == "!house practice Rose oral give much on"
    assert send({"text": "!home practice Rose oral give"}
                ) == "!home practice Rose oral give some in"
    assert send({"text": "!house seat", "intensity": "hard",
                 "length": "short"}) == "!house seat hard short confirm"
    assert send({"text": "!house order Rose", "title": "Master"}
                ) == "!house order Rose Master"
    assert send({"text": "!house leave"}) == "!house leave"


def test_no_visit_means_no_tabs(data_path:Path) -> None:
    hub = GameHub(data_path)
    kerl = hub.controller.repository.load("kerl")
    assert visit.current_visit(hub.controller, kerl) is None
    assert visit.sex_panel(hub.controller, kerl) is None
    assert views.live_panels(hub.controller, kerl) == []

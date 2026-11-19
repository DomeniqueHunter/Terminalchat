import json
from pathlib import Path

from fastapi.testclient import TestClient

from cursed_descent.models import Message
from cursed_descent.town_buildings import registry
from cursed_descent.view import Button, Panel
from cursed_descent.content import ITEMS
from cursed_descent.web import tools, views
from cursed_descent.web.app import create_app
from cursed_descent.web.hub import GameHub


def ask(socket, **data) -> str:
    socket.send_text(json.dumps(data))
    return socket.receive_text()


def test_connecting_sends_the_log_and_the_panels(data_path:Path) -> None:
    with TestClient(create_app(data_path, login=False)) as client:
        with client.websocket_connect("/ws") as socket:
            first = socket.receive_text()
    assert 'id="log"' in first and 'id="tab-character"' in first
    assert "id=\"viewer\"" in first and "kerl" in first.lower()


def test_selecting_a_viewer_shows_town_and_character(data_path:Path) -> None:
    with TestClient(create_app(data_path, login=False)) as client:
        with client.websocket_connect("/ws") as socket:
            socket.receive_text()
            page = ask(socket, action="select", viewer="kerl")
    assert "Last Light" in page and 'value="kerl" selected' in page
    assert "&quot;!bank&quot;" in page or '"text": "!bank"' in page


def test_the_bank_has_its_own_panel(data_path:Path) -> None:
    with TestClient(create_app(data_path, login=False)) as client:
        with client.websocket_connect("/ws") as socket:
            socket.receive_text()
            ask(socket, action="select", viewer="kerl")
            page = ask(socket, action="cmd", viewer="kerl", text="!bank")
    assert "&gt; kerl: !bank" in page
    assert "Inventory" in page and "Gold:" in page and "Items:" in page
    assert "Deposit 100" not in page and "← Town" in page


def test_a_counter_building_gets_its_buttons_from_its_offers(
        data_path:Path) -> None:
    hub = GameHub(data_path)
    kerl = hub.controller.repository.load("kerl")
    kerl.profile["town"] = "dusk_hollow"
    hub.controller.repository.save(kerl)
    hub.controller.handle("kerl", "!blood_bank")
    panel = registry.panel_for("blood_bank", hub.controller.town, kerl)
    assert panel.title.endswith("Blood Bank")
    assert [button.command for button in panel.buttons] == [
        "!blood_bank 1", "!blood_bank 2", "!blood_bank 3"]
    assert registry.panel_for("nowhere", hub.controller.town, kerl) is None


def test_a_command_without_a_character_is_refused(data_path:Path) -> None:
    with TestClient(create_app(data_path, login=False)) as client:
        with client.websocket_connect("/ws") as socket:
            socket.receive_text()
            page = ask(socket, action="cmd", viewer="", text="!status")
    assert "Select or create a character first." in page


def test_a_party_run_shows_combat_buttons_and_target_is_added(
        data_path:Path) -> None:
    with TestClient(create_app(data_path, login=False)) as client:
        with client.websocket_connect("/ws") as socket:
            socket.receive_text()
            ask(socket, action="cmd", viewer="kerl", text="!lobby")
            page = ask(socket, action="cmd", viewer="kerl", text="!start")
    assert "Force round" in page and "Cast" in page
    hub = GameHub.__new__(GameHub)
    assert hub.command_text({"text": "!hit", "target": "2"}) == "!hit 2"
    assert hub.command_text({"text": "!hit 1", "target": "2"}) == "!hit 1"
    assert hub.command_text({"text": "!cast", "spell": "fireball",
                             "target": "1"}) == "!cast fireball 1"
    assert hub.command_text({"text": "  hello "}) == "hello"


def test_log_text_is_escaped_and_marked(data_path:Path) -> None:
    hub = GameHub(data_path)
    entries = views.log_entries([
        Message("💀 It is over."), Message("🗺 Goblin Warrens: dark."),
        Message("<script>alert(1)</script>"),
        Message("secret", "kerl")])
    html = hub.log_html(entries)
    assert "&lt;script&gt;" in html and "<script>" not in html
    assert 'class="line death"' in html and 'class="line biome"' in html
    assert "→ kerl: secret" in html


def test_panels_render_nested_sections(data_path:Path) -> None:
    hub = GameHub(data_path)
    text = hub.render("nested.html", item=Panel(
        "Outer", ("line",), (Button("Go", "!go"),),
        (Panel("Inner", ("deep",)),)))
    assert "Outer" in text and "Inner" in text
    assert "deep" in text and "!go" in text


def test_the_page_has_the_tkinter_layout(data_path:Path) -> None:
    page = GameHub(data_path).page()
    for title in ("Party", "Profile", "Combat", "Encounter", "Hit enemy"):
        assert f"<legend>{title}</legend>" in page
    for tab in ("character", "party", "location", "inventory", "family",
                "contacts", "settings"):
        assert f'data-tab="{tab}"' in page
    for word in ("Acting as", "Make main", "Random party (4)", "Hire",
                 "Dismiss", "Autopilot on/off", "Auto time", "Light mode",
                 "Chat as selected"):
        assert word in page
    assert "Test tools" not in page
    assert "fireball" in page


def test_debug_adds_the_test_tools(data_path:Path) -> None:
    assert "Test tools" in GameHub(data_path, debug=True).page()


def test_slots_show_the_party_with_marker_and_star(data_path:Path) -> None:
    hub = GameHub(data_path)
    hub.controller.handle("kerl", "!lobby")
    rows = views.slot_rows(hub.controller, "kerl", "kerl")
    assert rows[0]["label"].startswith("1: ▶ kerl") and "★" in rows[0]["label"]
    assert rows[1]["label"] == "2: -" and rows[1]["name"] == ""


def test_the_right_tabs_are_filled_for_a_character(data_path:Path) -> None:
    with TestClient(create_app(data_path, login=False)) as client:
        with client.websocket_connect("/ws") as socket:
            socket.receive_text()
            page = ask(socket, action="select", viewer="kerl")
    assert "Stats –" in page and "Equipment" in page
    assert "Bag (" in page and "Family tree – kerl" in page
    assert "Friends" in page and "Last Light" in page


def test_hire_auto_and_potion_text_use_the_form_fields(
        data_path:Path) -> None:
    hub = GameHub(data_path)
    assert hub.command_text({"text": "!hire", "hire": "Mira"}) == "!hire Mira"
    assert hub.command_text({"text": "!dismiss",
                             "hire": "Mira"}) == "!dismiss Mira"
    assert hub.command_text({"text": "!auto", "viewer": "kerl"}) == "!auto kerl"
    kerl = hub.controller.repository.load("kerl")
    kerl.inventory = ["healing_potion"] if "healing_potion" in ITEMS else []
    assert hub.potion_text("nobody", "") == ""
    if kerl.inventory:
        assert hub.potion_text("kerl", "2") == "!use healing_potion 2"


def test_main_character_and_auto_time_are_hub_wide(data_path:Path) -> None:
    with TestClient(create_app(data_path, login=False)) as client:
        with client.websocket_connect("/ws") as socket:
            socket.receive_text()
            ask(socket, action="select", viewer="kerl")
            page = ask(socket, action="tool", viewer="kerl", tool="main")
            assert "main character now" in page and "kerl ★" in page
            page = ask(socket, action="tool", viewer="kerl",
                       tool="auto_time")
    assert "Auto time: off" in page


def test_login_preselects_the_main_character(data_path:Path) -> None:
    with TestClient(create_app(data_path, login=False)) as client:
        hub = client.app.state.hub
        with client.websocket_connect("/ws") as socket:
            socket.receive_text()
            assert hub.clients[0].viewer == ""
            ask(socket, action="select", viewer="kerl")
            ask(socket, action="tool", viewer="kerl", tool="main")
        with client.websocket_connect("/ws") as socket:
            socket.receive_text()
            assert hub.clients[-1].viewer == "kerl"


def test_test_tools_are_refused_without_debug(data_path:Path) -> None:
    with TestClient(create_app(data_path, login=False)) as client:
        with client.websocket_connect("/ws") as socket:
            socket.receive_text()
            ask(socket, action="select", viewer="kerl")
            socket.send_text(json.dumps({"action": "tool", "tool": "quick_start",
                                         "viewer": "kerl"}))
            page = ask(socket, action="cmd", viewer="kerl", text="!status")
    assert "Lobby" not in page.split("kerl: !status")[0]


def test_quick_start_and_everyone_hits_work_in_debug(data_path:Path) -> None:
    with TestClient(create_app(data_path, login=False, debug=True)) as client:
        with client.websocket_connect("/ws") as socket:
            socket.receive_text()
            page = ask(socket, action="tool", viewer="kerl",
                       tool="quick_start")
            assert "State: " in page
            page = ask(socket, action="tool", viewer="kerl",
                       tool="everyone_hits")
    assert "State: " in page


def test_encounter_buttons_and_hit_rows_follow_the_session(
        data_path:Path) -> None:
    hub = GameHub(data_path, debug=True)
    assert views.encounter_buttons(hub.controller, "kerl") == []
    assert views.hit_rows(hub.controller) == []
    tools.quick_start(hub.controller)
    rows = views.hit_rows(hub.controller)
    assert rows and {"uid", "name", "hp", "max_hp"} <= set(rows[0])


def test_hire_select_lists_own_maids_mercenaries_and_graduates(
        data_path:Path) -> None:
    from cursed_descent.models import Player
    hub = GameHub(data_path)
    repository = hub.controller.repository
    maid = Player(name="Maida", first_name="Maida", npc="maid")
    maid.profile = {"owner": "kerl"}
    other = Player(name="Maidb", first_name="Maidb", npc="maid")
    other.profile = {"owner": "somebody"}
    grad = Player(name="Maidc", first_name="Maidc", npc="maid")
    grad.profile = {"graduate": True}
    merc = Player(name="Hans", first_name="Hans", npc="mercenary")
    merc.profile = {"kind": "mercenary"}
    for npc in (maid, other, grad, merc):
        repository.add(npc)
    options = dict(views.hire_options(hub.controller, "kerl", ["galactica"]))
    assert options["galactica"] == "galactica"
    assert "your maid" in options["Maida"]
    assert "maid graduate" in options["Maidc"]
    assert "mercenary" in options["Hans"]
    assert "Maidb" not in options


def test_a_maid_hired_by_another_char_of_the_account_is_listed_and_free(
        data_path:Path) -> None:
    from cursed_descent.models import Player
    hub = GameHub(data_path)
    repository = hub.controller.repository
    maid = Player(name="Maida", first_name="Maida", npc="maid")
    maid.profile = {"owner": "galactica"}
    repository.add(maid)
    options = dict(views.hire_options(hub.controller, "kerl", []))
    assert "your maid" in options["Maida"]
    kerl = repository.load("kerl")
    from cursed_descent.npcs.hire import owns_maid
    assert owns_maid(repository, kerl, maid)

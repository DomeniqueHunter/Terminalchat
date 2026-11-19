import asyncio
from pathlib import Path

import pytest

from cursed_descent.config import REVIVE_PRICE
from cursed_descent.web import audience, views
from cursed_descent.web.hub import GameHub
from tests.test_web_log_scope import connect


STATIC = Path(views.__file__).parent / "static"


def test_observer_button_and_switch(data_path:Path) -> None:
    labels = [b.label for b in views.ambient_button("tavern", frozenset())]
    assert any("Watching others: on" in label for label in labels)
    off = views.ambient_button("tavern", frozenset({"witness"}))
    assert any("Watching others: off" in b.label for b in off)
    private = next(iter(views.PRIVATE_WHERE))
    assert views.ambient_button(private, frozenset()) == ()
    hub = GameHub(data_path)
    client = connect(hub, "kerl")
    seen = {"text": "Galactica waves.", "kind": "witness", "place": "tavern"}
    asyncio.run(hub.broadcast(audience.private("kerl", [seen])))
    assert "Galactica waves." in client.socket.sent[-1]
    asyncio.run(hub.handle(client, '{"action": "cmd", "viewer": "kerl", '
                                   '"text": "!ambient witness"}'))
    asyncio.run(hub.broadcast(audience.private("kerl", [
        {**seen, "text": "Galactica nods."}])))
    assert "Galactica nods." not in client.socket.sent[-1]


def test_family_form_builds_the_command_and_links_after_consent(
        data_path:Path) -> None:
    hub = GameHub(data_path)
    assert hub.command_text({"text": "!family mark", "fam_char": "Galactica",
                             "fam_role": "sister"}) == (
        "!family Galactica sister")
    assert hub.command_text({"text": "!family mark", "fam_char": "",
                             "fam_role": "sister"}) == ""
    controller = hub.controller
    controller.handle("kerl", "!family Galactica sister")
    asks = " ".join(m.text for m in controller.handle(
        "Galactica", "!family accept kerl"))
    assert "sister" in asks or "kerl" in asks.casefold()
    from cursed_descent.web.tabs import family_tab
    tab = family_tab(controller, controller.repository.load("kerl"))
    assert any(panel.title == "Your family" for panel in tab["panels"])


def labels_of(controller, name:str) -> list[str]:
    return [label for label, _ in views.party_buttons(controller, name)]


def test_party_menu_outside_lobby(controller) -> None:
    assert labels_of(controller, "Kerl") == [
        "Create Lobby", "Find Lobby", "Start"]
    assert dict(views.party_buttons(controller, "Kerl"))["Start"] == "!solo"


def test_party_menu_in_lobby_has_leave_retire_resume(controller) -> None:
    controller.handle("Kerl", "!lobby")
    assert labels_of(controller, "Kerl") == [
        "Start", "Leave", "Retire", "Resume"]
    controller.handle("Kerl", "!leave")
    assert labels_of(controller, "Kerl") == [
        "Create Lobby", "Find Lobby", "Start"]


def test_start_without_lobby_starts_a_solo_run(controller) -> None:
    controller.handle("Kerl", "!solo")
    assert controller.lobbies.of("Kerl") is not None
    assert controller.lobbies.of("Kerl").session.state != "lobby"
    assert labels_of(controller, "Kerl") == ["Leave", "Retire", "Resume"]


def test_dead_players_get_only_end_run_and_resume_now(controller) -> None:
    player = controller.repository.load("Kerl")
    player.records["cafe_lock"] = 1
    player.records["respawn_day"] = controller.town.world.day + 1
    controller.repository.save(player)
    assert labels_of(controller, "Kerl") == [
        "End run", f"Resume now {REVIVE_PRICE}"]
    assert dict(views.party_buttons(controller, "Kerl"))[
        f"Resume now {REVIVE_PRICE}"] == "!endrun pay"
    note = views.death_note(controller, "Kerl")
    assert "dead" in note and "minutes" in note
    assert views.death_note(controller, "Nobody") == ""


def hotkey_page(playwright, html:str):
    browser = playwright.chromium.launch()
    page = browser.new_page()
    page.set_content(html)
    page.evaluate("""() => {
        const make = (text, disabled, counter) => {
            const button = document.createElement("button");
            button.setAttribute("hx-vals", JSON.stringify({text}));
            button.disabled = disabled;
            button.onclick = () => { window[counter] = (window[counter] || 0) + 1; };
            document.body.appendChild(button);
        };
        make("!hit", false, "keyHit");
        make("!cast", true, "keyCast");
    }""")
    page.add_script_tag(path=str(STATIC / "app.js"))
    return browser, page


def test_combat_hotkeys_click_the_buttons(data_path:Path) -> None:
    import re
    html = re.sub(r"<script[^>]*src=[^>]*></script>", "",
                  GameHub(data_path).page())
    sync = pytest.importorskip("playwright.sync_api")
    try:
        with sync.sync_playwright() as playwright:
            browser, page = hotkey_page(playwright, html)
            page.keyboard.press("h")
            assert page.evaluate("window.keyHit") == 1
            page.keyboard.press("c")
            assert page.evaluate("window.keyCast") is None
            page.focus("#say-input")
            page.keyboard.type("hhh")
            assert page.evaluate("window.keyHit") == 1
            browser.close()
    except Exception as error:  # chromium missing in the test environment
        if "Executable doesn't exist" in str(error):
            pytest.skip("chromium is not installed")
        raise


def test_party_status_shows_names_and_hp_only_during_a_run(
        controller) -> None:
    assert views.party_rows(controller, "Kerl") == []
    controller.handle("Kerl", "!lobby")
    assert views.party_rows(controller, "Kerl") == []
    controller.handle("Kerl", "!start")
    rows = views.party_rows(controller, "Kerl")
    assert [row["name"].casefold() for row in rows] == ["kerl"]
    assert rows[0]["hp"] > 0 and rows[0]["max_hp"] >= rows[0]["hp"]
    assert rows[0]["you"] and rows[0]["alive"]

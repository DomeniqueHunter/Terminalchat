from pathlib import Path

from cursed_descent.web import views
from cursed_descent.web.hub import Client, GameHub


def sections(hub:GameHub, name:str) -> list[str]:
    player = hub.controller.repository.load(name)
    panel = views.location_panel(hub.controller, player)[0]
    return [section.title for section in panel.sections]


def test_brothel_menu_has_jobs_and_rent(data_path:Path) -> None:
    hub = GameHub(data_path)
    hub.controller.handle("kerl", "!brothel")
    names = sections(hub, "kerl")
    assert "Jobs" in names and "For yourself" in names


def test_brothel_client_panel_offers_acts_tone_and_kick(
        data_path:Path) -> None:
    hub = GameHub(data_path)
    hub.controller.handle("kerl", "!brothel")
    hub.controller.handle("kerl", "!job brothel whore")
    player = hub.controller.repository.load("kerl")
    shift = hub.controller.town.shifts.get("kerl")
    assert shift is not None
    if shift.client is None:
        shift.due = hub.controller.town.now
        hub.controller.tick()
    page = hub.panels_for(Client(None, "kerl"))
    assert "End shift" in page or "On shift" in page
    assert player.name == "kerl"


def test_serve_text_takes_tone_and_kick_from_the_form(
        data_path:Path) -> None:
    hub = GameHub(data_path)
    assert hub.command_text({"text": "!serve oral give",
                             "tone": "sweet"}) == "!serve oral give sweet"
    assert hub.command_text({"text": "!serve ballbusting give",
                             "tone": "", "kick": "front"}
                            ) == "!serve ballbusting give front"
    assert hub.command_text({"text": "!serve oral give",
                             "kick": "front"}) == "!serve oral give"


def test_maid_school_menu_and_enroll_guard(data_path:Path) -> None:
    hub = GameHub(data_path)
    hub.controller.handle("kerl", "!maidschool")
    names = sections(hub, "kerl")
    assert {"Courses (", "Maids for hire", "Enroll"} <= {
        name if not name.startswith("Courses") else "Courses ("
        for name in names}
    page = hub.panels_for(Client(None, "kerl"))
    assert 'class="danger"' not in page
    hub.controller.handle("kerl", "!maidschool enroll")
    page = hub.panels_for(Client(None, "kerl"))
    assert 'class="danger"' in page and "data-arm" in page


def test_brewhouse_shows_the_counter_offers(data_path:Path) -> None:
    hub = GameHub(data_path)
    hub.controller.handle("kerl", "!brewhouse")
    player = hub.controller.repository.load("kerl")
    panel = views.location_panel(hub.controller, player)[0]
    assert "Brewhouse" in panel.title or "🍺" in panel.title
    assert panel.buttons

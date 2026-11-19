from pathlib import Path

from cursed_descent.town_buildings.work import ui as work_ui
from cursed_descent.web import views
from cursed_descent.web.hub import Client, GameHub


def titles(hub:GameHub, name:str) -> list[str]:
    player = hub.controller.repository.load(name)
    panel = views.location_panel(hub.controller, player)[0]
    return [section.title for section in panel.sections]


def test_the_cafe_menu_depends_on_who_walks_in(data_path:Path) -> None:
    hub = GameHub(data_path)
    hub.controller.handle("kerl", "!cafe")
    hub.controller.handle("Beverley Morningwood", "!cafe")
    man = titles(hub, "kerl")
    lady = titles(hub, "Beverley Morningwood")
    assert "Jobs" in man and "Eat & drink" in man and "Take a seat" not in man
    assert "Take a seat" in lady and "Locals" in lady


def test_the_seat_job_shows_a_live_timer_and_actions(
        data_path:Path) -> None:
    hub = GameHub(data_path)
    hub.controller.handle("kerl", "!cafe")
    hub.controller.handle("kerl", "!job cafe seat")
    player = hub.controller.repository.load("kerl")
    parts = views.live_panels(hub.controller, player)
    assert parts and parts[0].title.startswith("Seat")
    assert parts[0].timer.startswith("Next guest")
    html = hub.render("live.html", parts=parts)
    assert 'id="timer"' in html and 'hx-swap-oob="true"' in html
    page = hub.panels_for(Client(None, "kerl"))
    assert "Hold breath" in page and "Quit (safeword)" in page


def test_jobs_and_orders_panels_use_the_building_commands(
        data_path:Path) -> None:
    hub = GameHub(data_path)
    player = hub.controller.repository.load("kerl")
    jobs = work_ui.jobs_panel("cafe", player)
    assert any(b.command == "!job cafe seat" for b in jobs.buttons)
    orders = work_ui.orders_panel("cafe", player)
    assert any(b.command == "!order cafe 1 take" for b in orders.buttons)

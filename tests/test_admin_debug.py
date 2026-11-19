from pathlib import Path

from cursed_descent.web.hub import GameHub


def test_debug_commands_need_debug_or_admin(data_path:Path) -> None:
    hub = GameHub(data_path)
    assert hub.controller.handle("kerl", "!events") == []
    hub.controller.is_admin = lambda name: name == "kerl"
    out = hub.controller.handle("kerl", "!events")
    assert out and out[0].text.startswith("Events:")
    assert hub.controller.handle("Galactica", "!events") == []


def test_admin_sees_teleport_buttons_at_the_station(data_path:Path) -> None:
    from cursed_descent.web import views
    hub = GameHub(data_path)
    controller = hub.controller
    controller.handle("kerl", "!station")
    player = controller.repository.load("kerl")

    def commands() -> list[str]:
        found = []
        for panel in views.location_panel(controller, player):
            for section in panel.sections:
                found += [b.command for b in section.buttons]
        return found

    assert not any(c.startswith("!teleport") for c in commands())
    controller.is_admin = lambda name: True
    assert any(c.startswith("!teleport ") for c in commands())
    controller.handle("kerl", "!teleport Dusk Hollow")
    assert controller.repository.load("kerl").profile["town"] == "dusk_hollow"

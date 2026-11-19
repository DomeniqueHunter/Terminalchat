from pathlib import Path

from cursed_descent.web import tabs
from cursed_descent.web.hub import GameHub


def test_request_needs_confirmation_and_shows_in_the_tab(
        data_path:Path) -> None:
    hub = GameHub(data_path)
    controller = hub.controller
    controller.handle("kerl", "!family Galactica son")
    lady = controller.repository.load("Galactica")
    assert not lady.profile.get("family")
    panels = tabs.family_tab(controller, lady)["panels"]
    assert panels[0].title == "Requests"
    assert panels[0].rows[0].buttons[0].command == "!family accept kerl"
    controller.handle("Galactica", "!family accept kerl")
    kerl = controller.repository.load("kerl")
    lady = controller.repository.load("Galactica")
    assert kerl.profile["family"][lady.id]["role"] == "son"
    assert not lady.profile.get("family_asks")


def test_decline_leaves_no_link(data_path:Path) -> None:
    hub = GameHub(data_path)
    controller = hub.controller
    controller.handle("kerl", "!family Galactica son")
    out = controller.handle("Galactica", "!family decline kerl")
    assert "decline" in out[0].text
    assert not controller.repository.load("kerl").profile.get("family")


def test_accept_without_request(data_path:Path) -> None:
    hub = GameHub(data_path)
    out = hub.controller.handle("Galactica", "!family accept kerl")
    assert "Nobody" in out[0].text


def test_the_form_builds_the_command(data_path:Path) -> None:
    hub = GameHub(data_path)
    data = {"text": "!family mark", "fam_char": "Galactica",
            "fam_role": "son"}
    assert hub.command_text(data) == "!family Galactica son"
    assert hub.command_text({"text": "!family mark"}) == ""

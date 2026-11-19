from pathlib import Path

from cursed_descent.web import tabs
from cursed_descent.web.hub import Client, GameHub
from cursed_descent.web.svg_canvas import SvgCanvas


def test_the_canvas_writes_basic_shapes() -> None:
    canvas = SvgCanvas(50, 60)
    canvas.create_oval(0, 0, 10, 20, fill="#fff", outline="")
    canvas.create_polygon([0, 0, 10, 0, 5, 9], fill="red", smooth=True)
    canvas.create_text(4, 4, text="a < b", anchor="nw", fill="#777",
                       font=("TkDefaultFont", 7))
    svg = canvas.svg()
    assert svg.startswith("<svg") and "<ellipse" in svg and "<path" in svg
    assert "a &lt; b" in svg
    canvas.delete("all")
    assert "<ellipse" not in canvas.svg()


def test_every_fixture_hero_gets_a_figure(data_path:Path) -> None:
    hub = GameHub(data_path)
    for name in hub.controller.repository.names():
        player = hub.controller.repository.load(name)
        if player.npc:
            continue
        assert "<ellipse" in tabs.figure_svg(player)


def test_the_character_tab_shows_the_figure_without_raw_tokens(
        data_path:Path) -> None:
    hub = GameHub(data_path)
    page = hub.panels_for(Client(None, "Beverley Morningwood"))
    assert 'class="portrait"' in page and "<svg" in page
    assert "<<npc." not in page

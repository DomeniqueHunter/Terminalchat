from datetime import datetime

from rich.style import Style
from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.events import Click
from textual.screen import ModalScreen
from textual.widgets import Static, TabbedContent, TabPane
from textual_image._terminal import probe_terminal

from animated_eicon import make_eicon_widget
from bbcode import INTERNAL_LINKS, to_text
from color_config import STATUS_STYLES, make_style
from eicons import AVATAR, THUMB, full_image_url, profile_url
from profile_api import KINK_CHOICES, Profile, ProfileError


THUMB_ROWS = 8
THUMB_COLUMNS = 5
GRID_GUTTER = 2
KINK_TITLES = {"fave": "Favorites", "yes": "Yes", "maybe": "Maybe", "no": "No"}


def fit_cells(pixels:tuple[int, int], max_columns:int, max_rows:int) -> tuple[int, int]:
    try:
        cell = probe_terminal().cell_size
        cell_width, cell_height = cell.width or 10, cell.height or 20
    except Exception:
        cell_width, cell_height = 10, 20
    width, height = max(pixels[0], 1), max(pixels[1], 1)
    scale = min(max_columns * cell_width / width, max_rows * cell_height / height)
    return max(1, round(width * scale / cell_width)), max(1, round(height * scale / cell_height))


def format_date(timestamp:int) -> str:
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d") if timestamp else "?"


class ProfileScreen(ModalScreen[None]):

    DEFAULT_CSS = """
    ProfileScreen {
        align: center middle;
    }
    ProfileScreen > Vertical {
        width: 90%;
        height: 90%;
        background: $panel;
        border: round $accent;
        border-title-align: center;
        border-subtitle-align: center;
        padding: 0 1;
    }
    ProfileScreen #profile_header {
        height: auto;
        margin-bottom: 1;
    }
    ProfileScreen #profile_header > .avatar {
        width: auto;
        margin-right: 2;
    }
    ProfileScreen #profile_info {
        width: 1fr;
    }
    ProfileScreen TabbedContent {
        height: 1fr;
    }
    ProfileScreen TabPane {
        padding: 0;
    }
    ProfileScreen #profile_images {
        layout: grid;
        grid-size: 5;
        grid-gutter: 1 2;
        height: auto;
    }
    ProfileScreen .image_cell {
        height: auto;
    }
    ProfileScreen .image_cell > Horizontal {
        height: 8;
        width: 1fr;
        align: center middle;
    }
    ProfileScreen .image_cell > Static {
        color: $text-muted;
        height: auto;
        max-height: 2;
        text-align: center;
    }
    ProfileScreen .kinks {
        height: auto;
    }
    ProfileScreen .kinks > Static {
        width: 1fr;
        padding-right: 2;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close", show=False),
        Binding("o", "open_web", "Copy profile link", show=False),
    ]

    def __init__(self, name:str) -> None:
        super().__init__()
        self.character = name
        self.images: list[tuple[str, str]] | None = None
        self.images_loaded = False

    def compose(self) -> ComposeResult:
        with Vertical() as box:
            box.border_title = f"Profile: {self.character}"
            box.border_subtitle = "o: copy profile link · esc: close · click names and links"
            with Horizontal(id="profile_header"):

                yield Static("Loading ...", id="profile_info")
            with TabbedContent(id="profile_tabs"):
                with TabPane("Info", id="tab_info"):
                    yield VerticalScroll(Static("", id="profile_infotags"))
                with TabPane("Description", id="tab_description"):
                    yield VerticalScroll(Static("", id="profile_description"))
                with TabPane("Kinks", id="tab_kinks"):
                    with VerticalScroll():
                        with Horizontal(classes="kinks"):
                            for choice in KINK_CHOICES:
                                yield Static("", id=f"kinks_{choice}")
                with TabPane("Images", id="tab_images"):
                    with VerticalScroll():
                        yield Static("", id="images_info")
                        yield Vertical(id="profile_images")

    def on_mount(self) -> None:
        self.run_worker(self.load_avatar(), group="avatar")
        self.run_worker(self.load_profile(), group="profile", exclusive=True)

    async def load_avatar(self) -> None:
        cache = getattr(self.app, "eicons", None)
        if cache is None:
            return
        image = await cache.get(self.character, AVATAR)
        if image is None or not self.is_attached:
            return
        widget = make_eicon_widget(image)
        widget.styles.height = 6
        widget.add_class("avatar")
        header = self.query_one("#profile_header", Horizontal)
        await header.mount(widget, before=self.query_one("#profile_info"))

    async def load_profile(self) -> None:
        api = getattr(self.app, "profile_api", None)
        info = self.query_one("#profile_info", Static)
        if api is None:
            info.update(Text("Profiles are only available while logged in", "bold red"))
            return
        try:
            profile = await api.profile(self.character)
        except ProfileError as error:
            info.update(Text.assemble((f"{self.character}\n", "bold"), (f"Could not load the profile: {error}", "red")))
            return
        if self.is_attached:
            self.show_profile(profile)

    def show_profile(self, profile:Profile) -> None:
        name = profile.name or self.character
        name_style = getattr(self.app, "name_style", lambda _: Style())
        info = Text()
        info.append(name, Style(bold=True) + name_style(name))
        if profile.title:
            info.append(f"  {profile.title}", "italic")
        status = self.app.client.presence.status_of(name) if hasattr(self.app, "client") else None
        info.append("\n")
        if status is None:
            info.append("offline", "dim")
        else:
            info.append(status[0], make_style(STATUS_STYLES.get(status[0], "")))
            if status[1]:
                info.append(": ")
                info.append_text(to_text(status[1], True, reveal_spoilers=True))
        info.append(f"\nCreated {format_date(profile.created)} · updated {format_date(profile.updated)} · {profile.views} views", "dim")
        url = profile_url(name)
        info.append("\n")
        info.append(url, Style(underline=True, link=url))
        self.query_one("#profile_info", Static).update(info)

        tags = Text()
        for group, entries in profile.infotags:
            if tags.plain:
                tags.append("\n\n")
            tags.append(group, "bold underline")
            width = max(len(label) for label, _ in entries) + 2
            for label, value in entries:
                tags.append(f"\n{label + ':':<{width}}", "dim")
                tags.append_text(to_text(value, True))
        self.query_one("#profile_infotags", Static).update(tags or Text("(no details)", "dim"))

        description = to_text(profile.description, True, name_style, True) if profile.description.strip() else Text("(no description)", "dim")
        self.query_one("#profile_description", Static).update(description)

        self.images = profile.images
        self.query_one("#profile_tabs", TabbedContent).get_tab("tab_images").label = f"Images ({len(profile.images)})"
        if self.query_one("#profile_tabs", TabbedContent).active == "tab_images":
            self.start_images()

        for choice in KINK_CHOICES:
            names = profile.kinks.get(choice, [])
            text = Text(f"{KINK_TITLES[choice]} ({len(names)})", "bold underline")
            for kink in names:
                text.append(f"\n{kink}")
            self.query_one(f"#kinks_{choice}", Static).update(text)

    def on_tabbed_content_tab_activated(self, event:TabbedContent.TabActivated) -> None:
        if event.pane.id == "tab_images":
            self.start_images()

    def start_images(self) -> None:
        if self.images is None or self.images_loaded:
            if self.images is None:
                self.query_one("#images_info", Static).update(Text("Loading ...", "dim"))
            return
        self.images_loaded = True
        if not self.images:
            self.query_one("#images_info", Static).update(Text("(no images)", "dim"))
            return
        self.query_one("#images_info", Static).update(Text("Click an image to copy the link to the full image", "dim"))
        self.run_worker(self.load_images(), group="images")

    async def load_images(self) -> None:
        cache = getattr(self.app, "eicons", None)
        grid = self.query_one("#profile_images", Vertical)
        for file_name, description in self.images or []:
            slot = Horizontal()
            cell = Vertical(slot, Static(Text(description or " ", "dim")), classes="image_cell")
            cell.link = full_image_url(file_name)
            await grid.mount(cell)
            image = await cache.get(file_name, THUMB) if cache is not None else None
            if not self.is_attached:
                return
            if image is None:
                await slot.mount(Static(Text(f"[{file_name}]", "dim")))
                continue
            columns, rows = fit_cells(image.frames[0].size, self.thumb_columns(grid), THUMB_ROWS)
            widget = make_eicon_widget(image)
            widget.styles.width = columns
            widget.styles.height = rows
            await slot.mount(widget)

    def thumb_columns(self, grid:Vertical) -> int:
        width = grid.size.width or self.size.width * 8 // 10
        return max(4, (width - GRID_GUTTER * (THUMB_COLUMNS - 1)) // THUMB_COLUMNS)

    def on_click(self, event:Click) -> None:
        link = event.style.link
        widget = event.widget
        while not link and widget is not None and widget is not self:
            link = getattr(widget, "link", None)
            widget = widget.parent
        if not link:
            return
        event.stop()
        if link.startswith(INTERNAL_LINKS):
            self.dismiss(None)
        self.app.open_link(link)

    def action_open_web(self) -> None:
        self.app.open_link(profile_url(self.character))

    def action_close(self) -> None:
        self.dismiss(None)


def main() -> None:
    print(format_date(0), format_date(1700000000))


if __name__ == "__main__":
    main()

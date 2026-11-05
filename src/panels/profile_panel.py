from datetime import datetime

from rich.style import Style
from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.events import Click
from textual.screen import ModalScreen
from textual.widgets import Static, TabbedContent, TabPane

from animated_eicon import make_eicon_widget
from bbcode import INTERNAL_LINKS, to_text
from color_config import STATUS_STYLES, make_style
from eicons import AVATAR, profile_url
from profile_api import KINK_CHOICES, Profile, ProfileError


KINK_TITLES = {"fave": "Favorites", "yes": "Yes", "maybe": "Maybe", "no": "No"}


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
        Binding("o", "open_web", "Open in browser", show=False),
    ]

    def __init__(self, name:str) -> None:
        super().__init__()
        self.character = name

    def compose(self) -> ComposeResult:
        with Vertical() as box:
            box.border_title = f"Profile: {self.character}"
            box.border_subtitle = "o: open in browser · esc: close · click names and links"
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

        for choice in KINK_CHOICES:
            names = profile.kinks.get(choice, [])
            text = Text(f"{KINK_TITLES[choice]} ({len(names)})", "bold underline")
            for kink in names:
                text.append(f"\n{kink}")
            self.query_one(f"#kinks_{choice}", Static).update(text)

    def on_click(self, event:Click) -> None:
        link = event.style.link
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

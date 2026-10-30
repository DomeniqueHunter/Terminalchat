from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Static


class InfoScreen(ModalScreen[None]):

    DEFAULT_CSS = """
    InfoScreen {
        align: center middle;
    }
    InfoScreen > Vertical {
        width: auto;
        max-width: 90%;
        height: auto;
        max-height: 90%;
        background: $panel;
        border: round $accent;
        border-title-align: center;
        border-subtitle-align: center;
        padding: 0 1;
    }
    InfoScreen VerticalScroll {
        width: auto;
        height: auto;
        max-height: 100%;
    }
    InfoScreen Static {
        width: auto;
    }
    """

    BINDINGS = [
        Binding("escape,q,enter", "close", "Close", show=False),
    ]

    def __init__(self, title:str, text:str) -> None:
        super().__init__()
        self.info_title = title
        self.text = text

    def compose(self) -> ComposeResult:
        with Vertical() as box:
            box.border_title = self.info_title
            box.border_subtitle = "esc to close"
            with VerticalScroll():
                yield Static(Text(self.text))

    def on_mount(self) -> None:
        self.query_one(VerticalScroll).focus()

    def action_close(self) -> None:
        self.dismiss(None)

    def on_click(self, event) -> None:
        if event.widget is self:
            self.dismiss(None)


def main() -> None:
    pass


if __name__ == "__main__":
    main()

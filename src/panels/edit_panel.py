from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.events import Key
from textual.screen import ModalScreen
from textual.widgets import Static, TextArea

from bbcode import to_text
from bbcode_area import BBCodeArea


class SingleLineArea(BBCodeArea):

    BINDINGS = [
        Binding("shift+enter,ctrl+enter,ctrl+j,alt+enter", "newline", show=False),
    ]

    def action_newline(self) -> None:
        start, end = self.selection
        self.replace("\n", start, end)

    async def _on_key(self, event:Key) -> None:
        if event.key == "enter":
            event.stop()
            event.prevent_default()
            self.screen.action_save()


class EditScreen(ModalScreen[str | None]):

    DEFAULT_CSS = """
    EditScreen {
        align: center middle;
    }
    EditScreen > Vertical {
        width: 80%;
        max-width: 100;
        height: auto;
        background: $panel;
        border: round $accent;
        border-title-align: center;
        border-subtitle-align: center;
        padding: 0 1;
    }
    EditScreen SingleLineArea {
        height: 6;
    }
    EditScreen .label {
        color: $text-muted;
    }
    EditScreen #edit_counter {
        text-align: right;
        color: $text-muted;
    }
    EditScreen #edit_preview {
        height: auto;
        max-height: 6;
        padding: 0 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", show=False),
    ]

    def __init__(self, title:str, text:str, max_length:int) -> None:
        super().__init__()
        self.edit_title = title
        self.initial = text
        self.max_length = max_length

    def compose(self) -> ComposeResult:
        with Vertical() as box:
            box.border_title = self.edit_title
            box.border_subtitle = "enter: save · ctrl+enter: new line · esc: cancel · empty clears"
            yield SingleLineArea(self.initial, soft_wrap=True, show_line_numbers=False, id="edit_text")
            yield Static("", id="edit_counter")
            yield Static("Preview:", classes="label")
            yield Static("", id="edit_preview")

    def on_mount(self) -> None:
        area = self.query_one("#edit_text", SingleLineArea)
        area.move_cursor(area.document.end)
        area.focus()
        self.refresh_info(area.text)

    def on_text_area_changed(self, event:TextArea.Changed) -> None:
        self.refresh_info(event.text_area.text)

    def refresh_info(self, text:str) -> None:
        length = len(text.strip())
        self.query_one("#edit_counter", Static).update(
            Text(f"{length} / {self.max_length}", "bold red" if length > self.max_length else ""))
        preview = to_text(text.strip(), True, reveal_spoilers=True) if text.strip() else Text("(no status message)", "dim")
        self.query_one("#edit_preview", Static).update(preview)

    def action_save(self) -> None:
        text = self.query_one("#edit_text", SingleLineArea).text.strip()
        if len(text) > self.max_length:
            self.app.notify(f"Too long ({len(text)}/{self.max_length})", severity="warning")
            return
        self.dismiss(text)

    def action_cancel(self) -> None:
        self.dismiss(None)


def main() -> None:
    pass


if __name__ == "__main__":
    main()

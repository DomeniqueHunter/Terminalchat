from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, OptionList
from textual.widgets.option_list import Option

from bbcode import to_text
from bbcode_area import CURSOR
from color_config import BBCODE_COLORS


SAMPLE = "text"

BBCODE_PATTERNS = [
    ("[b]{}[/b]", "bold (alt+b)"),
    ("[i]{}[/i]", "italic (alt+i)"),
    ("[u]{}[/u]", "underline (alt+u)"),
    ("[s]{}[/s]", "strike through (alt+s)"),
    ("[sup]{}[/sup]", "superscript"),
    ("[sub]{}[/sub]", "subscript"),
    ("[big]{}[/big]", "big text"),
    ("[small]{}[/small]", "small text"),
    ("[heading]{}[/heading]", "heading"),
    *[(f"[color={name}]{{}}[/color]", f"{name} text") for name in BBCODE_COLORS],
    ("[user]{}[/user]", "link to a character, click opens a private chat"),
    ("[icon]{}[/icon]", "avatar of a character, links to the profile"),
    ("[eicon]{}[/eicon]", "eicon (animated image) by name"),
    ("[url]{}[/url]", "link, the text is the address"),
    ("[url=https://]{}[/url]", "link with its own text"),
    ("[session=Title]{}[/session]", "channel invite, put the channel code inside"),
    ("[spoiler]{}[/spoiler]", "hidden until clicked (alt+p)"),
    ("[quote]{}[/quote]", "quote (alt+q)"),
    ("[quote=Name]{}[/quote]", "quote with author"),
    ("[noparse]{}[/noparse]", "show BBCode as plain text"),
    ("[collapse=Title]{}[/collapse]", "collapsible block (web client)"),
    ("[center]{}[/center]", "centered (web client)"),
    ("[indent]{}[/indent]", "indented (web client)"),
    ("[hr]", "horizontal line"),
]

PREVIEW_TEXT = {"[user]{}[/user]": "Name", "[icon]{}[/icon]": "Name", "[eicon]{}[/eicon]": "name",
                "[url]{}[/url]": "https://f-list.net", "[session=Title]{}[/session]": "ADH-..."}


def preview(template:str) -> Text:
    sample = PREVIEW_TEXT.get(template, SAMPLE)
    return to_text(template.replace(CURSOR, sample), True, reveal_spoilers=False)


def display(template:str) -> str:
    return template.replace(CURSOR, "\u2026")


class BBCodeScreen(ModalScreen[str | None]):

    DEFAULT_CSS = """
    BBCodeScreen {
        align: center middle;
    }
    BBCodeScreen > Vertical {
        width: 90;
        max-width: 95%;
        height: auto;
        max-height: 90%;
        background: $panel;
        border: round $accent;
        border-title-align: center;
        border-subtitle-align: center;
        padding: 0 1;
    }
    BBCodeScreen OptionList {
        height: 20;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", show=False),
        Binding("down", "move(1)", show=False),
        Binding("up", "move(-1)", show=False),
        Binding("pagedown", "move(10)", show=False),
        Binding("pageup", "move(-10)", show=False),
    ]

    def __init__(self, query:str="") -> None:
        super().__init__()
        self.query_text = query
        self.shown: list[str] = []

    def compose(self) -> ComposeResult:
        with Vertical() as box:
            box.border_title = "BBCode"
            box.border_subtitle = "type to search · enter: insert (wraps selected text) · esc: close"
            yield Input(value=self.query_text, placeholder="search, e.g. color, link, quote", id="bbcode_search")
            yield OptionList(id="bbcode_list")

    def on_mount(self) -> None:
        self.update_list(self.query_text)
        self.query_one("#bbcode_search", Input).focus()

    def on_input_changed(self, event:Input.Changed) -> None:
        self.update_list(event.value)

    def update_list(self, query:str) -> None:
        words = query.lower().split()
        matches = [(template, description) for template, description in BBCODE_PATTERNS
                   if all(word in f"{template} {description}".lower() for word in words)]
        self.shown = [template for template, _ in matches]
        width = max((len(display(template)) for template, _ in BBCODE_PATTERNS), default=0) + 2
        options = []
        for template, description in matches:
            label = Text(display(template).ljust(width))
            label.append_text(preview(template))
            label.append(f"  {description}", "dim")
            options.append(Option(label))
        option_list = self.query_one("#bbcode_list", OptionList)
        option_list.clear_options()
        option_list.add_options(options)
        if options:
            option_list.highlighted = 0

    def action_move(self, step:int) -> None:
        option_list = self.query_one("#bbcode_list", OptionList)
        if self.shown:
            current = option_list.highlighted or 0
            option_list.highlighted = max(0, min(len(self.shown) - 1, current + step))

    def on_input_submitted(self, event:Input.Submitted) -> None:
        index = self.query_one("#bbcode_list", OptionList).highlighted
        if index is not None and index < len(self.shown):
            self.dismiss(self.shown[index])

    def on_option_list_option_selected(self, event:OptionList.OptionSelected) -> None:
        self.dismiss(self.shown[event.option_index])

    def action_cancel(self) -> None:
        self.dismiss(None)


def main() -> None:
    for template, description in BBCODE_PATTERNS:
        print(f"{template:<32} {preview(template).plain:<20} {description}")


if __name__ == "__main__":
    main()

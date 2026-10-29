import os

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.content import Content
from textual.css.query import NoMatches
from textual.dom import NoScreen
from textual.events import Click
from textual.suggester import SuggestFromList
from textual.widgets import Header, Input, Static
from textual.widgets._header import HeaderTitle

from animated_eicon import make_eicon_widget
from bbcode import to_text
from chat_commands import COMMAND_NAMES, command_usage, matching_commands
from chat_store import render_line, split_line
from color_config import EICON_STYLE, NameStyle, make_style
from eicons import MAX_PER_MESSAGE, EiconCache, extract_eicons


class ChatLine(Vertical):

    DEFAULT_CSS = """
    ChatLine {
        height: auto;
    }
    ChatLine > .eicons {
        height: auto;
        width: 1fr;
    }
    ChatLine SixelEicon, ChatLine GenericEicon {
        width: auto;
    }
    ChatLine .missing {
        width: auto;
        margin-right: 1;
    }
    """

    def __init__(self, line:str, eicons:EiconCache | None=None, eicon_height:int=4,
                 name_style:NameStyle | None=None) -> None:
        super().__init__()
        self.name_style = name_style
        self.line = line
        self.eicons = eicons
        self.eicon_height = eicon_height
        self.rows: list[tuple[Horizontal, list[str]]] = []

    def compose(self) -> ComposeResult:
        if self.eicons is None or not extract_eicons(self.line):
            yield Static(render_line(self.line, self.eicons is None, self.name_style))
            return

        header, message = split_line(self.line, self.name_style)
        remaining = MAX_PER_MESSAGE
        for index, part in enumerate(message.split("\n")):
            text = to_text(part, False, self.name_style)
            if index == 0:
                yield Static(Text.assemble(header, text))
            elif text.plain.strip():
                yield Static(text)

            names = extract_eicons(part)[:remaining]
            remaining -= len(names)
            if names:
                row = Horizontal(classes="eicons")
                self.rows.append((row, names))
                yield row

    def on_mount(self) -> None:
        for row, names in self.rows:
            self.run_worker(self.load_row(row, names))

    async def load_row(self, row:Horizontal, names:list[str]) -> None:
        widgets = []
        for name in names:
            eicon = await self.eicons.get(name)
            if eicon is None:
                widgets.append(Static(Text(f":{name}:", make_style(EICON_STYLE)), classes="missing"))
                continue
            widget = make_eicon_widget(eicon)
            widget.styles.height = self.eicon_height
            widgets.append(widget)

        view = self.parent if isinstance(self.parent, VerticalScroll) else None
        at_end = view is not None and view.scroll_y >= view.max_scroll_y - 1
        await row.mount_all(widgets)
        if at_end:
            view.call_after_refresh(view.scroll_end, animate=False)


class HistoryInput(Input):

    BINDINGS = [
        Binding("up", "history_prev", show=False),
        Binding("down", "history_next", show=False),
        Binding("tab", "complete", show=False),
    ]

    def __init__(self, *args:object, max_history:int=100, **kwargs:object) -> None:
        suggester = SuggestFromList([f"/{name}" for name in COMMAND_NAMES], case_sensitive=False)
        super().__init__(*args, suggester=suggester, **kwargs)
        self.max_history = max_history
        self.history: list[str] = []
        self.position: int | None = None
        self.draft = ""

    def remember(self, text:str) -> None:
        if text and (not self.history or self.history[-1] != text):
            self.history.append(text)
            del self.history[:-self.max_history]
        self.position = None
        self.draft = ""

    def set_text(self, text:str) -> None:
        self.value = text
        self.cursor_position = len(text)

    def action_history_prev(self) -> None:
        if not self.history:
            return
        if self.position is None:
            self.draft = self.value
            self.position = len(self.history)
        if self.position > 0:
            self.position -= 1
            self.set_text(self.history[self.position])

    def action_history_next(self) -> None:
        if self.position is None:
            return
        self.position += 1
        if self.position >= len(self.history):
            self.position = None
            self.set_text(self.draft)
        else:
            self.set_text(self.history[self.position])

    def action_complete(self) -> None:
        if not self.value.startswith("/") or " " in self.value:
            self.app.action_focus_next()
            return
        names = [name for name, _, _ in matching_commands(self.value[1:])]
        if not names:
            return
        completion = names[0] + " " if len(names) == 1 else os.path.commonprefix(names)
        if len(completion) >= len(self.value) - 1:
            self.set_text("/" + completion)


class StatusHeader(Header):

    DEFAULT_CSS = """
    StatusHeader HeaderTitle {
        text-align: center;
    }
    """

    def _on_click(self, event:Click) -> None:
        event.prevent_default()
        self.toggle_class("-tall")
        self.refresh_title()

    def refresh_title(self) -> None:
        try:
            self.query_one(HeaderTitle).update(self.format_title())
        except (NoScreen, NoMatches):
            pass

    def format_title(self) -> Content:
        title = super().format_title()
        if not self.has_class("-tall"):
            return title
        status_message = getattr(self.app, "status_message", None)
        message = status_message() if status_message else ""
        if not message:
            return Content.assemble(title, "\n", Content("(no status message)").stylize("dim"))
        return Content.assemble(title, "\n", Content.from_rich_text(to_text(message, False)))


MAX_HINTS = 12


class CommandHints(Static):

    DEFAULT_CSS = """
    CommandHints {
        height: auto;
        max-height: 12;
        padding: 0 1;
        background: $panel;
        color: $text-muted;
        display: none;
    }
    """

    def show_for(self, value:str) -> None:
        if not value.startswith("/") or " " in value:
            self.display = False
            return
        typed = value[1:].lower()
        matches = matching_commands(typed)
        if not matches:
            self.display = False
            return
        hidden = len(matches) - MAX_HINTS + 1 if len(matches) > MAX_HINTS else 0
        shown = matches[:len(matches) - hidden] if hidden else matches
        width = max(len(command_usage(name, args)) for name, args, _ in shown) + 2
        text = Text()
        for index, (name, args, description) in enumerate(shown):
            usage = command_usage(name, args)
            if index:
                text.append("\n")
            text.append("/" + name[:len(typed)], "bold")
            text.append(name[len(typed):] + usage[len(name) + 1:])
            text.append(" " * (width - len(usage)))
            text.append(description, "dim")
        if hidden:
            text.append(f"\n... {hidden} more, keep typing", "dim italic")
        self.update(text)
        self.display = True


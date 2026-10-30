import os
import re
from dataclasses import dataclass
from typing import Callable

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.content import Content
from textual.css.query import NoMatches
from textual.dom import NoScreen
from textual.events import Click, Key
from textual.message import Message
from textual.widgets import Header, Static, TextArea
from textual.widgets._header import HeaderTitle

from animated_eicon import make_eicon_widget
from bbcode import to_text
from chat_commands import command_usage, matching_commands
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

    def on_click(self, event:Click) -> None:
        link = event.style.link
        open_link = getattr(self.app, "open_link", None)
        if link and open_link is not None:
            event.stop()
            open_link(link)

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


NAME_WORDS = 3


@dataclass
class NameCompletion:
    row: int
    start: int
    names: list[str]
    index: int
    text: str
    location: tuple[int, int]


class ChatInput(TextArea):

    DEFAULT_CSS = """
    ChatInput {
        height: 5;
    }
    """

    BINDINGS = [
        Binding("up", "history_prev", show=False),
        Binding("down", "history_next", show=False),
        Binding("tab", "complete", show=False),
        Binding("shift+tab", "complete_back", show=False),
        Binding("shift+enter,ctrl+enter,ctrl+j,alt+enter", "newline", show=False),
    ]

    class Submitted(Message):

        def __init__(self, chat_input:"ChatInput", value:str) -> None:
            super().__init__()
            self.chat_input = chat_input
            self.value = value

        @property
        def control(self) -> "ChatInput":
            return self.chat_input

    def __init__(self, *, placeholder:str="", id:str | None=None, max_history:int=100) -> None:
        super().__init__(id=id, soft_wrap=True, show_line_numbers=False, placeholder=placeholder)
        self.max_history = max_history
        self.sent_history: list[str] = []
        self.history_position: int | None = None
        self.draft = ""
        self.history_enabled = True
        self.name_source: Callable[[str], list[str]] | None = None
        self.name_completion: NameCompletion | None = None

    @property
    def value(self) -> str:
        return self.text

    @value.setter
    def value(self, text:str) -> None:
        self.set_text(text)

    def set_text(self, text:str) -> None:
        self.text = text
        self.move_cursor(self.document.end)

    async def _on_key(self, event:Key) -> None:
        if event.key == "enter":
            event.stop()
            event.prevent_default()
            self.post_message(self.Submitted(self, self.text))

    def action_newline(self) -> None:
        start, end = self.selection
        self.replace("\n", start, end)

    def remember(self, text:str) -> None:
        if text and (not self.sent_history or self.sent_history[-1] != text):
            self.sent_history.append(text)
            del self.sent_history[:-self.max_history]
        self.history_position = None
        self.draft = ""

    def action_history_prev(self) -> None:
        if self.cursor_location[0] > 0:
            self.action_cursor_up()
            return
        if not self.sent_history or not self.history_enabled:
            return
        if self.history_position is None:
            self.draft = self.text
            self.history_position = len(self.sent_history)
        if self.history_position > 0:
            self.history_position -= 1
            self.set_text(self.sent_history[self.history_position])

    def action_history_next(self) -> None:
        if self.cursor_location[0] < self.document.line_count - 1:
            self.action_cursor_down()
            return
        if self.history_position is None or not self.history_enabled:
            return
        self.history_position += 1
        if self.history_position >= len(self.sent_history):
            self.history_position = None
            self.set_text(self.draft)
        else:
            self.set_text(self.sent_history[self.history_position])

    def is_command_word(self) -> bool:
        return self.text.startswith("/") and " " not in self.text and "\n" not in self.text

    def action_complete(self) -> None:
        if self.is_command_word():
            self.complete_command()
        elif not self.text:
            self.app.action_focus_next()
        else:
            self.complete_name(1)

    def action_complete_back(self) -> None:
        if self.is_command_word() or not self.text:
            self.app.action_focus_previous()
        else:
            self.complete_name(-1)

    def find_names(self, before:str) -> tuple[int, list[str]] | None:
        if self.name_source is None:
            return None
        for count in range(NAME_WORDS, 0, -1):
            match = re.search(r"(?:\S+\s+){%d}\S+$" % (count - 1), before)
            if match is None:
                continue
            names = self.name_source(match.group(0))
            if names:
                return match.start(), names
        return None

    def complete_name(self, step:int) -> None:
        state = self.name_completion
        if state is not None and state.text == self.text and state.location == self.cursor_location:
            state.index = (state.index + step) % len(state.names)
        else:
            row, column = self.cursor_location
            found = self.find_names(self.document.get_line(row)[:column])
            if found is None:
                self.name_completion = None
                return
            start, names = found
            state = NameCompletion(row, start, names, 0 if step > 0 else len(names) - 1, "", (row, column))
        name = state.names[state.index]
        insert = name if self.text.startswith("/") else f"[user]{name}[/user]"
        result = self.replace(insert, (state.row, state.start), state.location)
        self.move_cursor(result.end_location)
        state.text = self.text
        state.location = self.cursor_location
        self.name_completion = state
        if len(state.names) > 1:
            self.app.notify(f"{state.index + 1}/{len(state.names)}: {name}", timeout=2)

    def complete_command(self) -> None:
        names = [name for name, _, _ in matching_commands(self.text[1:])]
        if not names:
            return
        completion = names[0] + " " if len(names) == 1 else os.path.commonprefix(names)
        if len(completion) >= len(self.text) - 1:
            self.set_text("/" + completion)


class InputModeBar(Horizontal):

    DEFAULT_CSS = """
    InputModeBar {
        height: 1;
    }
    InputModeBar #input_info {
        width: 1fr;
        text-align: right;
        color: $text-muted;
    }
    InputModeBar .mode {
        width: auto;
        margin-left: 1;
        padding: 0 1;
    }
    InputModeBar .mode.-active {
        text-style: bold reverse;
    }
    """

    class ModeSelected(Message):

        def __init__(self, mode:str) -> None:
            super().__init__()
            self.mode = mode

    def compose(self) -> ComposeResult:
        yield Static("", id="input_info")
        yield Static("Chat", id="mode_chat", classes="mode")
        yield Static("Ads", id="mode_ads", classes="mode")

    def on_click(self, event:Click) -> None:
        if event.widget is not None and event.widget.id in ("mode_chat", "mode_ads"):
            event.stop()
            self.post_message(self.ModeSelected(event.widget.id[5:]))

    def show(self, info:Text | str, mode:str, ads_possible:bool) -> None:
        self.query_one("#input_info", Static).update(info)
        for name in ("chat", "ads"):
            button = self.query_one(f"#mode_{name}", Static)
            button.display = ads_possible
            button.set_class(name == mode, "-active")


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


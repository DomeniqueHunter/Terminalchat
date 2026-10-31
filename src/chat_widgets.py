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
from textual.widget import Widget
from textual.widgets import Header, Static, TextArea
from textual.widgets._header import HeaderTitle

from animated_eicon import make_eicon_widget
from bbcode import SPOILER_LINK, to_text
from bbcode_area import BBCodeArea
from chat_commands import COMMAND_ALIASES, COMMAND_INFO, NAME_COMMANDS, command_usage, matching_commands
from chat_store import join_header, render_line, split_line
from color_config import EICON_STYLE, ICON_STYLE, NameStyle, make_style
from eicons import AVATAR, IMAGE_PATTERN, MAX_PER_MESSAGE, EiconCache, extract_images, profile_url


INLINE_MARKER = "\ue000"
INLINE_TEXT_LIMIT = 60


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
    ChatLine > .inline {
        height: auto;
        width: 1fr;
    }
    ChatLine > .inline > Static {
        width: auto;
        content-align-vertical: middle;
    }
    ChatLine > .inline > .rest {
        width: 1fr;
    }
    ChatLine .slot {
        width: 0;
        height: 0;
    }
    """

    def __init__(self, line:str, eicons:EiconCache | None=None, eicon_height:int=4,
                 name_style:NameStyle | None=None) -> None:
        super().__init__()
        self.name_style = name_style
        self.line = line
        self.eicons = eicons
        self.eicon_height = eicon_height
        self.rows: list[tuple[Widget, list[tuple[str, str]]]] = []
        self.reveal_spoilers = False

    def compose(self) -> ComposeResult:
        if self.eicons is None or not extract_images(self.line):
            yield Static(render_line(self.line, self.eicons is None, self.name_style, self.reveal_spoilers))
            return

        header, message = split_line(self.line, self.name_style)
        remaining = MAX_PER_MESSAGE
        for index, part in enumerate(message.split("\n")):
            line_header = header if index == 0 else Text()
            images = extract_images(part)
            pieces = self.inline_pieces(part, line_header, images) if len(images) <= remaining else None
            if pieces is not None:
                remaining -= len(images)
                yield self.inline_row(pieces, images)
                continue

            text = to_text(part, False, self.name_style, self.reveal_spoilers)
            if index == 0:
                yield Static(join_header(header, text))
            elif text.plain.strip():
                yield Static(text)

            images = images[:remaining]
            remaining -= len(images)
            if images:
                row = Horizontal(classes="eicons")
                self.rows.append((row, images))
                yield row

    def inline_pieces(self, part:str, header:Text, images:list[tuple[str, str]]) -> list[Text] | None:
        if not images or "[noparse]" in part.lower():
            return None
        marked = IMAGE_PATTERN.sub(INLINE_MARKER, part)
        pieces = to_text(marked, False, self.name_style, self.reveal_spoilers).split(INLINE_MARKER, allow_blank=True)
        if len(pieces) != len(images) + 1 or any("\n" in piece.plain for piece in pieces):
            return None
        if not any(piece.plain.strip() for piece in pieces):
            return None
        if len(header.plain) + sum(len(piece.plain) for piece in pieces[:-1]) > INLINE_TEXT_LIMIT:
            return None
        pieces[0] = Text.assemble(header, pieces[0])
        return pieces

    def inline_row(self, pieces:list[Text], images:list[tuple[str, str]]) -> Horizontal:
        children = []
        for piece in pieces[:-1]:
            if piece.plain:
                text = Static(piece)
                text.styles.height = self.eicon_height
                children.append(text)
            children.append(Static("", classes="slot"))
        rest = Static(pieces[-1], classes="rest")
        rest.styles.min_height = self.eicon_height
        children.append(rest)
        row = Horizontal(*children, classes="inline")
        self.rows.append((row, images))
        return row

    async def on_click(self, event:Click) -> None:
        link = event.style.link
        widget = event.widget
        while not link and widget is not None and widget is not self:
            link = getattr(widget, "link", None)
            widget = widget.parent
        if not link:
            return
        event.stop()
        if link == SPOILER_LINK:
            self.reveal_spoilers = True
            self.rows = []
            await self.recompose()
            self.on_mount()
            return
        open_link = getattr(self.app, "open_link", None)
        if open_link is not None:
            open_link(link)

    def on_mount(self) -> None:
        for row, images in self.rows:
            self.run_worker(self.load_row(row, images))

    async def load_row(self, row:Widget, images:list[tuple[str, str]]) -> None:
        widgets = []
        for kind, name in images:
            image = await self.eicons.get(name, kind)
            link = profile_url(name) if kind == AVATAR else None
            if image is None:
                label = f"[{name}]" if kind == AVATAR else f":{name}:"
                style = make_style(ICON_STYLE if kind == AVATAR else EICON_STYLE)
                widget = Static(Text(label, style), classes="missing")
            else:
                widget = make_eicon_widget(image)
                widget.styles.height = self.eicon_height
            if link:
                widget.link = link
                widget.tooltip = f"{name} - click to open the profile"
            widgets.append(widget)

        view = self.parent if isinstance(self.parent, VerticalScroll) else None
        at_end = view is not None and view.scroll_y >= view.max_scroll_y - 1
        if row.has_class("inline"):
            slots = list(row.query(".slot"))
            for widget, slot in zip(widgets, slots):
                await row.mount(widget, before=slot)
            await row.remove_children(slots)
        else:
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


class ChatInput(BBCodeArea):

    DEFAULT_CSS = """
    ChatInput {
        height: 5;
    }
    """

    BINDINGS = [
        Binding("up", "history_prev", show=False),
        Binding("down", "history_next", show=False),
        Binding("tab", "complete", show=False),
        Binding("ctrl+tab,shift+tab", "complete_back", show=False),
        Binding("shift+enter,ctrl+enter,ctrl+j,alt+enter", "newline", show=False),
        Binding("ctrl+c", "copy_or_clear", show=False),
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

    def action_copy_or_clear(self) -> None:
        if self.selected_text:
            self.action_copy()
            return
        self.clear()
        self.history_position = None
        self.name_completion = None

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

    def in_name_command(self) -> bool:
        if not self.text.startswith("/"):
            return False
        command = re.split(r"\s", self.text[1:], maxsplit=1)[0].lower()
        return COMMAND_ALIASES.get(command, command) in NAME_COMMANDS

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
        insert = name if self.in_name_command() else f"[user]{name}[/user]"
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
        if not value.startswith("/"):
            self.display = False
            return
        if " " in value or "\n" in value:
            self.show_usage(re.split(r"\s", value[1:], maxsplit=1)[0].lower())
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

    def show_usage(self, name:str) -> None:
        name = COMMAND_ALIASES.get(name, name)
        entry = next((entry for entry in COMMAND_INFO if entry[0] == name), None)
        if entry is None:
            self.display = False
            return
        name, args, description = entry
        text = Text()
        text.append("/" + name, "bold")
        text.append((" " + args) if args else "")
        text.append("  " + description, "dim")
        self.update(text)
        self.display = True

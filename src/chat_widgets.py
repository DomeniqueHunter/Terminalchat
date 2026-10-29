from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Static

from animated_eicon import make_eicon_widget
from bbcode import to_text
from chat_store import render_line, split_line
from color_config import EICON_STYLE, make_style
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

    def __init__(self, line:str, eicons:EiconCache | None=None, eicon_height:int=4) -> None:
        super().__init__()
        self.line = line
        self.eicons = eicons
        self.eicon_height = eicon_height
        self.rows: list[tuple[Horizontal, list[str]]] = []

    def compose(self) -> ComposeResult:
        if self.eicons is None or not extract_eicons(self.line):
            yield Static(render_line(self.line, show_eicons=self.eicons is None))
            return

        header, message = split_line(self.line)
        remaining = MAX_PER_MESSAGE
        for index, part in enumerate(message.split("\n")):
            text = to_text(part, show_eicons=False)
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

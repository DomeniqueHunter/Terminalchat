from rich.style import Style
from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import OptionList, TabbedContent, TabPane
from textual.widgets.option_list import Option

from color_config import OP_STYLE, STATUS_STYLES, STATUS_SYMBOLS, NameStyle, make_style, no_name_style


Entry = tuple[str, str, bool]


def render_entry(name:str, status:str, is_op:bool, name_style:NameStyle) -> Text:
    symbol = STATUS_SYMBOLS.get(status, STATUS_SYMBOLS["online"])
    style = STATUS_STYLES.get(status, STATUS_STYLES["online"])
    text = Text.assemble((symbol, make_style(style)), " ")
    if is_op:
        text.append("@", make_style(OP_STYLE))
    base = make_style(OP_STYLE) if is_op else Style()
    text.append(name, base + name_style(name))
    return text


class Sidebar(Vertical):

    DEFAULT_CSS = """
    Sidebar {
        width: 32;
        border: solid magenta;
    }
    Sidebar TabbedContent {
        height: 1fr;
    }
    Sidebar TabPane {
        padding: 0;
        height: 1fr;
    }
    Sidebar OptionList, Sidebar OptionList:focus {
        height: 1fr;
        border: none;
        padding: 0;
    }
    """

    def __init__(self, **kwargs:object) -> None:
        super().__init__(**kwargs)
        self.shown: dict[str, tuple] = {}
        self.name_style: NameStyle = no_name_style

    def compose(self) -> ComposeResult:
        with TabbedContent(id="sidebar_tabs"):
            with TabPane("Friends", id="tab_friends"):
                yield OptionList(id="friends_list")
            with TabPane("Channel", id="tab_channel"):
                yield OptionList(id="members_list")

    def show_tab(self, tab_id:str) -> None:
        self.query_one(TabbedContent).active = tab_id

    def update_list(self, list_id:str, tab_id:str, label:str, entries:list[Entry], empty:str) -> None:
        key = (label, tuple(entries), empty)
        if self.shown.get(list_id) == key:
            return
        self.shown[list_id] = key

        view = self.query_one(f"#{list_id}", OptionList)
        scroll_y = view.scroll_y
        highlighted = view.highlighted_option.id if view.highlighted_option else None

        view.clear_options()
        if entries:
            view.add_options([Option(render_entry(*entry, self.name_style), id=entry[0]) for entry in entries])
            names = [entry[0] for entry in entries]
            if highlighted in names:
                view.highlighted = names.index(highlighted)
        else:
            view.add_option(Option(empty, disabled=True))
        view.scroll_to(y=scroll_y, animate=False)
        self.query_one(TabbedContent).get_tab(tab_id).label = label

import asyncio

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Label, ListItem, ListView, Static


CHARACTER_CSS = """
CharacterScreen {
    align: center middle;
}

#character_box {
    width: 50;
    height: 70%;
    border: solid $accent;
    background: $panel;
    padding: 1 2;
}

#character_list {
    height: 1fr;
    margin-top: 1;
}
"""


class CharacterItem(ListItem):

    def __init__(self, name:str, current:bool) -> None:
        super().__init__(Label(f"{'> ' if current else '  '}{name}", markup=False))
        self.character = name


class CharacterScreen(ModalScreen[str | None]):

    CSS = CHARACTER_CSS

    def __init__(self, characters:list[str], current:str="") -> None:
        super().__init__()
        self.characters = characters
        self.current = current
        self.render_lock = asyncio.Lock()

    def compose(self) -> ComposeResult:
        with Vertical(id="character_box"):
            yield Static("[b]Choose character[/b]")
            yield Input(placeholder="search...", id="character_search")
            yield ListView(id="character_list")

    async def on_mount(self) -> None:
        await self.render_list("")
        self.query_one("#character_search", Input).focus()

    async def render_list(self, needle:str) -> None:
        async with self.render_lock:
            await self._render_list(needle)

    async def _render_list(self, needle:str) -> None:
        view = self.query_one("#character_list", ListView)
        await view.clear()
        names = [name for name in self.characters if needle.lower() in name.lower()]
        await view.extend([CharacterItem(name, name == self.current) for name in names])
        if names:
            view.index = names.index(self.current) if self.current in names else 0

    async def on_input_changed(self, event:Input.Changed) -> None:
        await self.render_list(event.value.strip())

    def on_input_submitted(self, event:Input.Submitted) -> None:
        view = self.query_one("#character_list", ListView)
        if isinstance(view.highlighted_child, CharacterItem):
            self.dismiss(view.highlighted_child.character)

    def on_list_view_selected(self, event:ListView.Selected) -> None:
        if isinstance(event.item, CharacterItem):
            self.dismiss(event.item.character)

    def on_key(self, event:object) -> None:
        key = getattr(event, "key", "")
        view = self.query_one("#character_list", ListView)
        if key == "escape":
            self.dismiss(None)
        elif key in ("up", "down") and not view.has_focus:
            view.action_cursor_up() if key == "up" else view.action_cursor_down()

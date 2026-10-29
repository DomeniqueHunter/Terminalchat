import asyncio
import html
from typing import Any

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Label, ListItem, ListView, Static

from terminal_config import CHANNELS_CSS


MAX_ENTRIES = 500


class ChannelItem(ListItem):

    def __init__(self, code:str, title:str) -> None:
        super().__init__(Label(f"#{html.unescape(title)}", markup=False))
        self.code = code


class ChannelsList(ModalScreen):

    CSS = CHANNELS_CSS

    def __init__(self, client:Any) -> None:
        super().__init__()
        self.client = client
        self.filters = {"public": "", "private": ""}
        self.render_lock = asyncio.Lock()

    def compose(self) -> ComposeResult:
        with Horizontal(id="container"):
            with Vertical(classes="panel"):
                yield Static("Public Channels")
                yield Input(placeholder="search public...", id="public_search")
                yield ListView(id="public_list")

            with Vertical(classes="panel"):
                yield Static("Private Channels")
                yield Input(placeholder="search private...", id="private_search")
                yield ListView(id="private_list")

    async def on_mount(self) -> None:
        await self.render_lists()
        self.query_one("#public_search", Input).focus()

    def entries(self, kind:str) -> list[tuple[str, str]]:
        manager = self.client.channel_manager
        source = manager.official_channels if kind == "public" else manager.open_private_channels
        needle = self.filters[kind].lower()
        items = [(code, channel.name) for code, channel in source.items() if needle in channel.name.lower()]
        return sorted(items, key=lambda item: item[1].lower())[:MAX_ENTRIES]

    async def render_lists(self) -> None:
        async with self.render_lock:
            await self._render_lists()

    async def _render_lists(self) -> None:
        for kind in ("public", "private"):
            view = self.query_one(f"#{kind}_list", ListView)
            await view.clear()
            items = [ChannelItem(code, title) for code, title in self.entries(kind)]
            if items:
                await view.extend(items)
                view.index = 0
            else:
                await view.append(ListItem(Label("(loading / no match)")))

    async def on_input_changed(self, event:Input.Changed) -> None:
        kind = "public" if event.input.id == "public_search" else "private"
        self.filters[kind] = event.value.strip()
        await self.render_lists()

    async def on_list_view_selected(self, event:ListView.Selected) -> None:
        if not isinstance(event.item, ChannelItem):
            return
        self.app.pop_screen()
        await self.client.join(event.item.code)

    def on_key(self, event:Any) -> None:
        if event.key == "escape":
            self.app.pop_screen()

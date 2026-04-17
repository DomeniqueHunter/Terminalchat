from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Static, Input, ListView, ListItem, Label
from textual.containers import Horizontal, Vertical

from terminal_config import CHANNELS_CSS
from fchat import Opcode as opcode

from chat_log import logging


class ChannelsList(ModalScreen):

    CSS = CHANNELS_CSS

    def __init__(self, main=None):
        super().__init__()
        self.main = main

        self.public_filter = ""
        self.private_filter = ""

        self.public_list: ListView | None = None
        self.private_list: ListView | None = None

    def compose(self) -> ComposeResult:
        with Horizontal(id="container"):

            with Vertical(classes="panel"):
                yield Static("Public Chats")
                yield Input(placeholder="search public...", id="public_search")
                yield ListView(id="public_list")

            with Vertical(classes="panel"):
                yield Static("Private Chats")
                yield Input(placeholder="search private...", id="private_search")
                yield ListView(id="private_list")

    def on_mount(self) -> None:
        self.public_list = self.query_one("#public_list", ListView)
        self.private_list = self.query_one("#private_list", ListView)

        self.render_lists()
        self.set_focus(self.public_list)

    def render_lists(self) -> None:
        self.public_list.clear()
        self.private_list.clear()

        pf = self.public_filter.lower()
        pr = self.private_filter.lower()

        for code, channel in self.main.channel_manager.official_channels.items():
            name = str(channel)

            if pf in name.lower():
                item = ListItem(Label(f"#{name}"))
                item.channel = channel
                self.public_list.append(item)

        for code, channel in self.main.channel_manager.open_private_channels.items():
            name = channel.name

            if pr in name.lower():
                item = ListItem(Label(f"#{name}"))
                item.channel = channel
                self.private_list.append(item)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        logging("debug.log", f"channel: {event.item.channel.name} {event.item.channel.code}\n")

        channel = event.item.channel

        if channel:
            self.call_later(lambda: self._join(channel.code))

    async def _join(self, channel) -> None:
        logging("debug.log", f"join: {channel}\n")

        await self.join_channel(channel)
        self.app.pop_screen()

    async def join_channel(self, channel) -> None:
        if self.main:
            payload = {"channel": getattr(channel, "code", str(channel))}
            await self.main.comm.message(opcode.JOIN_CHANNEL, payload)

            if hasattr(self.main, "chats"):
                key = channel.name if hasattr(channel, "name") else str(channel)
                self.main.chats.setdefault(key, [])

    def on_input_submitted(self, event: Input.Submitted) -> None:
        value = event.value.strip()

        if event.input.id == "public_search":
            self.public_filter = value

        elif event.input.id == "private_search":
            self.private_filter = value

        self.render_lists()
        event.input.value = ""

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.app.pop_screen()
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Static, Input
from textual.containers import Horizontal, Vertical, VerticalScroll

from terminal_config import CHANNELS_CSS
from chat_log import logging


class ChannelsList(ModalScreen):

    CSS = CHANNELS_CSS

    def __init__(self, main=None):
        super().__init__()
        self.main = main

        self.public_filter = ""
        self.private_filter = ""

    def compose(self) -> ComposeResult:
        with Horizontal(id="container"):

            with VerticalScroll(classes="panel"):

                yield Static("Public Chats")
                yield Input(placeholder="search public...", id="public_search")

                self.public_container = VerticalScroll()
                yield self.public_container

            with VerticalScroll(classes="panel"):

                yield Static("Private Chats")
                yield Input(placeholder="search private...", id="private_search")

                self.private_container = VerticalScroll()
                yield self.private_container

    def on_mount(self) -> None:
        self.render_lists()

    def render_lists(self) -> None:
        self.public_container.remove_children()
        self.private_container.remove_children()

        pf = self.public_filter.lower()
        pr = self.private_filter.lower()

        for code, channel in self.main.channel_manager.official_channels.items():
            name = str(channel)

            if pf in name.lower():
                self.public_container.mount(Static(f"#{name}"))

        for code, channel in self.main.channel_manager.open_private_channels.items():
            name = channel.name

            if pr in name.lower():
                self.private_container.mount(Static(f"#{name}"))

    def on_input_submitted(self, event: Input.Submitted) -> None:
        value = event.value.strip()

        if event.input.id == "public_search":
            self.public_filter = value

        elif event.input.id == "private_search":
            self.private_filter = value

        self.render_lists()

        event.input.value = ""

        logging("debug.log", f"search submitted: {event.input.id} -> {value}\n")

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.app.pop_screen()
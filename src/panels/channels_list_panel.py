

from textual.app import App, ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Static
from textual.containers import Horizontal, Vertical, VerticalScroll

from terminal_config import CHANNELS_CSS


class ChannelsList(ModalScreen):

    CSS = CHANNELS_CSS

    def __init__(self, main:App=None):
        super().__init__()
        self.main = main
        print(self.main.channel_manager.official_channels)

    def compose(self) -> ComposeResult:
        with Horizontal(id="container"):

            with VerticalScroll(classes="panel"):
                yield Static("Public Chats")
                for code, channel in self.main.channel_manager.official_channels.items():
                    yield Static(f"#{channel}")

            with VerticalScroll(classes="panel"):
                yield Static("Private Chats")
                for code, channel in self.main.channel_manager.open_private_channels.items():
                    yield Static(f"#{channel.name}")
    
    def on_key(self, event) -> None:
        if event.key == "escape":
            self.app.pop_screen()
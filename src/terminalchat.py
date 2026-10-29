#!/usr/bin/env python3

import asyncio
import html

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Footer, Header, Input, Label, ListItem, ListView, Static

from chat_store import CHANNEL, Chat
from chat_widgets import ChatLine, HistoryInput
from client import Client
from config import Config
from eicons import EiconCache
from panels.channels_list_panel import ChannelsList
from terminal_config import APP_BINDINGS, APP_CSS


LIST_REFRESH_SECONDS = 300


class ChatApp(App):
    BINDINGS = APP_BINDINGS
    CSS = APP_CSS
    TITLE = "Terminal Chat"

    def __init__(self, config:Config) -> None:
        super().__init__()
        self.client = Client(config, self)
        self.eicons = None
        if config.get("eicons", "inline") == "inline":
            self.eicons = EiconCache(max_age_hours=float(config.get("eicon_max_age_hours", 24)))
        self.eicon_height = int(config.get("eicon_height", 4))
        self.gif_enabled = bool(config.get("eicon_animate", True))
        self.active_chat: str | None = None
        self.list_ids: list[str | None] = []

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="main"):
            yield ListView(id="chat_list")
            with Vertical(id="chat_container"):
                yield VerticalScroll(id="chat_view")
                yield HistoryInput(placeholder="Type message or /help ...", id="chat_input")
        yield Footer()

    @property
    def list_view(self) -> ListView:
        return self.query_one("#chat_list", ListView)

    @property
    def chat_view(self) -> VerticalScroll:
        return self.query_one("#chat_view", VerticalScroll)

    def current_chat(self) -> Chat | None:
        return self.client.store.get(self.active_chat) if self.active_chat else None

    async def on_mount(self) -> None:
        self.sub_title = "connecting..."
        await self.chat_view.mount(Static("No chats - press ctrl+o for the channel list or type /help", classes="placeholder"))
        self.query_one("#chat_input", Input).focus()
        self.run_worker(self.start_backend(), exclusive=True)

    async def on_unmount(self) -> None:
        await self.client.stop()
        if self.eicons is not None:
            await self.eicons.close()

    async def start_backend(self) -> None:
        if not await self.client.start():
            self.sub_title = "offline"
            self.notify("Could not connect to the chat server", severity="error")
            return

        self.sub_title = f"online as {self.client.character}"
        self.run_worker(self.client.consumer.receive(), group="receiver")
        self.run_worker(self.periodic_worker(), group="periodic")

        await self.client.restore_pins()
        defaults = self.client.config.get("default_channels") or []
        for index, channel in enumerate(defaults):
            await self.client.join(channel, open_chat=index == 0)
        first = self.first_chat_id()
        if not defaults and first and self.active_chat is None:
            await self.open_chat(first)

    async def periodic_worker(self) -> None:
        while True:
            await self.client.request_channel_lists()
            await asyncio.sleep(LIST_REFRESH_SECONDS)

    async def connection_lost(self) -> None:
        self.sub_title = "disconnected"
        self.notify("Connection to the chat server lost", severity="error", timeout=15)
        await self.client.stop()

    def channel_lists_updated(self) -> None:
        if isinstance(self.screen, ChannelsList):
            self.screen.run_worker(self.screen.render_lists(), exclusive=True)

    def chat_line(self, line:str) -> ChatLine:
        return ChatLine(line, self.eicons, self.eicon_height)

    def first_chat_id(self) -> str | None:
        chats = list(self.client.store.chats.values())
        ordered = [chat for chat in chats if chat.kind == CHANNEL] + [chat for chat in chats if chat.kind != CHANNEL]
        return ordered[0].id if ordered else None

    def list_entry(self, chat:Chat) -> ListItem:
        prefix = "#" if chat.kind == CHANNEL else "@"
        marker = "*" if chat.unread else " "
        pin = "+" if self.client.pins.is_pinned(chat) else " "
        return ListItem(Label(f"{marker}{pin}{prefix}{html.unescape(chat.title)}", markup=False))

    async def rebuild_list(self) -> None:
        chats = list(self.client.store.chats.values())
        channels = [chat for chat in chats if chat.kind == CHANNEL]
        users = [chat for chat in chats if chat.kind != CHANNEL]

        self.list_ids = []
        items = []
        for chat in channels:
            self.list_ids.append(chat.id)
            items.append(self.list_entry(chat))
        if channels and users:
            self.list_ids.append(None)
            items.append(ListItem(Label(""), disabled=True))
        for chat in users:
            self.list_ids.append(chat.id)
            items.append(self.list_entry(chat))

        await self.list_view.clear()
        if items:
            await self.list_view.extend(items)
        if self.active_chat in self.list_ids:
            self.list_view.index = self.list_ids.index(self.active_chat)

    async def open_chat(self, chat_id:str) -> None:
        chat = self.client.store.get(chat_id)
        if chat is None:
            return
        self.active_chat = chat_id
        chat.unread = False

        await self.chat_view.remove_children()
        lines = self.client.store.history(chat)
        widgets = [self.chat_line(line) for line in lines] or [Static("No messages yet", classes="placeholder")]
        await self.chat_view.mount_all(widgets)
        self.chat_view.scroll_end(animate=False)
        await self.rebuild_list()

    async def show_line(self, chat_id:str, line:str) -> None:
        if chat_id == self.active_chat:
            await self.chat_view.query(".placeholder").remove()
            await self.chat_view.mount(self.chat_line(line))
            self.chat_view.scroll_end(animate=False)
            return
        chat = self.client.store.get(chat_id)
        if chat is not None:
            chat.unread = True
        await self.rebuild_list()

    async def chat_removed(self, chat_id:str) -> None:
        if chat_id != self.active_chat:
            await self.rebuild_list()
            return
        self.active_chat = None
        first = self.first_chat_id()
        if first:
            await self.open_chat(first)
            return
        await self.chat_view.remove_children()
        await self.chat_view.mount(Static("No chats", classes="placeholder"))
        await self.rebuild_list()

    async def on_list_view_selected(self, event:ListView.Selected) -> None:
        if event.list_view.id != "chat_list":
            return
        index = event.list_view.index
        if index is not None and 0 <= index < len(self.list_ids) and self.list_ids[index]:
            await self.open_chat(self.list_ids[index])
            self.query_one("#chat_input", Input).focus()

    def action_open_channels_list(self) -> None:
        if not isinstance(self.screen, ChannelsList):
            self.push_screen(ChannelsList(self.client))

    async def action_close_chat(self) -> None:
        chat = self.current_chat()
        if chat is None:
            return
        if chat.kind == CHANNEL:
            await self.client.leave(chat.key)
        self.client.store.remove(chat.id)
        await self.chat_removed(chat.id)

    async def on_input_submitted(self, event:Input.Submitted) -> None:
        if event.input.id != "chat_input":
            return
        text = event.value.strip()
        event.input.value = ""
        if not text:
            return
        if isinstance(event.input, HistoryInput):
            event.input.remember(text)

        if text.startswith("/"):
            await self.client.commands.handle(text)
            return

        chat = self.current_chat()
        if chat is None:
            self.notify("No chat open", severity="warning")
            return
        await self.client.send(chat, text)


def main() -> None:
    config = Config("config.json")
    ChatApp(config).run()


if __name__ == "__main__":
    main()

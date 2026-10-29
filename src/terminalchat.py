#!/usr/bin/env python3

import asyncio
import html

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Footer, Header, Input, Label, ListItem, ListView, Static

from chat_store import CHANNEL, Chat, render_line
from client import Client
from config import Config
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
        self.active_chat: str | None = None
        self.list_ids: list[str] = []

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="main"):
            yield ListView(id="chat_list")
            with Vertical(id="chat_container"):
                yield VerticalScroll(id="chat_view")
                yield Input(placeholder="Type message or /help ...", id="chat_input")
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

    async def start_backend(self) -> None:
        if not await self.client.start():
            self.sub_title = "offline"
            self.notify("Could not connect to the chat server", severity="error")
            return

        self.sub_title = f"online as {self.client.character}"
        self.run_worker(self.client.consumer.receive(), group="receiver")
        self.run_worker(self.periodic_worker(), group="periodic")

        defaults = self.client.config.get("default_channels") or []
        for index, channel in enumerate(defaults):
            await self.client.join(channel, open_chat=index == 0)

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

    async def rebuild_list(self) -> None:
        chats = self.client.store.chats
        self.list_ids = list(chats.keys())
        items = []
        for chat_id in self.list_ids:
            chat = chats[chat_id]
            prefix = "#" if chat.kind == CHANNEL else "@"
            marker = "* " if chat.unread else "  "
            items.append(ListItem(Label(f"{marker}{prefix}{html.unescape(chat.title)}", markup=False)))

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
        widgets = [Static(render_line(line)) for line in lines] or [Static("No messages yet", classes="placeholder")]
        await self.chat_view.mount_all(widgets)
        self.chat_view.scroll_end(animate=False)
        await self.rebuild_list()

    async def show_line(self, chat_id:str, line:str) -> None:
        if chat_id == self.active_chat:
            await self.chat_view.query(".placeholder").remove()
            await self.chat_view.mount(Static(render_line(line)))
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
        ids = self.client.store.ids()
        if ids:
            await self.open_chat(ids[0])
            return
        await self.chat_view.remove_children()
        await self.chat_view.mount(Static("No chats", classes="placeholder"))
        await self.rebuild_list()

    async def on_list_view_selected(self, event:ListView.Selected) -> None:
        if event.list_view.id != "chat_list":
            return
        index = event.list_view.index
        if index is not None and 0 <= index < len(self.list_ids):
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

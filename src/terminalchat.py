#!/usr/bin/env python3

from typing import Dict, List, Set

import asyncio
import json

from datetime import datetime
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Header, Footer, Input, Static, ListView, ListItem

from terminal_config import CSS, BINDINGS
from config import Config
from communication import Communication


class ChatApp(App):
    BINDINGS = BINDINGS
    CSS = CSS

    def __init__(self) -> None:
        super().__init__()

        # chat storage: user -> messages
        self.chats: Dict[str, List[str]] = {}

        # UI state
        self.closed: Set[str] = set()
        self.active_chat: str | None = None

        self.config_obj = None
        self.comm = None

    def compose(self) -> ComposeResult:
        yield Header()

        with Horizontal(id="main"):
            self.list_view = ListView(id="chat_list")
            yield self.list_view

            with Vertical(id="chat_container"):
                self.chat_view = VerticalScroll(id="chat_view")
                yield self.chat_view

                yield Input(placeholder="Type message...")

        yield Footer()

    def on_mount(self) -> None:
        self.rebuild_list()

        if self.chats:
            first_user = next(iter(self.chats))
            self.open_chat(first_user)

        self.run_worker(self.start_backend(), exclusive=True)

    async def start_backend(self) -> None:
        await self.comm.connect()

        await self.comm.start_sender()
        await self.comm.identify()
        await self.comm.start_receiver()

        self.run_worker(self.receiver_consumer(), exclusive=False)

    async def receiver_consumer(self) -> None:
        while True:
            op, json_message = await self.comm.receive()

            if op == "PIN":
                await self.comm.priority_message(opcode="PIN")

            elif op == "PRI":
                data = json.loads(json_message)
                user = data.get("character")
                message = (data.get("message") or "").strip()

                # ensure chat exists
                if user not in self.chats:
                    self.chats[user] = []

                # reopen if closed
                if user in self.closed:
                    self.closed.remove(user)

                # store message
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # formatted message
                formatted_message = f"[{timestamp}] {user}: {message}"
                # self.chats[user].append(f"[{timestamp}] **{user}**: {message}")

                # logging per user
                base_path = Path("chats") / str(self.config_obj.get("character")) / str(user)
                base_path.mkdir(parents=True, exist_ok=True)

                log_file = base_path / "chat.log"

                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(f"{formatted_message}\n")

                if user == self.active_chat:
                    self.chat_view.mount(Static(f"[{timestamp}] [b]{user}[/b]: {message}", markup=True))
                    self.chat_view.scroll_end()

                self.rebuild_list()

            elif op == "MSG":
                pass

    def add_message(self, user: str, msg: str) -> None:
        if user not in self.chats:
            return

        self.chat_view.mount(Static(msg))
        self.chat_view.scroll_end()

    def rebuild_list(self) -> None:
        self.list_view.clear()

        for user in self.chats.keys():
            if user in self.closed:
                continue

            self.list_view.append(ListItem(Static(user)))

    def open_chat(self, user: str) -> None:
        self.active_chat = user

        self.chat_view.remove_children()

        base_path = Path("chats") / str(self.config_obj.get("character")) / str(user)
        log_file = base_path / "chat.log"

        if log_file.exists():
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    self.chat_view.mount(Static(line.rstrip()))
        else:
            self.chat_view.mount(Static("No messages yet"))

        self.chat_view.scroll_end()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        visible_users = [u for u in self.chats.keys() if u not in self.closed]

        if 0 <= event.index < len(visible_users):
            self.open_chat(visible_users[event.index])

    async def handle_input(self, text: str) -> None:
        await asyncio.sleep(0)

        if not self.active_chat:
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        msg = f"You: {text}"

        # UI
        self.chat_view.mount(Static(msg))
        self.chat_view.scroll_end()

        # local model update (optional but consistent)
        self.chats[self.active_chat].append(msg)

        # logging
        base_path = Path("chats") / str(self.config_obj.get("character")) / str(self.active_chat)
        base_path.mkdir(parents=True, exist_ok=True)

        log_file = base_path / "chat.log"

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {msg}\n")

        # SEND to server
        await self.comm.message("MSG", {
            "to": self.active_chat,
            "message": text
        })

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()

        if text:
            await self.handle_input(text)

        event.input.value = ""

    def action_close_chat(self) -> None:
        if self.active_chat:
            self.closed.add(self.active_chat)
            self.rebuild_list()

            visible = [u for u in self.chats.keys() if u not in self.closed]

            if visible:
                self.open_chat(visible[0])
            else:
                self.chat_view.remove_children()
                self.chat_view.mount(Static("No chats"))


def main() -> None:
    app = ChatApp()

    config = Config("config.json")
    comm = Communication(config)

    app.config_obj = config
    app.comm = comm

    app.run()


if __name__ == "__main__":
    main()
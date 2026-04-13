#!/usr/bin/env python3

from typing import Dict, List, Set

import asyncio
import json

from datetime import datetime
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Header, Footer, Input, Static, ListView, ListItem

from opcodes import Opcode as opcode
from terminal_config import CSS, BINDINGS
from config import Config
from communication import Communication
from channels import ChannelManager


class ChatApp(App):
    BINDINGS = BINDINGS
    CSS = CSS

    def __init__(self) -> None:
        super().__init__()

        # chat storage: target -> messages (structured)
        self.chats: Dict[str, List[dict]] = {}
        self.channel_manager = ChannelManager()

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
            first = next(iter(self.chats))
            self.open_chat(first)

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
                continue

            data = json.loads(json_message)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if op == "PRI":
                user = data.get("character")
                message = (data.get("message") or "").strip()

                if user not in self.chats:
                    self.chats[user] = []

                if user in self.closed:
                    self.closed.remove(user)

                formatted_message = f"[{timestamp}] {user}: {message}"
                formatted_message_bold = f"[{timestamp}] [b]{user}[/b]: {message}"

                self.chats[user].append({
                    "type": "PRI",
                    "text": formatted_message
                })

                base_path = Path("chats") / str(self.config_obj.get("character")) / str(user)
                base_path.mkdir(parents=True, exist_ok=True)

                log_file = base_path / "chat.log"

                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(f"{formatted_message}\n")

                if user == self.active_chat:
                    self.chat_view.mount(Static(formatted_message_bold, markup=True))
                    self.chat_view.scroll_end()

                self.rebuild_list()

            elif op == "MSG":
                room = data.get("room")
                message = (data.get("message") or "").strip()

                if room not in self.chats:
                    self.chats[room] = []

                if room in self.closed:
                    self.closed.remove(room)

                formatted_message = f"[{timestamp}] {message}"

                self.chats[room].append({
                    "type": "MSG",
                    "text": formatted_message
                })

                base_path = Path("chats") / str(self.config_obj.get("character")) / str(room)
                base_path.mkdir(parents=True, exist_ok=True)
                log_file = base_path / "chat.log"

                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(f"{formatted_message}\n")

                if room == self.active_chat:
                    self.chat_view.mount(Static(formatted_message))
                    self.chat_view.scroll_end()

                self.rebuild_list()
            elif op == "ORS":
                self.channel_manager.add_open_private_channels(json_message)
                continue

            elif op == "CHA":
                self.channel_manager.add_official_channels(json_message)
                continue

    def rebuild_list(self) -> None:
        self.list_view.clear()

        for chat in self.chats.keys():
            if chat in self.closed:
                continue

            self.list_view.append(ListItem(Static(chat)))

    def open_chat(self, chat: str) -> None:
        self.active_chat = chat

        self.chat_view.remove_children()

        base_path = Path("chats") / str(self.config_obj.get("character")) / str(chat)
        log_file = base_path / "chat.log"

        if log_file.exists():
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    self.chat_view.mount(Static(line.rstrip()))
        else:
            self.chat_view.mount(Static("No messages yet"))

        self.chat_view.scroll_end()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        visible = [c for c in self.chats.keys() if c not in self.closed]

        if 0 <= event.index < len(visible):
            self.open_chat(visible[event.index])

    def action_close_chat(self) -> None:
        if not self.active_chat:
            return

        self.closed.add(self.active_chat)
        self.rebuild_list()

        visible = [c for c in self.chats.keys() if c not in self.closed]

        if visible:
            self.open_chat(visible[0])
        else:
            self.chat_view.remove_children()
            self.chat_view.mount(Static("No chats"))

    async def handle_input(self, text: str) -> None:
        await asyncio.sleep(0)

        if not self.active_chat:
            return

        message = text
        target = self.active_chat
        me = self.config_obj.get("character")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        base_path = Path("chats") / str(self.config_obj.get("character")) / str(target)
        base_path.mkdir(parents=True, exist_ok=True)
        log_file = base_path / "chat.log"

        is_channel = target.startswith("#")  # falls du später anders entscheidest

        if is_channel:
            opcode_used = opcode.CHANNEL_MESSAGE

            data = {
                "channel": target,
                "message": message
            }
        else:
            opcode_used = opcode.PRIVATE_MESSAGE

            data = {
                "character": me,
                "recipient": target,
                "message": message
            }
        
        formatted_message = f"[{timestamp}] {me}: {message}"
        formatted_message_bold = f"[{timestamp}] [b]{me}[/b]: {message}"

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{formatted_message}\n")

        # UI update (unchanged behavior)
        self.chats[target].append(message)

        self.chat_view.mount(Static(f"{formatted_message_bold}", markup=True))
        self.chat_view.scroll_end()

        # send
        await self.comm.message(opcode_used, data)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()

        if text:
            await self.handle_input(text)

        event.input.value = ""


def main() -> None:
    app = ChatApp()

    config = Config("config.json")
    comm = Communication(config)

    app.config_obj = config
    app.comm = comm

    app.run()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

from typing import List, Set

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


def load_chat(chat_id: int) -> List[str]:
    if chat_id == 0:
        return ["Hello!", "Hi!", "Chat 1"]
    if chat_id == 1:
        return ["Another chat", "More messages"]
    return ["Empty chat"]


class ChatApp(App):
    BINDINGS = BINDINGS
    CSS = CSS

    def __init__(self) -> None:
        super().__init__()
        self.all_chats: List[str] = []
        self.closed: Set[str] = set()
        self.active_chat: int = 0

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

        if self.all_chats:
            self.open_chat(0)

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

                # logging
                base_path = Path("chats") / str(self.config_obj.get("character")) / str(user)
                base_path.mkdir(parents=True, exist_ok=True)

                log_file = base_path / "chat.log"
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(f"[{timestamp}] {json_message}\n")

                # add chat if new
                if user not in self.all_chats:
                    self.all_chats.append(user)

                # reopen if closed
                if user in self.closed:
                    self.closed.remove(user)

                self.rebuild_list()

            elif op == "MSG":
                pass

    def add_message(self, opcode: str, msg: str) -> None:
        self.chat_view.mount(Static(f"{opcode}: {msg}"))
        self.chat_view.scroll_end()

    def rebuild_list(self) -> None:
        self.list_view.clear()

        for user in self.all_chats:
            if user in self.closed:
                continue

            self.list_view.append(ListItem(Static(user)))

    def open_chat(self, chat_id: int) -> None:
        self.active_chat = chat_id

        self.chat_view.remove_children()

        for msg in load_chat(chat_id):
            self.chat_view.mount(Static(msg))

        self.chat_view.scroll_end()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        visible = [u for u in self.all_chats if u not in self.closed]

        if 0 <= event.index < len(visible):
            self.open_chat(self.all_chats.index(visible[event.index]))

    async def handle_input(self, text: str) -> None:
        await asyncio.sleep(0)

        self.chat_view.mount(Static(f"You: {text}"))
        self.chat_view.scroll_end()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()

        if text:
            await self.handle_input(text)

        event.input.value = ""

    def action_close_chat(self) -> None:
        if not self.all_chats:
            return

        user = self.all_chats[self.active_chat]
        self.closed.add(user)

        self.rebuild_list()

        visible = [u for u in self.all_chats if u not in self.closed]

        if visible:
            self.open_chat(self.all_chats.index(visible[0]))
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
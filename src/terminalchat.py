#!/usr/bin/env python3

from typing import List, Set

import asyncio
import json

from datetime import datetime

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Header, Footer, Input, Static, ListView, ListItem

from pathlib import Path

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
        self.all_chats: List[str] = ["Chat 1", "Chat 2"]
        self.closed: Set[int] = set()
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

        visible = self.visible_chats()
        if visible:
            self.open_chat(visible[0])

        # start async backend inside textual event loop
        self.run_worker(self.start_backend(), exclusive=True)

    async def start_backend(self) -> None:
        await self.comm.connect()

        await self.comm.start_sender()
        await self.comm.identify()
        await self.comm.start_receiver()

        self.run_worker(self.receiver_consumer(), exclusive=False)
    
    async def receiver_consumer(self) -> None:
        log_file = Path("chat.log")
        while True:
            op, json_message = await self.comm.receive()

            if op == "PIN": # ping event
                await self.comm.priority_message(opcode="PIN")

            elif op == "PRI": # private message
                data = json.loads(json_message)
                user = data.get("character")
                message = data.get("message")
                message = message.strip()

                # logging of chats
                base_path = Path("chats") / str(self.config_obj.get("character")) / str(user)
                base_path.mkdir(parents=True, exist_ok=True)
                log_file = base_path / "chat.log"
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                if user not in self.all_chats:
                    # update chats
                    self.all_chats.append(user)
                    self.rebuild_list()

                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(f"[{timestamp}] {json_message}\n")


            elif op == "MSG": # channel message
                pass

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{timestamp}: {json_message}\n")
            

    def add_message(self, opcode: str, msg: str) -> None:
        self.chat_view.mount(Static(f"{opcode}: {msg}"))
        self.chat_view.scroll_end()

    def visible_chats(self) -> List[int]:
        return [i for i in range(len(self.all_chats)) if i not in self.closed]

    def rebuild_list(self) -> None:
        self.list_view.clear()

        for chat_id in self.visible_chats():
            self.list_view.append(ListItem(Static(self.all_chats[chat_id])))

    def open_chat(self, chat_id: int) -> None:
        self.active_chat = chat_id

        self.chat_view.remove_children()

        for msg in load_chat(chat_id):
            self.chat_view.mount(Static(msg))

        self.chat_view.scroll_end()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        visible = self.visible_chats()

        if 0 <= event.index < len(visible):
            self.open_chat(visible[event.index])

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
        visible = self.visible_chats()

        if not visible:
            return

        chat_id = self.active_chat
        self.closed.add(chat_id)

        self.rebuild_list()

        visible = self.visible_chats()

        if visible:
            self.open_chat(visible[0])
        else:
            self.chat_view.remove_children()
            self.chat_view.mount(Static("No chats"))


def main() -> None:
    app = ChatApp()

    # dependency injection (clean & simple)
    config = Config("config.json")
    comm = Communication(config)

    app.config_obj = config
    app.comm = comm

    app.run()


if __name__ == "__main__":
    main()
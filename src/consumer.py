
from fchat import Opcode as opcode
from reaction import Reaction, EXCEPTION_REACTION_HANDLER

from typing import Dict, List, Set

import asyncio
import json

from datetime import datetime
from pathlib import Path

from textual.widgets import Header, Footer, Input, Static, ListView, ListItem
from chat_log import logging


class Consumer:

    def __init__(self, chat_client):
        self.chat_client = chat_client
        self.comm = None

        self.opcode_handler = Reaction()
        self.opcode_handler.add_action(opcode.PING, self.ping_handler)
        self.opcode_handler.add_action(opcode.PRIVATE_MESSAGE, self.private_message_handler)
        self.opcode_handler.add_action(opcode.CHANNEL_MESSAGE, self.public_message_handler)
        self.opcode_handler.add_action(opcode.LIST_OFFICAL_CHANNELS, self.list_official_channels_handler)
        self.opcode_handler.add_action(opcode.LIST_PRIVATE_CHANNELS, self.list_private_channels_handler)
        self.opcode_handler.add_action(EXCEPTION_REACTION_HANDLER, self.__defaultException)
    
    async def receive(self) -> None:
        while True:
            op, json_message = await self.comm.receive()

            data = json.loads(json_message)
            # logging("debug.log", f"{op}: {json_message}\n")
            
            if op:
                await self.opcode_handler.react(op, data)
    
    async def ping_handler(self, data:dict):   
        await self.comm.priority_message(opcode=opcode.PING)

    async def private_message_handler(self, data:dict):
        user = data.get("character")
        message = (data.get("message") or "").strip()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if user not in self.chat_client.chats:
            self.chat_client.chats[user] = []

        if user in self.chat_client.closed:
            self.chat_client.closed.remove(user)

        formatted_message = f"[{timestamp}] {user}: {message}"
        formatted_message_bold = f"[{timestamp}] [b]{user}[/b]: {message}"

        self.chat_client.chats[user].append({
            "type": "PRI",
            "text": formatted_message
        })

        base_path = Path("chats") / str(self.chat_client.config_obj.get("character")) / str(user)
        base_path.mkdir(parents=True, exist_ok=True)

        log_file = base_path / "chat.log"

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{formatted_message}\n")

        if user == self.chat_client.active_chat:
            self.chat_client.chat_view.mount(Static(formatted_message_bold, markup=True))
            self.chat_client.chat_view.scroll_end()

        self.chat_client.rebuild_list()

    async def public_message_handler(self, data:dict):
        channel_id = data.get("channel")
        message = (data.get("message") or "").strip()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if channel_id not in self.chat_client.chats:
            self.chat_client.chats[channel_id] = []

        if channel_id in self.chat_client.closed:
            self.chat_client.closed.remove(channel_id)

        formatted_message = f"[{timestamp}] {message}"

        self.chat_client.chats[channel_id].append({
            "type": "MSG",
            "text": formatted_message
        })

        base_path = Path("chats") / str(self.chat_client.config_obj.get("character")) / "channels" / str(channel_id)
        base_path.mkdir(parents=True, exist_ok=True)
        log_file = base_path / "chat.log"

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{formatted_message}\n")

        if channel_id == self.chat_client.active_chat:
            self.chat_client.chat_view.mount(Static(formatted_message))
            self.chat_client.chat_view.scroll_end()

        self.chat_client.rebuild_list()

    async def list_private_channels_handler(self, data:dict):
        self.chat_client.channel_manager.add_open_private_channels(data)

    async def list_official_channels_handler(self, data:dict):
        self.chat_client.channel_manager.add_official_channels(data)
    
    async def __defaultException(self, data:dict):
        pass

    
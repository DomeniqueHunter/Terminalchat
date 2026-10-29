from typing import Any

from fchat import Channel
from fchat import ChannelManager
from fchat import Communication
from fchat import Opcode as opcode

from chat_commands import ChatCommands
from chat_store import CHANNEL, USER, Chat, ChatStore, make_id
from config import Config
from consumer import Consumer
from genders import GenderStore
from own_status import OwnStatus
from pins import Pins
from presence import Presence


class Client:

    def __init__(self, config:Config, app:Any) -> None:
        self.config = config
        self.app = app
        self.character = str(config.get("character"))

        self.comm = Communication(config)
        self.channel_manager = ChannelManager(join_method=self._join_method)
        self.store = ChatStore(self.character)
        self.consumer = Consumer(self)
        self.commands = ChatCommands(self)

        self.pins = Pins(self.store.base / "pins.json")
        self.genders = GenderStore(self.store.base.parent / "genders.json")
        self.own_status = OwnStatus(self.store.base / "status.json")

        self.pending_open: set[str] = set()
        self.joining: set[str] = set()
        self.presence = Presence(app.presence_changed)

    async def start(self, ticket:str) -> str | None:
        async def cached_ticket() -> str:
            return ticket

        self.comm.get_api_ticket = cached_ticket
        if not await self.comm.connect():
            return "Could not connect to the chat server"
        await self.comm.start_sender()
        await self.comm.identify()
        await self.comm.start_receiver()
        return None

    async def stop(self) -> None:
        await self.comm.stop()

    def is_me(self, name:str | None) -> bool:
        return bool(name) and name.lower() == self.character.lower()

    def channel_title(self, code:str) -> str | None:
        channel = self.channel_manager.joined_channels.get(code) or self.channel_manager.find_channel_by_id(code)
        return channel.name if channel else None

    async def send_status(self) -> None:
        payload = {"status": self.own_status.status, "statusmsg": self.own_status.message}
        await self.comm.message(opcode.STATUS, payload)

    async def restore_status(self) -> None:
        if not self.own_status.is_default():
            await self.send_status()

    async def request_channel_lists(self) -> None:
        await self.comm.message(opcode.LIST_OFFICAL_CHANNELS)
        await self.comm.message(opcode.LIST_PRIVATE_CHANNELS)

    def resolve_channel(self, name_or_code:str) -> str:
        channel = self.channel_manager.find_channel(name_or_code)
        if channel is None:
            channel = self.channel_manager.find_channel_by_id(name_or_code)
        return channel.code if channel else name_or_code

    async def join(self, name_or_code:str, open_chat:bool=True) -> None:
        code = self.resolve_channel(name_or_code)
        if code in self.channel_manager.joined_channels:
            if open_chat:
                await self.app.open_chat(make_id(CHANNEL, code))
            return
        if open_chat:
            self.pending_open.add(code)
        if code in self.joining:
            return
        self.joining.add(code)
        await self.comm.message(opcode.JOIN_CHANNEL, {"channel": code})

    async def restore_pins(self) -> None:
        for item in self.pins.items:
            if item["kind"] == CHANNEL:
                self.store.get_or_create(item["key"], CHANNEL, item.get("title"))
                await self.join(item["key"], open_chat=False)
            else:
                self.store.get_or_create(item["key"], USER, item.get("title"))
        await self.app.rebuild_list()

    async def _join_method(self, code:str, name:str="", force:bool=False) -> None:
        await self.comm.message(opcode.JOIN_CHANNEL, {"channel": code})

    async def leave(self, code:str) -> None:
        self.joining.discard(code)
        self.channel_manager.joined_channels.pop(code, None)
        self.presence.drop_channel(code)
        await self.comm.message(opcode.LEAVE_CHANNEL, {"channel": code})

    def set_online(self, name:str, status:str="online") -> None:
        self.presence.set_online(name, status)

    def set_offline(self, name:str) -> None:
        self.presence.set_offline(name)

    def find_online(self, name:str) -> str | None:
        return self.presence.find_online(name)

    async def open_private(self, character:str) -> None:
        name = self.find_online(character)
        if name is None:
            existing = self.store.find_user(character)
            if existing is None:
                self.app.notify(f"'{character}' is not online or does not exist", severity="warning")
                return
            name = existing.key
        chat = self.store.get_or_create(name, USER)
        await self.app.open_chat(chat.id)

    async def send(self, chat:Chat, message:str) -> None:
        if chat.kind == CHANNEL:
            await self.comm.message(opcode.CHANNEL_MESSAGE, {"channel": chat.key, "message": message})
        else:
            await self.comm.message(opcode.PRIVATE_MESSAGE, {"recipient": chat.key, "message": message})
        line = self.store.append(chat, self.character, message)
        await self.app.show_line(chat.id, line)

    async def on_joined(self, code:str, title:str) -> None:
        self.joining.discard(code)
        self.channel_manager.add_channel(Channel(title, code))
        chat = self.store.get_or_create(code, CHANNEL, title)
        if code in self.pending_open:
            self.pending_open.discard(code)
            await self.app.open_chat(chat.id)
        else:
            await self.app.rebuild_list()

    async def on_left(self, code:str) -> None:
        self.channel_manager.joined_channels.pop(code, None)
        self.presence.drop_channel(code)
        chat_id = make_id(CHANNEL, code)
        self.store.remove(chat_id)
        await self.app.chat_removed(chat_id)

    async def on_private_message(self, sender:str, message:str) -> None:
        chat = self.store.get_or_create(sender, USER)
        line = self.store.append(chat, sender, message)
        await self.app.show_line(chat.id, line)

    async def on_channel_message(self, code:str, sender:str, message:str) -> None:
        chat = self.store.find(CHANNEL, code)
        if chat is None:
            chat = self.store.get_or_create(code, CHANNEL, self.channel_title(code))
        line = self.store.append(chat, sender, message)
        await self.app.show_line(chat.id, line)


def main() -> None:
    pass


if __name__ == "__main__":
    main()

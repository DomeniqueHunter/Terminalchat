import json
from typing import Any, Awaitable, Callable

from fchat import Opcode as opcode
from fchat.communication import COMM_ERROR

from chat_log import logging
from chat_store import CHANNEL


Handler = Callable[[dict], Awaitable[None]]


class Consumer:

    def __init__(self, client:Any) -> None:
        self.client = client
        self.handlers: dict[str, Handler] = {
            opcode.PING: self.on_ping,
            opcode.PRIVATE_MESSAGE: self.on_private_message,
            opcode.CHANNEL_MESSAGE: self.on_channel_message,
            opcode.ROLEPLAY_AD: self.on_ad,
            opcode.ROLL: self.on_roll,
            opcode.LIST_OFFICAL_CHANNELS: self.on_official_channels,
            opcode.LIST_PRIVATE_CHANNELS: self.on_private_channels,
            opcode.JOIN_CHANNEL: self.on_join,
            opcode.LEAVE_CHANNEL: self.on_leave,
            opcode.LIST_CHARACTERS: self.on_character_list,
            opcode.USER_CONNECTED: self.on_user_connected,
            opcode.GONE_OFFLINE: self.on_user_offline,
            opcode.ERROR: self.on_error,
            opcode.SYSTEM_MESSAGE: self.on_system,
        }

    @property
    def comm(self) -> Any:
        return self.client.comm

    @property
    def app(self) -> Any:
        return self.client.app

    async def receive(self) -> None:
        while True:
            op, raw = await self.comm.receive()

            if op == COMM_ERROR:
                await self.app.connection_lost()
                return

            handler = self.handlers.get(op)
            if handler is None:
                continue

            try:
                data = json.loads(raw) if raw else {}
                await handler(data)
            except Exception as error:
                logging("debug.log", f"{op} handler failed: {error!r} raw={raw}\n")

    async def on_ping(self, data:dict) -> None:
        await self.comm.priority_message(opcode.PING)

    async def on_private_message(self, data:dict) -> None:
        await self.client.on_private_message(data["character"], data.get("message", ""))

    async def on_channel_message(self, data:dict) -> None:
        await self.client.on_channel_message(data["channel"], data["character"], data.get("message", ""))

    async def on_ad(self, data:dict) -> None:
        await self.client.on_channel_message(data["channel"], f"[AD] {data['character']}", data.get("message", ""))

    async def on_roll(self, data:dict) -> None:
        message = data.get("message", "")
        if "channel" in data:
            await self.client.on_channel_message(data["channel"], "System", message)
        elif not self.client.is_me(data.get("character")):
            await self.client.on_private_message(data["character"], message)

    async def on_official_channels(self, data:dict) -> None:
        self.client.channel_manager.add_official_channels(data)
        self.app.channel_lists_updated()

    async def on_private_channels(self, data:dict) -> None:
        self.client.channel_manager.add_open_private_channels(data)
        self.app.channel_lists_updated()

    async def on_join(self, data:dict) -> None:
        if not self.client.is_me(data["character"]["identity"]):
            return
        code = data["channel"]
        await self.client.on_joined(code, data.get("title") or code)

    async def on_leave(self, data:dict) -> None:
        if self.client.is_me(data.get("character")):
            await self.client.on_left(data["channel"])

    async def on_character_list(self, data:dict) -> None:
        for entry in data.get("characters", []):
            self.client.set_online(entry[0])

    async def on_user_connected(self, data:dict) -> None:
        self.client.set_online(data["identity"])

    async def on_user_offline(self, data:dict) -> None:
        self.client.set_offline(data["character"])

    async def on_error(self, data:dict) -> None:
        self.app.notify(f"Error {data.get('number')}: {data.get('message')}", severity="error")

    async def on_system(self, data:dict) -> None:
        if "channel" in data and self.client.store.find(CHANNEL, data["channel"]):
            await self.client.on_channel_message(data["channel"], "System", data.get("message", ""))
        else:
            self.app.notify(data.get("message", ""), title="System")


def main() -> None:
    pass


if __name__ == "__main__":
    main()

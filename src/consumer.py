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
            opcode.FRIENDS_LIST: self.on_friends,
            opcode.STATUS: self.on_status,
            opcode.INITIAL_CHANNEL_DATA: self.on_channel_users,
            opcode.LIST_OPS: self.on_ops,
            opcode.PROMOTE_OP: self.on_op_added,
            opcode.DEMOTE_OP: self.on_op_removed,
            opcode.USER_CONNECTED: self.on_user_connected,
            opcode.GONE_OFFLINE: self.on_user_offline,
            opcode.INVITE: self.on_invite,
            opcode.KICK: self.on_kick,
            opcode.BAN: self.on_ban,
            opcode.TIMEOUT: self.on_timeout,
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
                if isinstance(data, dict) and isinstance(data.get("channel"), str):
                    data["channel"] = self.client.canonical_channel(data["channel"])
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
        else:
            character = data.get("character", "")
            partner = data.get("recipient", "") if self.client.is_me(character) else character
            if partner:
                await self.client.on_private_system(partner, message)

    async def on_official_channels(self, data:dict) -> None:
        self.client.channel_manager.add_official_channels(data)
        self.app.channel_lists_updated()

    async def on_private_channels(self, data:dict) -> None:
        self.client.channel_manager.add_open_private_channels(data)
        self.app.channel_lists_updated()

    async def on_join(self, data:dict) -> None:
        code = data["channel"]
        identity = data["character"]["identity"]
        if not self.client.is_me(identity):
            self.client.presence.add_member(code, identity)
            return
        await self.client.on_joined(code, data.get("title") or code)

    async def on_leave(self, data:dict) -> None:
        if self.client.is_me(data.get("character")):
            await self.client.on_left(data["channel"])
        else:
            self.client.presence.remove_member(data["channel"], data.get("character", ""))

    async def on_character_list(self, data:dict) -> None:
        for entry in data.get("characters", []):
            self.client.set_online(entry[0], entry[2] if len(entry) > 2 else "online")
            self.client.genders.set(entry[0], entry[1] if len(entry) > 1 else None)

    async def on_user_connected(self, data:dict) -> None:
        self.client.set_online(data["identity"], data.get("status", "online"))
        self.client.genders.set(data["identity"], data.get("gender"))

    async def on_friends(self, data:dict) -> None:
        self.client.presence.set_friends(data.get("characters", []))

    async def on_status(self, data:dict) -> None:
        self.client.presence.set_status(data["character"], data.get("status", "online"))

    async def on_channel_users(self, data:dict) -> None:
        names = [user["identity"] for user in data.get("users", [])]
        self.client.presence.set_members(data["channel"], names)

    async def on_ops(self, data:dict) -> None:
        self.client.presence.set_ops(data["channel"], data.get("oplist", []))

    async def on_op_added(self, data:dict) -> None:
        self.client.presence.add_op(data["channel"], data["character"])

    async def on_op_removed(self, data:dict) -> None:
        self.client.presence.remove_op(data["channel"], data["character"])

    async def on_user_offline(self, data:dict) -> None:
        self.client.set_offline(data["character"])

    async def on_kick(self, data:dict) -> None:
        name = data.get("character", "")
        await self.client.on_channel_event(data["channel"], f"{data.get('operator', '?')} kicked {name}", name)

    async def on_ban(self, data:dict) -> None:
        name = data.get("character", "")
        await self.client.on_channel_event(data["channel"], f"{data.get('operator', '?')} banned {name}", name)

    async def on_timeout(self, data:dict) -> None:
        name = data.get("character", "")
        text = f"{data.get('operator', '?')} timed out {name} for {data.get('length', '?')} minutes"
        await self.client.on_channel_event(data["channel"], text, name)

    async def on_invite(self, data:dict) -> None:
        code = data.get("name", "")
        self.client.on_invited(data.get("sender", "?"), code, data.get("title") or code)

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

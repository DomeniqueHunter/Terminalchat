import asyncio
import os
from typing import Any, Awaitable, Callable

from own_status import MAX_MESSAGE_LENGTH, VALID_STATUSES


COMMAND_INFO = [
    ("join", "<channel>", "join a channel (name or code)"),
    ("leave", "", "leave / close the current chat"),
    ("priv", "<name>", "open a private chat"),
    ("me", "<text>", "emote in the current chat"),
    ("status", "[status] [text]", "set status and/or status message"),
    ("status:flag", "<status>", "change only the status"),
    ("status:message", "[text]", "change only the message (empty clears it)"),
    ("channels", "", "open the channel list"),
    ("users", "", "show/hide friends and channel users"),
    ("pin", "", "pin the current chat, restored on start"),
    ("unpin", "", "unpin the current chat"),
    ("pins", "", "show pinned chats"),
    ("gif", "[on|off]", "toggle animated eicons"),
    ("char", "[name]", "switch character"),
    ("logout", "", "log out and forget password"),
    ("minimize", "", "detach, keep running in background"),
    ("help", "", "show all commands"),
    ("quit", "", "exit"),
]

COMMAND_NAMES = [name for name, _, _ in COMMAND_INFO]


def command_usage(name:str, args:str) -> str:
    return f"/{name} {args}".rstrip()


def matching_commands(prefix:str) -> list[tuple[str, str, str]]:
    prefix = prefix.lower()
    return [entry for entry in COMMAND_INFO if entry[0].startswith(prefix)]


HELP_TEXT = "\n".join(f"{command_usage(name, args):<26} {description}" for name, args, description in COMMAND_INFO)


def unquote(text:str) -> str:
    text = text.strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        return text[1:-1].strip()
    return text


class ChatCommands:

    def __init__(self, client:Any) -> None:
        self.client = client
        self.commands: dict[str, Callable[[str], Awaitable[None]]] = {
            "join": self.cmd_join,
            "leave": self.cmd_leave,
            "close": self.cmd_leave,
            "priv": self.cmd_priv,
            "me": self.cmd_me,
            "status": self.cmd_status,
            "status:flag": self.cmd_status_flag,
            "status:message": self.cmd_status_message,
            "channels": self.cmd_channels,
            "users": self.cmd_users,
            "pin": self.cmd_pin,
            "unpin": self.cmd_unpin,
            "pins": self.cmd_pins,
            "gif": self.cmd_gif,
            "char": self.cmd_char,
            "logout": self.cmd_logout,
            "minimize": self.cmd_minimize,
            "detach": self.cmd_minimize,
            "help": self.cmd_help,
            "quit": self.cmd_quit,
        }

    @property
    def app(self) -> Any:
        return self.client.app

    async def handle(self, text:str) -> None:
        name, _, args = text[1:].partition(" ")
        func = self.commands.get(name.lower())
        if func is None:
            self.app.notify(f"Unknown command: /{name}  (see /help)", severity="warning")
            return
        await func(args.strip())

    async def cmd_join(self, args:str) -> None:
        if not args:
            self.app.notify("Usage: /join <channel>", severity="warning")
            return
        await self.client.join(unquote(args))

    async def cmd_leave(self, args:str) -> None:
        await self.app.action_close_chat()

    async def cmd_priv(self, args:str) -> None:
        if not args:
            self.app.notify("Usage: /priv <character>", severity="warning")
            return
        await self.client.open_private(unquote(args))

    async def cmd_me(self, args:str) -> None:
        chat = self.app.current_chat()
        if chat is None or not args:
            return
        await self.client.send(chat, f"/me {args}")

    async def cmd_pin(self, args:str) -> None:
        chat = self.app.current_chat()
        if chat is None:
            self.app.notify("No chat open", severity="warning")
            return
        if self.client.pins.pin(chat):
            self.app.notify(f"Pinned {chat.title}")
        await self.app.rebuild_list()

    async def cmd_unpin(self, args:str) -> None:
        chat = self.app.current_chat()
        if chat is None:
            self.app.notify("No chat open", severity="warning")
            return
        if self.client.pins.unpin(chat):
            self.app.notify(f"Unpinned {chat.title}")
        await self.app.rebuild_list()

    async def cmd_pins(self, args:str) -> None:
        items = self.client.pins.items
        if not items:
            self.app.notify("No pinned chats")
            return
        lines = [f"{'#' if item['kind'] == 'channel' else '@'}{item.get('title') or item['key']}" for item in items]
        self.app.notify("\n".join(lines), title="Pinned", timeout=10)

    async def cmd_gif(self, args:str) -> None:
        value = args.lower()
        if value in ("on", "off"):
            self.app.gif_enabled = value == "on"
        elif value:
            self.app.notify("Usage: /gif [on|off]", severity="warning")
            return
        else:
            self.app.gif_enabled = not self.app.gif_enabled
        self.app.notify(f"Animated eicons {'on' if self.app.gif_enabled else 'off'}")

    async def cmd_char(self, args:str) -> None:
        if not self.app.characters:
            self.app.notify("Character list not available yet", severity="warning")
            return
        name = unquote(args)
        if not name:
            self.app.choose_character()
            return
        match = self.app.match_character(name)
        if match is None:
            self.app.notify(f"'{name}' is not a character of this account", severity="warning")
        elif match == self.client.character:
            self.app.notify(f"Already logged in as {match}")
        else:
            self.app.run_worker(self.app.switch_character(match), exclusive=True, group="backend")

    async def cmd_logout(self, args:str) -> None:
        await self.app.logout()

    async def cmd_minimize(self, args:str) -> None:
        if not os.environ.get("TMUX"):
            self.app.notify("/minimize needs the 'terminalchat' launcher (runs inside tmux)", severity="warning")
            return
        process = await asyncio.create_subprocess_exec(
            "tmux", "detach-client", stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL
        )
        if await process.wait() != 0:
            self.app.notify("Could not detach from tmux", severity="error")

    async def cmd_users(self, args:str) -> None:
        self.app.action_toggle_sidebar()

    async def cmd_status(self, args:str) -> None:
        own = self.client.own_status
        if not args:
            message = f": {own.message}" if own.message else ""
            self.app.notify(f"Status {own.status}{message}\nUsage: /status [{'|'.join(VALID_STATUSES)}] [message]",
                            title="Status", timeout=8)
            return
        first, _, rest = args.partition(" ")
        if first.lower() in VALID_STATUSES:
            status, message = first.lower(), rest.strip()
        else:
            status, message = own.status, args.strip()
        await self.apply_status(status, message)

    async def cmd_status_flag(self, args:str) -> None:
        own = self.client.own_status
        status = args.strip().lower()
        if not status:
            self.app.notify(f"Status {own.status}\nUsage: /status:flag <{'|'.join(VALID_STATUSES)}>", title="Status", timeout=8)
            return
        if status not in VALID_STATUSES:
            self.app.notify(f"Unknown status '{status}', use one of: {', '.join(VALID_STATUSES)}", severity="warning")
            return
        await self.apply_status(status, own.message)

    async def cmd_status_message(self, args:str) -> None:
        await self.apply_status(self.client.own_status.status, args.strip())

    async def apply_status(self, status:str, message:str) -> None:
        if len(message) > MAX_MESSAGE_LENGTH:
            self.app.notify(f"Status message too long ({len(message)}/{MAX_MESSAGE_LENGTH})", severity="warning")
            return
        self.client.own_status.set(status, message)
        if self.app.online:
            await self.client.send_status()
            self.app.update_subtitle()
        self.app.notify(f"Status set to {status}" + (f": {message}" if message else ""))

    async def cmd_channels(self, args:str) -> None:
        self.app.action_open_channels_list()

    async def cmd_help(self, args:str) -> None:
        self.app.notify(HELP_TEXT, title="Commands", timeout=10)

    async def cmd_quit(self, args:str) -> None:
        self.app.exit()


def main() -> None:
    pass


if __name__ == "__main__":
    main()

from typing import Any, Awaitable, Callable


HELP_TEXT = (
    "/join <channel>   join a channel (name or code)\n"
    "/leave            leave / close the current chat\n"
    "/priv <name>      open a private chat\n"
    "/me <text>        emote in the current chat\n"
    "/pin, /unpin      (un)pin the current chat, restored on start\n"
    "/pins             show pinned chats\n"
    "/channels         open the channel list\n"
    "/quit             exit"
)


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
            "channels": self.cmd_channels,
            "pin": self.cmd_pin,
            "unpin": self.cmd_unpin,
            "pins": self.cmd_pins,
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

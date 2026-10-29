from typing import Any, Awaitable, Callable


HELP_TEXT = (
    "/join <channel>   join a channel (name or code)\n"
    "/leave            leave / close the current chat\n"
    "/priv <name>      open a private chat\n"
    "/me <text>        emote in the current chat\n"
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

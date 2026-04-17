import shlex
from typing import Dict, List, Any

from chat_log import logging

class ChatCommands:

    def __init__(self, app: Any) -> None:
        self.app = app

        self.commands = {
            "me": self.cmd_me,
            "priv": self.cmd_priv,
            "join": self.cmd_join,
        }

    async def handle(self, text: str) -> None:
        try:
            parts = shlex.split(text[1:])
        except ValueError:
            return

        if not parts:
            return

        cmd = parts[0]
        args = parts[1:]

        if cmd not in self.commands:
            return

        func = self.commands[cmd]
        await func(args)

    async def cmd_me(self, args: List[str]) -> None:
        pass

    async def cmd_priv(self, args: List[str]) -> None:
        logging("debug.log", f"__priv: {args}\n")

    async def cmd_join(self, args: List[str]) -> None:
        pass


def main() -> None:
    pass


if __name__ == "__main__":
    main()

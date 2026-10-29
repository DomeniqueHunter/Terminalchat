import html
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from rich.text import Text

from bbcode import to_text
from color_config import SENDER_STYLE


USER = "user"
CHANNEL = "channel"

LINE_PATTERN = re.compile(r"^(\[[^\]]*\]) (.+?): (.*)$")


def make_id(kind:str, key:str) -> str:
    return f"{kind}:{key}"


@dataclass
class Chat:
    key: str
    kind: str
    title: str
    unread: bool = False

    @property
    def id(self) -> str:
        return make_id(self.kind, self.key)


class ChatStore:

    def __init__(self, character:str, base_dir:str="chats") -> None:
        self.base = Path(base_dir) / character
        self.chats: dict[str, Chat] = {}

    def get(self, chat_id:str) -> Chat | None:
        return self.chats.get(chat_id)

    def find(self, kind:str, key:str) -> Chat | None:
        return self.chats.get(make_id(kind, key))

    def find_user(self, name:str) -> Chat | None:
        name = name.strip().lower()
        for chat in self.chats.values():
            if chat.kind == USER and chat.key.lower() == name:
                return chat
        return None

    def get_or_create(self, key:str, kind:str, title:str | None=None) -> Chat:
        chat = self.find(kind, key)
        if chat is None:
            chat = Chat(key, kind, title or key)
            self.chats[chat.id] = chat
        elif title:
            chat.title = title
        return chat

    def remove(self, chat_id:str) -> None:
        self.chats.pop(chat_id, None)

    def ids(self) -> list[str]:
        return list(self.chats.keys())

    def log_path(self, chat:Chat) -> Path:
        if chat.kind == CHANNEL:
            return self.base / "channels" / chat.key / "chat.log"
        return self.base / chat.key / "chat.log"

    def append(self, chat:Chat, sender:str, message:str) -> str:
        line = format_line(sender, message)
        path = self.log_path(chat)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as file:
            file.write(f"{line}\n")
        return line

    def history(self, chat:Chat, limit:int=300) -> list[str]:
        path = self.log_path(chat)
        if not path.exists():
            return []
        with open(path, "r", encoding="utf-8") as file:
            lines = [line.rstrip("\n") for line in file]
        return lines[-limit:]


def format_line(sender:str, message:str) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = html.unescape(message).strip()
    if message.startswith("/me "):
        return f"[{timestamp}] * {sender} {message[4:]}"
    if message.startswith("/me's "):
        return f"[{timestamp}] * {sender}'s {message[6:]}"
    return f"[{timestamp}] {sender}: {message}"


def render_line(line:str) -> Text:
    match = LINE_PATTERN.match(line)
    if not match:
        return to_text(line)
    timestamp, sender, message = match.groups()
    return Text.assemble(f"{timestamp} ", (sender, SENDER_STYLE), ": ", to_text(message))


def main() -> None:
    print(render_line(format_line("Tester", "Hallo [b]Welt[/b] &amp; so")))


if __name__ == "__main__":
    main()

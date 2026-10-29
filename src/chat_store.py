import html
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

from rich.text import Text

from bbcode import to_text
from color_config import SENDER_STYLE, NameStyle, make_style, no_name_style


USER = "user"
CHANNEL = "channel"
CONSOLE = "console"

LINE_PATTERN = re.compile(r"^(\[[^\]]*\]) ([^\n]+?): (.*)$", re.DOTALL)
CONTINUATION = "\t"
ENTRY_START = re.compile(r"^\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\] ")
DAY_FILE = re.compile(r"^\d{4}-\d{2}-\d{2}\.log$")
CONSOLE_DIR = "_console"


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
        self.migrated: set[str] = set()

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

    def log_dir(self, chat:Chat) -> Path:
        if chat.kind == CONSOLE:
            return self.base / CONSOLE_DIR
        if chat.kind == CHANNEL:
            return self.base / "channels" / chat.key
        return self.base / chat.key

    def legacy_log(self, chat:Chat) -> Path:
        if chat.kind == CONSOLE:
            return self.base / "console.log"
        return self.log_dir(chat) / "chat.log"

    def migrate(self, chat:Chat) -> None:
        if chat.id in self.migrated:
            return
        self.migrated.add(chat.id)
        legacy = self.legacy_log(chat)
        if not legacy.exists():
            return
        fallback = datetime.fromtimestamp(legacy.stat().st_mtime).strftime("%Y-%m-%d")
        groups: dict[str, list[str]] = {}
        for entry in read_entries(legacy):
            groups.setdefault(entry_date(entry) or fallback, []).append(entry)
        directory = self.log_dir(chat)
        directory.mkdir(parents=True, exist_ok=True)
        for day, entries in groups.items():
            path = directory / f"{day}.log"
            existing = path.read_text(encoding="utf-8") if path.exists() else ""
            tmp_path = path.with_suffix(".tmp")
            tmp_path.write_text("".join(encode_entry(entry) for entry in entries) + existing, encoding="utf-8")
            tmp_path.replace(path)
        legacy.replace(legacy.with_name(legacy.name + ".bak"))

    def day_files(self, chat:Chat) -> list[Path]:
        directory = self.log_dir(chat)
        if not directory.is_dir():
            return []
        return sorted(path for path in directory.iterdir() if DAY_FILE.match(path.name))

    def append(self, chat:Chat, sender:str, message:str) -> str:
        self.migrate(chat)
        line = format_line(sender, message)
        directory = self.log_dir(chat)
        directory.mkdir(parents=True, exist_ok=True)
        with open(directory / f"{line[1:11]}.log", "a", encoding="utf-8") as file:
            file.write(encode_entry(line))
        return line

    def history(self, chat:Chat, limit:int=300) -> list[str]:
        self.migrate(chat)
        entries: list[str] = []
        for path in reversed(self.day_files(chat)):
            entries = read_entries(path) + entries
            if len(entries) >= limit:
                break
        return entries[-limit:]

    def cleanup(self, keep_days:int) -> int:
        if keep_days <= 0 or not self.base.is_dir():
            return 0
        oldest = (datetime.now() - timedelta(days=keep_days - 1)).strftime("%Y-%m-%d")
        removed = 0
        for path in self.base.rglob("*.log"):
            if DAY_FILE.match(path.name) and path.name[:10] < oldest:
                path.unlink()
                removed += 1
        return removed


def encode_entry(entry:str) -> str:
    return entry.replace("\n", "\n" + CONTINUATION) + "\n"


def read_entries(path:Path) -> list[str]:
    entries: list[str] = []
    with open(path, "r", encoding="utf-8") as file:
        for raw in file:
            raw = raw.rstrip("\n")
            if entries and not ENTRY_START.match(raw):
                entries[-1] += "\n" + raw.removeprefix(CONTINUATION)
            else:
                entries.append(raw)
    return entries


def entry_date(entry:str) -> str | None:
    return entry[1:11] if ENTRY_START.match(entry) else None


def format_line(sender:str, message:str) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = html.unescape(message).replace("\r\n", "\n").replace("\r", "\n").strip()
    if message.startswith("/me "):
        return f"[{timestamp}] * {sender} {message[4:]}"
    if message.startswith("/me's "):
        return f"[{timestamp}] * {sender}'s {message[6:]}"
    return f"[{timestamp}] {sender}: {message}"


AD_PREFIX = "[AD] "


def is_ad_line(line:str) -> bool:
    match = LINE_PATTERN.match(line)
    return bool(match) and match.group(2).startswith(AD_PREFIX)


def split_line(line:str, name_style:NameStyle | None=None) -> tuple[Text, str]:
    name_style = name_style or no_name_style
    match = LINE_PATTERN.match(line)
    if not match:
        return Text(), line
    timestamp, sender, message = match.groups()
    return Text.assemble(f"{timestamp} ", (sender, make_style(SENDER_STYLE) + name_style(sender)), ": "), message


def render_line(line:str, show_eicons:bool=True, name_style:NameStyle | None=None) -> Text:
    header, message = split_line(line, name_style)
    return Text.assemble(header, to_text(message, show_eicons, name_style))


def main() -> None:
    print(render_line(format_line("Tester", "Hallo [b]Welt[/b] &amp; so")))


if __name__ == "__main__":
    main()

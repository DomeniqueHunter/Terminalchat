import json
from pathlib import Path

from chat_store import Chat


class Pins:

    def __init__(self, path:Path) -> None:
        self.path = path
        self.items: list[dict] = self.load()

    def load(self) -> list[dict]:
        try:
            with open(self.path, "r", encoding="utf-8") as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
        return [item for item in data if isinstance(item, dict) and "kind" in item and "key" in item]

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.path.with_suffix(".tmp")
        with open(tmp_path, "w", encoding="utf-8") as file:
            json.dump(self.items, file, indent=2, ensure_ascii=False)
        tmp_path.replace(self.path)

    def is_pinned(self, chat:Chat) -> bool:
        return any(item["kind"] == chat.kind and item["key"] == chat.key for item in self.items)

    def pin(self, chat:Chat) -> bool:
        if self.is_pinned(chat):
            return False
        self.items.append({"kind": chat.kind, "key": chat.key, "title": chat.title})
        self.save()
        return True

    def unpin(self, chat:Chat) -> bool:
        if not self.is_pinned(chat):
            return False
        self.items = [item for item in self.items if not (item["kind"] == chat.kind and item["key"] == chat.key)]
        self.save()
        return True


def main() -> None:
    pass


if __name__ == "__main__":
    main()

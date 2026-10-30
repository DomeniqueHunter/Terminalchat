import json
from pathlib import Path


class AdSettings:

    def __init__(self, path:Path, default:bool=True) -> None:
        self.path = path
        self.default = default
        self.channels: dict[str, bool] = self.load()

    def load(self) -> dict[str, bool]:
        try:
            with open(self.path, "r", encoding="utf-8") as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
        return {str(key).lower(): bool(value) for key, value in data.items()} if isinstance(data, dict) else {}

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.path.with_suffix(".tmp")
        with open(tmp_path, "w", encoding="utf-8") as file:
            json.dump(self.channels, file, indent=2, sort_keys=True)
        tmp_path.replace(self.path)

    def visible(self, code:str) -> bool:
        return self.channels.get(code.lower(), self.default)

    def set_visible(self, code:str, visible:bool) -> None:
        self.channels[code.lower()] = visible
        self.save()


class AdDrafts:

    def __init__(self, path:Path) -> None:
        self.path = path
        self.drafts: dict[str, str] = self.load()
        self.dirty = False

    def load(self) -> dict[str, str]:
        try:
            with open(self.path, "r", encoding="utf-8") as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
        return {str(key).lower(): str(value) for key, value in data.items()} if isinstance(data, dict) else {}

    def save(self) -> None:
        if not self.dirty:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.path.with_suffix(".tmp")
        with open(tmp_path, "w", encoding="utf-8") as file:
            json.dump(self.drafts, file, indent=2, sort_keys=True, ensure_ascii=False)
        tmp_path.replace(self.path)
        self.dirty = False

    def get(self, code:str) -> str:
        return self.drafts.get(code.lower(), "")

    def set(self, code:str, text:str) -> None:
        key = code.lower()
        if self.drafts.get(key, "") == text:
            return
        if text:
            self.drafts[key] = text
        else:
            self.drafts.pop(key, None)
        self.dirty = True


def main() -> None:
    pass


if __name__ == "__main__":
    main()

import json
from pathlib import Path


class GenderStore:

    def __init__(self, path:Path) -> None:
        self.path = path
        self.data: dict[str, str] = self.load()
        self.dirty = False

    def load(self) -> dict[str, str]:
        try:
            with open(self.path, "r", encoding="utf-8") as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
        return {str(key): str(value) for key, value in data.items()} if isinstance(data, dict) else {}

    def get(self, name:str) -> str | None:
        return self.data.get(name.strip().lower())

    def set(self, name:str, gender:str | None) -> None:
        if not name or not gender:
            return
        key = name.strip().lower()
        if self.data.get(key) != gender:
            self.data[key] = gender
            self.dirty = True

    def save(self) -> None:
        if not self.dirty:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.path.with_suffix(".tmp")
        with open(tmp_path, "w", encoding="utf-8") as file:
            json.dump(self.data, file, ensure_ascii=False, sort_keys=True)
        tmp_path.replace(self.path)
        self.dirty = False


def main() -> None:
    pass


if __name__ == "__main__":
    main()

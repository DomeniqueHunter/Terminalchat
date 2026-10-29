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


def main() -> None:
    pass


if __name__ == "__main__":
    main()

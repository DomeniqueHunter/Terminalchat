import json
import os
from pathlib import Path


DEFAULTS = {
    "account": "",
    "password": "",
    "character": "",
    "remember_password": True,
    "protocol": "wss://",
    "server": "chat.f-list.net",
    "endpoint": "/chat2",
    "default_channels": [],
}

CREDENTIAL_KEYS = ("account", "password", "character")


class Config(dict):

    def __init__(self, file_path:str) -> None:
        self.path = Path(file_path).expanduser().resolve()
        self.data_dir: Path | None = None
        data = dict(DEFAULTS)
        if self.path.exists():
            with open(self.path, "r", encoding="utf-8") as file:
                data.update(json.load(file))
        super().__init__(data)

    def is_complete(self) -> bool:
        return all(self.get(key) for key in CREDENTIAL_KEYS)

    def save(self) -> None:
        data = dict(self)
        if not data.get("remember_password"):
            data["password"] = ""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.path.with_suffix(".tmp")
        with open(tmp_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        os.chmod(tmp_path, 0o600)
        tmp_path.replace(self.path)


def main() -> None:
    config = Config("config.json")
    print(config.path, "complete:", config.is_complete())


if __name__ == "__main__":
    main()

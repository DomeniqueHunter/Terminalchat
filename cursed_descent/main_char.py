import json
from pathlib import Path


SETTINGS_FILE = "gui_settings.json"
KEY = "main_char"


class MainChar:
    def __init__(self, data_path:Path, scope:str="") -> None:
        self.path = data_path / SETTINGS_FILE
        self.key = f"{KEY}:{scope}" if scope else KEY
        self.name = self.load()

    def read(self) -> dict:
        try:
            saved = json.loads(self.path.read_text(encoding="utf-8"))
            return saved if isinstance(saved, dict) else {}
        except (OSError, ValueError):
            return {}

    def load(self) -> str:
        name = self.read().get(self.key, "")
        return name if isinstance(name, str) else ""

    def set(self, name:str) -> None:
        self.name = name
        saved = self.read()
        saved[self.key] = name
        try:
            self.path.write_text(json.dumps(saved, indent=2),
                                 encoding="utf-8")
        except OSError:
            pass

    def resolve(self, players:list[str]) -> str:
        if self.name in players:
            return self.name
        fallback = players[0] if players else ""
        if fallback != self.name:
            self.set(fallback)
        return fallback

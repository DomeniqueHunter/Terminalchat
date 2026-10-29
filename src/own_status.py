import json
from pathlib import Path


VALID_STATUSES = ("online", "looking", "busy", "dnd", "idle", "away")
DEFAULT_STATUS = "online"
MAX_MESSAGE_LENGTH = 255


class OwnStatus:

    def __init__(self, path:Path) -> None:
        self.path = path
        self.status = DEFAULT_STATUS
        self.message = ""
        self.load()

    def load(self) -> None:
        try:
            with open(self.path, "r", encoding="utf-8") as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return
        if isinstance(data, dict):
            status = str(data.get("status", DEFAULT_STATUS)).lower()
            self.status = status if status in VALID_STATUSES else DEFAULT_STATUS
            self.message = str(data.get("message", ""))[:MAX_MESSAGE_LENGTH]

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.path.with_suffix(".tmp")
        with open(tmp_path, "w", encoding="utf-8") as file:
            json.dump({"status": self.status, "message": self.message}, file, ensure_ascii=False, indent=2)
        tmp_path.replace(self.path)

    def set(self, status:str, message:str) -> None:
        self.status = status if status in VALID_STATUSES else DEFAULT_STATUS
        self.message = message.strip()[:MAX_MESSAGE_LENGTH]
        self.save()

    def is_default(self) -> bool:
        return self.status == DEFAULT_STATUS and not self.message


def main() -> None:
    pass


if __name__ == "__main__":
    main()

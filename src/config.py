import json
from pathlib import Path


class Config(dict):
    def __init__(self, file_path):
        path = Path(file_path).expanduser().resolve()

        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

        super().__init__(data)


def load_json_config(file_path: str) -> dict:
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data


def main() -> None:
    file_path = "config.json"
    load_json_config(file_path)


if __name__ == "__main__":
    main()
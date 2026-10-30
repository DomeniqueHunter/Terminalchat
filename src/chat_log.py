from datetime import datetime
from pathlib import Path


LOG_DIR: Path | None = None


def set_log_dir(path:Path) -> None:
    global LOG_DIR
    path.mkdir(parents=True, exist_ok=True)
    LOG_DIR = path


def logging(log_file:str, message:str, timestamp_enabled:bool=True) -> None:
    timestamp = f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] ' if timestamp_enabled else ""
    path = Path(log_file)
    if LOG_DIR is not None and not path.is_absolute():
        path = LOG_DIR / path
    with open(path, "a", encoding="utf-8") as file:
        file.write(f"{timestamp}{message}")


def main() -> None:
    logging("test.log", "Test1\n")


if __name__ == "__main__":
    main()

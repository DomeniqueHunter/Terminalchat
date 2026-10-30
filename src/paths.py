import os
import shutil
from pathlib import Path


APP_NAME = "terminalchat"
LEGACY_DIR = Path(__file__).resolve().parent


def xdg_dir(variable:str, fallback:str) -> Path:
    value = os.environ.get(variable)
    return Path(value) if value else Path.home() / fallback


def config_file() -> Path:
    override = os.environ.get("TERMINALCHAT_CONFIG")
    if override:
        return Path(override).expanduser()
    return xdg_dir("XDG_CONFIG_HOME", ".config") / APP_NAME / "config.json"


def data_dir(configured:str | None=None) -> Path:
    override = os.environ.get("TERMINALCHAT_DATA") or configured
    if override:
        return Path(override).expanduser()
    return xdg_dir("XDG_DATA_HOME", ".local/share") / APP_NAME


def move_legacy(source:Path, target:Path, label:str) -> str | None:
    if not source.exists() or source.resolve() == target.resolve():
        return None
    if target.exists():
        return f"Old {label} left in place: {source} (already exists: {target})"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(target))
    if target.is_file():
        os.chmod(target, 0o600)
    return f"Moved {label}: {source} -> {target}"


def migrate_config(target:Path) -> str | None:
    return move_legacy(LEGACY_DIR / "config.json", target, "config")


def migrate_data(target:Path) -> str | None:
    return move_legacy(LEGACY_DIR / "chats", target / "chats", "chat logs")


def main() -> None:
    print("config:", config_file())
    print("data:", data_dir())


if __name__ == "__main__":
    main()

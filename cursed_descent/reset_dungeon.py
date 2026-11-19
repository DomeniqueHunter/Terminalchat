import argparse
import shutil
from pathlib import Path

from cursed_descent.config import (
    BANK_FILE_NAME, BOUTIQUE_FILE_NAME, FARM_FILE_NAME, LEADERBOARD_FILE_NAME,
    ACCOUNT_DB_NAME, ACCOUNTS_DIR_NAME, NPC_DIR_NAME,
    REMAINS_FILE_NAME, SHOPS_DIR_NAME,
)


WORLD_FILES = (REMAINS_FILE_NAME, BOUTIQUE_FILE_NAME, SHOPS_DIR_NAME,
               FARM_FILE_NAME)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reset the dungeon: remains, skeletons, consorts, "
                    "boutique, butcher, farm, lodges and Velvet's stock.")
    parser.add_argument("--data", type=Path, default=Path("game_data"))
    parser.add_argument("--leaderboard", action="store_true",
                        help="also wipe the leaderboard")
    parser.add_argument("--players", action="store_true",
                        help="also delete all player characters (accounts "
                             "and serial keys stay)")
    parser.add_argument("--npcs", action="store_true",
                        help="delete all NPCs (they are created fresh from "
                             "their prototypes at the next start)")
    parser.add_argument("--all", action="store_true",
                        help="wipe everything (same as both flags)")
    parser.add_argument("--yes", action="store_true",
                        help="do not ask for confirmation")
    return parser.parse_args()


def targets(args:argparse.Namespace) -> list[Path]:
    paths = [args.data / name for name in WORLD_FILES]
    if args.leaderboard or args.all:
        paths.append(args.data / LEADERBOARD_FILE_NAME)
    if args.players or args.all:
        paths.append(args.data / BANK_FILE_NAME)
    if args.npcs or args.all:
        paths.append(args.data / NPC_DIR_NAME)
    return [path for path in paths if path.exists()]


def confirm(paths:list[Path]) -> bool:
    print("This will delete:")
    for path in paths:
        print(f"  {path}")
    return input("Type 'reset' to continue: ").strip() == "reset"


def wipe_characters(data:Path, humans:bool) -> int:
    from cursed_descent.accounts import AccountStore
    from cursed_descent.storage import PlayerRepository
    if not (data / ACCOUNTS_DIR_NAME / ACCOUNT_DB_NAME).exists():
        return 0
    store = AccountStore(data)
    rows = store.characters(humans)
    for row in rows:
        PlayerRepository.file_for(
            type("Dirs", (), {"accounts_dir": data / ACCOUNTS_DIR_NAME,
                              "npc_dir": data / NPC_DIR_NAME})(),
            row["id"], row["account_id"]).unlink(missing_ok=True)
        store.remove_character(row["id"])
    store.close()
    return len(rows)


def remove(path:Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()


def main() -> None:
    args = parse_args()
    paths = targets(args)
    if not paths and not (args.players or args.npcs or args.all):
        print(f"Nothing to reset in {args.data}.")
        return
    if not args.yes and not confirm(paths):
        print("Aborted.")
        return
    for path in paths:
        remove(path)
        print(f"Deleted {path}")
    if args.players or args.all:
        print(f"Removed {wipe_characters(args.data, True)} characters.")
    if args.npcs or args.all:
        print(f"Removed {wipe_characters(args.data, False)} NPC records.")
    print("The dungeon is fresh again. Characters were "
          f"{'deleted' if args.players or args.all else 'kept'}.")


if __name__ == "__main__":
    main()

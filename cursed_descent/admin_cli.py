import argparse
import getpass
import sys
import time
from pathlib import Path

from .accounts import (
    AccountError, AccountStore, ban_text, parse_duration,
)
from .config import TEMP_ADMIN_SECONDS


REFRESH_WAIT_SECONDS = 5.0


def parse_args(argv:list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="admin", description="Cursed Descent account administration")
    parser.add_argument("--data", type=Path, default=Path("game_data"))
    sub = parser.add_subparsers(dest="command", required=True)
    serial = sub.add_parser("serial", help="create serial keys")
    serial.add_argument("count", type=int, nargs="?", default=1)
    sub.add_parser("serials", help="list serial keys")
    sub.add_parser("accounts", help="list accounts")
    reset = sub.add_parser("password", help="set a new password")
    reset.add_argument("name")
    reset.add_argument("--password", default=None)
    refresh = sub.add_parser("refresh", help="reload characters from disk "
                             "in the running server")
    refresh.add_argument("name", nargs="?", default="")
    refresh.add_argument("--all", action="store_true")
    refresh.add_argument("--npcs", action="store_true")
    admin = sub.add_parser("admin", help="temporary admin rights")
    admin.add_argument("name")
    admin.add_argument("--seconds", type=int, default=TEMP_ADMIN_SECONDS)
    admin.add_argument("--revoke", action="store_true")
    kick = sub.add_parser("kick", help="disconnect an account now")
    kick.add_argument("name")
    ban = sub.add_parser("ban", help="ban an account for a time")
    ban.add_argument("name")
    ban.add_argument("duration", help="30m, 2h, 7d or perm")
    ban.add_argument("reason", nargs="*", default=[])
    unban = sub.add_parser("unban", help="lift a ban")
    unban.add_argument("name")
    sub.add_parser("bans", help="list active bans")
    return parser.parse_args(argv)


def show_serials(store:AccountStore) -> None:
    for row in store.serials():
        state = f"used by {row['used_by']}" if row["used_by"] else "free"
        print(f"{row['key']}  {state}")


def show_accounts(store:AccountStore) -> None:
    for account in store.accounts():
        chars = ", ".join(row["handle"]
                          for row in store.characters_of(account.id))
        flag = " [admin]" if account.admin else ""
        print(f"{account.name}{flag}: {chars or '-'}")


def show_bans(store:AccountStore) -> None:
    bans = store.bans()
    for account in bans:
        print(f"{account.name}: {ban_text(account)}")
    if not bans:
        print("No active bans.")


def queue(store:AccountStore, scope:str, target:str="") -> int:
    request = store.request_refresh(scope, target)
    deadline = time.time() + REFRESH_WAIT_SECONDS
    while time.time() < deadline:
        result = store.refresh_result(request)
        if result is not None:
            print(result)
            return 0
        time.sleep(0.25)
    print("Queued, but the server did not answer in time. Is it running? "
          "It applies the request as soon as it is.", file=sys.stderr)
    return 1


def kick(store:AccountStore, name:str) -> int:
    account = store.by_name(name)
    if account is None:
        print(f"No account named {name}.", file=sys.stderr)
        return 1
    if account.admin:
        print("Admins cannot be kicked.", file=sys.stderr)
        return 1
    return queue(store, "kick", account.name)


def refresh(args:argparse.Namespace, store:AccountStore) -> int:
    if args.all:
        scope, target = "all", ""
    elif args.npcs:
        scope, target = "npcs", ""
    elif args.name:
        scope, target = "account", args.name
        if store.by_name(args.name) is None:
            print(f"No account named {args.name}.", file=sys.stderr)
            return 1
    else:
        print("Give an account name, --npcs or --all.", file=sys.stderr)
        return 1
    return queue(store, scope, target)


def run(args:argparse.Namespace, store:AccountStore) -> int:
    if args.command == "serial":
        for key in store.new_serials(args.count):
            print(key)
    elif args.command == "serials":
        show_serials(store)
    elif args.command == "accounts":
        show_accounts(store)
    elif args.command == "password":
        password = args.password or getpass.getpass("New password: ")
        if not store.set_password(args.name, password):
            print(f"No account named {args.name}.", file=sys.stderr)
            return 1
        print("Password changed, all sessions of the account ended.")
    elif args.command == "refresh":
        return refresh(args, store)
    elif args.command == "kick":
        return kick(store, args.name)
    elif args.command == "ban":
        seconds = parse_duration(args.duration)
        if not store.ban(args.name, seconds, " ".join(args.reason)):
            print(f"No account named {args.name}.", file=sys.stderr)
            return 1
        print(ban_text(store.by_name(args.name)))
        queue(store, "kick", args.name)
    elif args.command == "unban":
        if not store.unban(args.name):
            print(f"No account named {args.name}.", file=sys.stderr)
            return 1
        print(f"{args.name} is no longer banned.")
    elif args.command == "bans":
        show_bans(store)
    elif args.command == "admin":
        seconds = 0 if args.revoke else args.seconds
        if not store.set_admin(args.name, seconds):
            print(f"No account named {args.name}.", file=sys.stderr)
            return 1
        print("Admin rights revoked." if args.revoke else
              f"{args.name} is admin for {seconds // 60} minutes "
              "(also ends on server restart).")
    return 0


def main(argv:list[str] | None=None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    store = AccountStore(args.data)
    try:
        return run(args, store)
    except AccountError as error:
        print(error, file=sys.stderr)
        return 1
    finally:
        store.close()


if __name__ == "__main__":
    raise SystemExit(main())

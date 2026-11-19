import hashlib
import hmac
import re
import secrets
import sqlite3
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

from .config import (
    ACCOUNT_DB_NAME, ACCOUNT_NAME_LENGTH, ACCOUNTS_DIR_NAME,
    MIN_PASSWORD_LENGTH, SESSION_DAYS, TEMP_ADMIN_SECONDS,
)


SERIAL_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
SERIAL_GROUPS = 4
SERIAL_GROUP_LENGTH = 4
NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 _.-]*$")
SCRYPT = {"n": 2 ** 14, "r": 8, "p": 1}

SCHEMA = """
CREATE TABLE IF NOT EXISTS accounts (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE COLLATE NOCASE,
    salt BLOB NOT NULL,
    hash BLOB NOT NULL,
    admin_until REAL NOT NULL DEFAULT 0,
    created REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS serials (
    key TEXT PRIMARY KEY,
    created REAL NOT NULL,
    used_by TEXT,
    used_at REAL
);
CREATE TABLE IF NOT EXISTS characters (
    id TEXT PRIMARY KEY,
    account_id TEXT,
    handle TEXT NOT NULL,
    key TEXT NOT NULL UNIQUE,
    npc INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS characters_account ON characters (account_id);
CREATE TABLE IF NOT EXISTS refreshes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scope TEXT NOT NULL,
    target TEXT NOT NULL DEFAULT '',
    created REAL NOT NULL,
    result TEXT
);
CREATE TABLE IF NOT EXISTS sessions (
    token_hash TEXT PRIMARY KEY,
    account_id TEXT NOT NULL,
    expires REAL NOT NULL
);
"""


PERMANENT_BAN = 2 ** 60
DURATION_UNITS = {"m": 60, "h": 3600, "d": 86400}
DURATION_PATTERN = re.compile(r"^(\d+)([mhd])$")


class AccountError(ValueError):
    pass


@dataclass(frozen=True)
class Account:
    id: str
    name: str
    admin: bool
    banned_until: float = 0.0
    ban_reason: str = ""

    @property
    def banned(self) -> bool:
        return self.banned_until > time.time()


def parse_duration(text:str) -> int:
    text = text.strip().lower()
    if text in ("perm", "permanent"):
        return PERMANENT_BAN
    match = DURATION_PATTERN.match(text)
    if match is None or int(match.group(1)) < 1:
        raise AccountError("Duration looks like 30m, 2h, 7d or perm.")
    return int(match.group(1)) * DURATION_UNITS[match.group(2)]


def ban_text(account:Account) -> str:
    reason = f" ({account.ban_reason})" if account.ban_reason else ""
    if account.banned_until >= PERMANENT_BAN:
        return f"This account is banned permanently{reason}."
    until = time.strftime("%d.%m. %H:%M",
                          time.localtime(account.banned_until))
    return f"This account is banned until {until}{reason}."


def hash_password(password:str, salt:bytes) -> bytes:
    return hashlib.scrypt(password.encode("utf-8"), salt=salt, **SCRYPT)


def normalize_serial(text:str) -> str:
    return re.sub(r"[^A-Z0-9]", "", text.upper())


def format_serial(raw:str) -> str:
    size = SERIAL_GROUP_LENGTH
    return "-".join(raw[index:index + size]
                    for index in range(0, len(raw), size))


class AccountStore:
    def __init__(self, data_path:Path) -> None:
        folder = data_path / ACCOUNTS_DIR_NAME
        folder.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(folder / ACCOUNT_DB_NAME,
                                  check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.executescript(SCHEMA)
        self.migrate()

    def migrate(self) -> None:
        columns = {row["name"] for row in
                   self.db.execute("PRAGMA table_info(accounts)")}
        with self.db:
            if "banned_until" not in columns:
                self.db.execute("ALTER TABLE accounts ADD COLUMN "
                                "banned_until REAL NOT NULL DEFAULT 0")
            if "ban_reason" not in columns:
                self.db.execute("ALTER TABLE accounts ADD COLUMN "
                                "ban_reason TEXT NOT NULL DEFAULT ''")

    def close(self) -> None:
        self.db.close()

    def new_serials(self, count:int=1) -> list[str]:
        keys = []
        for _ in range(count):
            raw = "".join(secrets.choice(SERIAL_ALPHABET) for _ in range(
                SERIAL_GROUPS * SERIAL_GROUP_LENGTH))
            self.db.execute("INSERT INTO serials (key, created) VALUES "
                            "(?, ?)", (raw, time.time()))
            keys.append(format_serial(raw))
        self.db.commit()
        return keys

    def serials(self) -> list[dict]:
        rows = self.db.execute(
            "SELECT s.key, s.created, s.used_at, a.name AS used_by "
            "FROM serials s LEFT JOIN accounts a ON a.id = s.used_by "
            "ORDER BY s.created, s.key").fetchall()
        return [{**dict(row), "key": format_serial(row["key"])}
                for row in rows]

    def register(self, serial:str, name:str, password:str) -> Account:
        name = name.strip()
        low, high = ACCOUNT_NAME_LENGTH
        if not low <= len(name) <= high or not NAME_PATTERN.match(name):
            raise AccountError(
                f"The account name needs {low}-{high} letters, digits, "
                f"space, dot, dash or underscore.")
        if len(password) < MIN_PASSWORD_LENGTH:
            raise AccountError(f"The password needs at least "
                               f"{MIN_PASSWORD_LENGTH} characters.")
        key = normalize_serial(serial)
        account_id = str(uuid.uuid4())
        salt = secrets.token_bytes(16)
        digest = hash_password(password, salt)
        now = time.time()
        try:
            with self.db:
                taken = self.db.execute(
                    "UPDATE serials SET used_by = ?, used_at = ? "
                    "WHERE key = ? AND used_by IS NULL",
                    (account_id, now, key)).rowcount
                if not taken:
                    raise AccountError("This serial key is not valid.")
                self.db.execute(
                    "INSERT INTO accounts (id, name, salt, hash, created) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (account_id, name, salt, digest, now))
        except sqlite3.IntegrityError:
            raise AccountError("This account name is already taken.")
        return Account(account_id, name, False)

    def account_of(self, row) -> Account:
        return Account(row["id"], row["name"],
                       row["admin_until"] > time.time(),
                       row["banned_until"], row["ban_reason"])

    def by_name(self, name:str) -> Account | None:
        row = self.db.execute("SELECT * FROM accounts WHERE name = ?",
                              (name.strip(),)).fetchone()
        return self.account_of(row) if row else None

    def by_id(self, account_id:str) -> Account | None:
        row = self.db.execute("SELECT * FROM accounts WHERE id = ?",
                              (account_id,)).fetchone()
        return self.account_of(row) if row else None

    def login(self, name:str, password:str) -> Account | None:
        row = self.db.execute("SELECT * FROM accounts WHERE name = ?",
                              (name.strip(),)).fetchone()
        if row is None:
            hash_password(password, b"0" * 16)
            return None
        digest = hash_password(password, row["salt"])
        if not hmac.compare_digest(digest, row["hash"]):
            return None
        return self.account_of(row)

    def accounts(self) -> list[Account]:
        rows = self.db.execute("SELECT * FROM accounts ORDER BY name")
        return [self.account_of(row) for row in rows.fetchall()]

    def set_password(self, name:str, password:str) -> bool:
        if len(password) < MIN_PASSWORD_LENGTH:
            raise AccountError(f"The password needs at least "
                               f"{MIN_PASSWORD_LENGTH} characters.")
        salt = secrets.token_bytes(16)
        with self.db:
            changed = self.db.execute(
                "UPDATE accounts SET salt = ?, hash = ? WHERE name = ?",
                (salt, hash_password(password, salt), name.strip())).rowcount
            if changed:
                self.db.execute(
                    "DELETE FROM sessions WHERE account_id = (SELECT id "
                    "FROM accounts WHERE name = ?)", (name.strip(),))
        return bool(changed)

    def set_admin(self, name:str, seconds:int=TEMP_ADMIN_SECONDS) -> bool:
        until = time.time() + seconds if seconds > 0 else 0
        with self.db:
            return bool(self.db.execute(
                "UPDATE accounts SET admin_until = ? WHERE name = ?",
                (until, name.strip())).rowcount)

    def ban(self, name:str, seconds:int, reason:str="") -> bool:
        account = self.by_name(name)
        if account is None:
            return False
        if account.admin:
            raise AccountError("Admins cannot be banned.")
        with self.db:
            self.db.execute(
                "UPDATE accounts SET banned_until = ?, ban_reason = ? "
                "WHERE id = ?",
                (min(time.time() + seconds, PERMANENT_BAN), reason.strip(),
                 account.id))
            self.db.execute("DELETE FROM sessions WHERE account_id = ?",
                            (account.id,))
        return True

    def unban(self, name:str) -> bool:
        with self.db:
            return bool(self.db.execute(
                "UPDATE accounts SET banned_until = 0, ban_reason = '' "
                "WHERE name = ?", (name.strip(),)).rowcount)

    def bans(self) -> list[Account]:
        return [account for account in self.accounts() if account.banned]

    def end_sessions(self, name:str) -> bool:
        account = self.by_name(name)
        if account is None:
            return False
        with self.db:
            self.db.execute("DELETE FROM sessions WHERE account_id = ?",
                            (account.id,))
        return True

    def clear_admins(self) -> None:
        with self.db:
            self.db.execute("UPDATE accounts SET admin_until = 0")

    def start_session(self, account_id:str) -> str:
        token = secrets.token_urlsafe(32)
        expires = time.time() + SESSION_DAYS * 86400
        with self.db:
            self.db.execute("DELETE FROM sessions WHERE expires < ?",
                            (time.time(),))
            self.db.execute("INSERT INTO sessions VALUES (?, ?, ?)",
                            (hashlib.sha256(token.encode()).hexdigest(),
                             account_id, expires))
        return token

    def session_account(self, token:str) -> Account | None:
        if not token:
            return None
        row = self.db.execute(
            "SELECT account_id FROM sessions WHERE token_hash = ? "
            "AND expires > ?", (hashlib.sha256(token.encode()).hexdigest(),
                                time.time())).fetchone()
        return self.by_id(row["account_id"]) if row else None

    def end_session(self, token:str) -> None:
        with self.db:
            self.db.execute("DELETE FROM sessions WHERE token_hash = ?",
                            (hashlib.sha256(token.encode()).hexdigest(),))

    def add_character(self, char_id:str, account_id:str | None,
                      handle:str, key:str, npc:bool) -> None:
        with self.db:
            self.db.execute(
                "INSERT INTO characters (id, account_id, handle, key, npc) "
                "VALUES (?, ?, ?, ?, ?) ON CONFLICT(id) DO UPDATE SET "
                "account_id = excluded.account_id, handle = excluded.handle, "
                "key = excluded.key, npc = excluded.npc",
                (char_id, account_id, handle, key, int(npc)))

    def remove_character(self, char_id:str) -> None:
        with self.db:
            self.db.execute("DELETE FROM characters WHERE id = ?",
                            (char_id,))

    def character_by_key(self, key:str):
        return self.db.execute("SELECT * FROM characters WHERE key = ?",
                               (key,)).fetchone()

    def character_by_id(self, char_id:str):
        return self.db.execute("SELECT * FROM characters WHERE id = ?",
                               (char_id,)).fetchone()

    def characters(self, humans:bool | None=None) -> list:
        query = "SELECT * FROM characters"
        if humans is True:
            query += " WHERE account_id IS NOT NULL AND npc = 0"
        elif humans is False:
            query += " WHERE account_id IS NULL OR npc != 0"
        return self.db.execute(query + " ORDER BY key").fetchall()

    def request_refresh(self, scope:str, target:str="") -> int:
        with self.db:
            self.db.execute("DELETE FROM refreshes WHERE created < ?",
                            (time.time() - 3600,))
            cursor = self.db.execute(
                "INSERT INTO refreshes (scope, target, created) "
                "VALUES (?, ?, ?)", (scope, target, time.time()))
        return cursor.lastrowid

    def open_refreshes(self) -> list:
        return self.db.execute(
            "SELECT * FROM refreshes WHERE result IS NULL ORDER BY id"
        ).fetchall()

    def finish_refresh(self, request_id:int, result:str) -> None:
        with self.db:
            self.db.execute("UPDATE refreshes SET result = ? WHERE id = ?",
                            (result, request_id))

    def refresh_result(self, request_id:int) -> str | None:
        row = self.db.execute("SELECT result FROM refreshes WHERE id = ?",
                              (request_id,)).fetchone()
        return row["result"] if row else None

    def characters_of(self, account_id:str) -> list:
        return self.db.execute(
            "SELECT * FROM characters WHERE account_id = ? ORDER BY key",
            (account_id,)).fetchall()

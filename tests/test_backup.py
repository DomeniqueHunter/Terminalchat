import io
import sqlite3
import subprocess
from pathlib import Path

from cursed_descent.backup import create, restore


def make_data(folder:Path) -> None:
    (folder / "players").mkdir(parents=True)
    (folder / "players" / "kerl.json").write_text('{"gold": 5}')
    (folder / "world.json").write_text('{"day": 3}')
    db = sqlite3.connect(folder / "accounts.db")
    db.execute("CREATE TABLE t (x INTEGER)")
    db.execute("INSERT INTO t VALUES (7)")
    db.commit()
    db.close()


def test_backup_roundtrip(tmp_path:Path) -> None:
    source = tmp_path / "source"
    make_data(source)
    stream = io.BytesIO()
    assert create(source, stream) == 3
    (source / "world.json").write_text('{"day": 99}')
    (source / "players" / "kerl.json").unlink()
    (source / "junk.txt").write_text("new")
    sqlite3.connect(source / "accounts.db").execute(
        "DELETE FROM t").connection.commit()
    stream.seek(0)
    restore(source, stream)
    assert (source / "world.json").read_text() == '{"day": 3}'
    assert (source / "players" / "kerl.json").exists()
    assert not (source / "junk.txt").exists()
    assert not (source / ".restore_tmp").exists()
    rows = sqlite3.connect(source / "accounts.db").execute(
        "SELECT x FROM t").fetchall()
    assert rows == [(7,)]


def test_backup_skips_wal_side_files(tmp_path:Path) -> None:
    make_data(tmp_path)
    (tmp_path / "accounts.db-wal").write_text("x")
    assert create(tmp_path, io.BytesIO()) == 3


def test_console_script_is_valid_bash() -> None:
    script = Path(__file__).parent.parent / "console.sh"
    assert subprocess.run(["bash", "-n", str(script)]).returncode == 0

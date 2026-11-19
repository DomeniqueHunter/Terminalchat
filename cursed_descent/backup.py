import argparse
import shutil
import sqlite3
import sys
import tarfile
import tempfile
from pathlib import Path
from typing import BinaryIO


DB_SUFFIXES = (".db", ".sqlite", ".sqlite3")
SIDE_SUFFIXES = ("-wal", "-shm", "-journal")
SCRATCH_NAME = ".restore_tmp"


def is_database(path:Path) -> bool:
    return path.suffix in DB_SUFFIXES


def is_side_file(path:Path) -> bool:
    return path.name.endswith(SIDE_SUFFIXES)


def snapshot(source:Path, target:Path) -> None:
    origin = sqlite3.connect(source)
    copy = sqlite3.connect(target)
    try:
        origin.backup(copy)
    finally:
        copy.close()
        origin.close()


def create(data:Path, stream:BinaryIO) -> int:
    count = 0
    with tempfile.TemporaryDirectory() as scratch:
        with tarfile.open(fileobj=stream, mode="w|gz") as archive:
            for path in sorted(data.rglob("*")):
                if not path.is_file() or is_side_file(path):
                    continue
                name = path.relative_to(data).as_posix()
                if is_database(path):
                    copy = Path(scratch) / f"{count}.db"
                    snapshot(path, copy)
                    archive.add(copy, arcname=name)
                else:
                    archive.add(path, arcname=name)
                count += 1
    return count


def clear(data:Path) -> None:
    for entry in data.iterdir():
        if entry.name == SCRATCH_NAME:
            continue
        if entry.is_dir() and not entry.is_symlink():
            shutil.rmtree(entry)
        else:
            entry.unlink()


def restore(data:Path, stream:BinaryIO) -> int:
    data.mkdir(parents=True, exist_ok=True)
    scratch = data / SCRATCH_NAME
    shutil.rmtree(scratch, ignore_errors=True)
    scratch.mkdir()
    try:
        with tarfile.open(fileobj=stream, mode="r|gz") as archive:
            archive.extractall(scratch, filter="data")
        found = list(scratch.rglob("*"))
        clear(data)
        for entry in scratch.iterdir():
            shutil.move(str(entry), data / entry.name)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    return sum(1 for entry in found if entry.is_file())


def parse_args(argv:list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="backup")
    parser.add_argument("command", choices=["create", "restore"])
    parser.add_argument("--data", type=Path, default=Path("game_data"))
    return parser.parse_args(argv)


def main(argv:list[str] | None=None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.command == "create":
        count = create(args.data, sys.stdout.buffer)
    else:
        count = restore(args.data, sys.stdin.buffer)
    print(f"{args.command}: {count} files", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

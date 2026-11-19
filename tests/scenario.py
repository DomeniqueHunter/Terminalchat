import hashlib
import importlib
import itertools
import random
import shutil
import tempfile
import uuid
from pathlib import Path
from unittest import mock

from tests.fixture_data import build
from tests.ready import confirm


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "game_data"
PLAYER_NAMES = ("kerl", "galactica", "gianna_morningwood",
                "beverley_morningwood")
CHUNK_SIZE = 50
FROZEN_TIME = "2026-01-01 12:00"


class FixedUuid:
    def __init__(self, number:int) -> None:
        self.hex = f"{number:032x}"

    def __str__(self) -> str:
        return self.hex


def run_scenario(package:str="cursed_descent", steps:int=1500,
                 seed:int=7) -> list[str]:
    controller_module = importlib.import_module(f"{package}.controller")
    with tempfile.TemporaryDirectory() as tmp:
        data_path = Path(tmp) / "game_data"
        build(data_path)
        random.seed(seed)
        controller = controller_module.GameController(data_path)
        controller.town.visits_on = False
        clock = importlib.import_module(f"{package}.clock")
        clock.FROZEN = FROZEN_TIME
        counter = itertools.count()
        try:
            with mock.patch.object(uuid, "uuid4",
                                   lambda: FixedUuid(next(counter))):
                return play(controller, steps, random.Random(seed + 1))
        finally:
            clock.FROZEN = ""


def play(controller, steps:int, chooser:random.Random) -> list[str]:
    transcript: list[str] = []
    session = controller.session
    now = 0.0

    def record(messages) -> None:
        for message in messages:
            transcript.append(f"{message.recipient}|{message.text}")

    for step in range(steps):
        now += 1000.0
        if session.state == "idle":
            record(controller.handle(PLAYER_NAMES[0], "!lobby", now))
            for name in PLAYER_NAMES[1:]:
                record(controller.handle(name, "!join", now))
            record(controller.handle(PLAYER_NAMES[0], "!start", now))
            record(confirm(controller, now))
            continue
        if session.state == "paused":
            record(controller.handle(PLAYER_NAMES[0], "!resume", now))
            continue
        living = session.living()
        if not living:
            record(controller.handle(PLAYER_NAMES[0], "!force", now))
            continue
        if session.state == "combat":
            for player in living:
                command = chooser.choice(["!hit", "!hit", "!dodge", "!guard"])
                record(controller.handle(player.name, command, now))
        else:
            options = session.available_commands()
            if not options or chooser.random() < 0.25:
                record(controller.handle(living[0].name, "!force", now))
            else:
                command = f"!{chooser.choice(options)}"
                record(controller.handle(living[0].name, command, now))
        record(controller.tick(now))
    return transcript


def fingerprint(transcript:list[str]) -> dict:
    chunks = [
        hashlib.sha256("\n".join(transcript[start:start + CHUNK_SIZE])
                       .encode("utf-8")).hexdigest()
        for start in range(0, len(transcript), CHUNK_SIZE)
    ]
    return {"messages": len(transcript), "chunk_size": CHUNK_SIZE,
            "chunks": chunks}

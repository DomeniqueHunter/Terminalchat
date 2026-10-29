import asyncio
import os
import re
import time
from dataclasses import dataclass
from email.utils import formatdate
from pathlib import Path
from urllib.parse import quote

import aiohttp
from PIL import Image as PILImage
from PIL import ImageSequence

from chat_log import logging


EICON_URL = "https://static.f-list.net/images/eicon/{name}.gif"
EICON_PATTERN = re.compile(r"\[eicon\](.*?)\[/eicon\]", re.IGNORECASE)
NOPARSE_PATTERN = re.compile(r"\[noparse\].*?\[/noparse\]", re.IGNORECASE)
MAX_PER_MESSAGE = 36
TIMEOUT_SECONDS = 15
MAX_FRAMES = 60
MIN_FRAME_MS = 50
DEFAULT_FRAME_MS = 100

UPDATED = "updated"
UNCHANGED = "unchanged"
GONE = "gone"
FAILED = "failed"


@dataclass
class Eicon:
    frames: list[PILImage.Image]
    durations: list[int]


def eicon_url(name:str) -> str:
    return EICON_URL.format(name=quote(name.strip().lower(), safe=""))


def extract_eicons(text:str) -> list[str]:
    text = NOPARSE_PATTERN.sub("", text)
    names = [name.strip() for name in EICON_PATTERN.findall(text) if name.strip()]
    return names[:MAX_PER_MESSAGE]


def default_cache_dir() -> Path:
    base = os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache"
    return Path(base) / "terminalchat" / "eicons"


class EiconCache:

    def __init__(self, cache_dir:Path | None=None, max_age_hours:float=24) -> None:
        self.cache_dir = cache_dir or default_cache_dir()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_age = max_age_hours * 3600
        self.images: dict[str, tuple[Eicon | None, float]] = {}
        self.tasks: dict[str, asyncio.Task] = {}
        self.session: aiohttp.ClientSession | None = None

    def file_path(self, name:str) -> Path:
        return self.cache_dir / f"{quote(name.strip().lower(), safe='')}.gif"

    async def get(self, name:str) -> Eicon | None:
        key = name.strip().lower()
        cached = self.images.get(key)
        if cached is not None and time.monotonic() - cached[1] < self.max_age:
            return cached[0]
        if key not in self.tasks:
            self.tasks[key] = asyncio.create_task(self._load(key))
        image = await self.tasks[key]
        self.images[key] = (image, time.monotonic())
        self.tasks.pop(key, None)
        return image

    async def _load(self, name:str) -> Eicon | None:
        path = self.file_path(name)
        if path.exists():
            if time.time() - path.stat().st_mtime > self.max_age:
                if await self._fetch(name, path, path.stat().st_mtime) == GONE:
                    path.unlink(missing_ok=True)
                    return None
        elif await self._fetch(name, path) != UPDATED:
            return None
        try:
            return await asyncio.to_thread(load_frames, path)
        except Exception as error:
            logging("debug.log", f"eicon {name} unreadable: {error!r}\n")
            return None

    async def _fetch(self, name:str, path:Path, since:float | None=None) -> str:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=TIMEOUT_SECONDS))
        headers = {"If-Modified-Since": formatdate(since, usegmt=True)} if since else {}
        try:
            async with self.session.get(eicon_url(name), headers=headers) as response:
                if response.status == 304:
                    os.utime(path)
                    return UNCHANGED
                if response.status in (404, 410):
                    return GONE
                if response.status != 200:
                    return FAILED
                data = await response.read()
        except Exception as error:
            logging("debug.log", f"eicon {name} download failed: {error!r}\n")
            return FAILED
        tmp_path = path.with_suffix(".tmp")
        tmp_path.write_bytes(data)
        tmp_path.replace(path)
        return UPDATED

    async def close(self) -> None:
        if self.session is not None and not self.session.closed:
            await self.session.close()


def load_frames(path:Path) -> Eicon:
    frames: list[PILImage.Image] = []
    durations: list[int] = []
    with PILImage.open(path) as image:
        for index, frame in enumerate(ImageSequence.Iterator(image)):
            if index >= MAX_FRAMES:
                break
            frames.append(frame.convert("RGBA"))
            duration = frame.info.get("duration") or DEFAULT_FRAME_MS
            if duration < 20:
                duration = DEFAULT_FRAME_MS
            durations.append(max(duration, MIN_FRAME_MS))
    return Eicon(frames, durations)


def main() -> None:
    print(extract_eicons("hi [eicon]Wave[/eicon] [noparse][eicon]no[/eicon][/noparse] [EICON]cat hug[/EICON]"))
    print(eicon_url("cat hug"))


if __name__ == "__main__":
    main()

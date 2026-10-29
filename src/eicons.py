import asyncio
import os
import re
from pathlib import Path
from urllib.parse import quote

import aiohttp
from PIL import Image as PILImage

from chat_log import logging


EICON_URL = "https://static.f-list.net/images/eicon/{name}.gif"
EICON_PATTERN = re.compile(r"\[eicon\](.*?)\[/eicon\]", re.IGNORECASE)
NOPARSE_PATTERN = re.compile(r"\[noparse\].*?\[/noparse\]", re.IGNORECASE)
MAX_PER_MESSAGE = 36
TIMEOUT_SECONDS = 15


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

    def __init__(self, cache_dir:Path | None=None) -> None:
        self.cache_dir = cache_dir or default_cache_dir()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.images: dict[str, PILImage.Image | None] = {}
        self.tasks: dict[str, asyncio.Task] = {}
        self.session: aiohttp.ClientSession | None = None

    def file_path(self, name:str) -> Path:
        return self.cache_dir / f"{quote(name.strip().lower(), safe='')}.gif"

    async def get(self, name:str) -> PILImage.Image | None:
        key = name.strip().lower()
        if key in self.images:
            return self.images[key]
        if key not in self.tasks:
            self.tasks[key] = asyncio.create_task(self._load(key))
        image = await self.tasks[key]
        self.images[key] = image
        self.tasks.pop(key, None)
        return image

    async def _load(self, name:str) -> PILImage.Image | None:
        path = self.file_path(name)
        if not path.exists() and not await self._download(name, path):
            return None
        try:
            return await asyncio.to_thread(first_frame, path)
        except Exception as error:
            logging("debug.log", f"eicon {name} unreadable: {error!r}\n")
            return None

    async def _download(self, name:str, path:Path) -> bool:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=TIMEOUT_SECONDS))
        try:
            async with self.session.get(eicon_url(name)) as response:
                if response.status != 200:
                    return False
                data = await response.read()
        except Exception as error:
            logging("debug.log", f"eicon {name} download failed: {error!r}\n")
            return False
        tmp_path = path.with_suffix(".tmp")
        tmp_path.write_bytes(data)
        tmp_path.replace(path)
        return True

    async def close(self) -> None:
        if self.session is not None and not self.session.closed:
            await self.session.close()


def first_frame(path:Path) -> PILImage.Image:
    with PILImage.open(path) as image:
        image.seek(0)
        return image.convert("RGBA")


def main() -> None:
    print(extract_eicons("hi [eicon]Wave[/eicon] [noparse][eicon]no[/eicon][/noparse] [EICON]cat hug[/EICON]"))
    print(eicon_url("cat hug"))


if __name__ == "__main__":
    main()

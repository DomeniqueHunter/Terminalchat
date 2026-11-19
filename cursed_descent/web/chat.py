import re
import time
from collections import deque

from ..config import CHAT_BURST, CHAT_BURST_SECONDS, CHAT_MAX_LENGTH
from ..controller import GameController
from . import audience, views


CONTROL = re.compile(r"[\x00-\x1f\x7f]+")
SAY_WORDS = ("say", "s")
WHISPER_WORDS = ("w", "whisper", "tell")


WHISPER_USAGE = "Usage: !w <name>: <text>   e.g. !w Lyra Dawn: hello"


class ChatError(ValueError):
    def __init__(self, message:str, usage:str="") -> None:
        super().__init__(message)
        self.usage = usage


def clean(text:str) -> str:
    return CONTROL.sub(" ", text).strip()


def parse(text:str) -> tuple[str, str, str] | None:
    """Returns (kind, target, body) or None when the text is no chat."""
    if not text.startswith("!"):
        return ("say", "", clean(text)) if text.strip() else None
    word, _, rest = text[1:].partition(" ")
    word = word.lower()
    if word in SAY_WORDS:
        return "say", "", clean(rest)
    if word in WHISPER_WORDS:
        name, colon, body = rest.partition(":")
        if not colon:
            name, _, body = rest.strip().partition(" ")
        return "whisper", clean(name), clean(body)
    return None


def where(controller:GameController, name:str) -> tuple[str, str]:
    return audience.place_of(controller, name)


def listeners(controller:GameController, speaker:str) -> set[str]:
    return audience.place_mates(controller, speaker)


class Limiter:
    def __init__(self) -> None:
        self.sent: dict[str, deque[float]] = {}

    def allow(self, name:str, now:float | None=None) -> bool:
        now = time.monotonic() if now is None else now
        stamps = self.sent.setdefault(name, deque())
        while stamps and now - stamps[0] > CHAT_BURST_SECONDS:
            stamps.popleft()
        if len(stamps) >= CHAT_BURST:
            return False
        stamps.append(now)
        return True


def deliver(controller:GameController, speaker:str, kind:str, target:str,
            body:str) -> list[audience.Item]:
    if not body:
        raise ChatError("Say something first.",
                        WHISPER_USAGE if kind == "whisper" else "")
    if len(body) > CHAT_MAX_LENGTH:
        raise ChatError(f"Too long: at most {CHAT_MAX_LENGTH} characters.")
    if kind == "say":
        entry = {"text": f"💬 {speaker}: {body}", "kind": "chat"}
        return [(listeners(controller, speaker), entry)]
    names = audience.canonical(controller)
    found = names.get(target.casefold())
    if not found:
        raise ChatError(f"Nobody called '{target}'.", WHISPER_USAGE)
    if found == speaker:
        raise ChatError("Whispering to yourself is a bad sign.",
                        WHISPER_USAGE)
    entry = {"text": f"🤫 {speaker} → {found}: {body}", "kind": "whisper"}
    return [({speaker, found}, entry)]

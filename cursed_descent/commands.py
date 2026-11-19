from dataclasses import dataclass

from .config import COMMAND_PREFIX


ALIASES = {"h": "hit", "c": "cast", "f": "force", "d": "dodge",
           "g": "guard", "p": "potion", "e": "enter", "i": "inv",
           "s": "status"}


@dataclass(frozen=True)
class Command:
    name: str
    args: tuple[str, ...] = ()

    @property
    def argument(self) -> str:
        return " ".join(self.args)

    @property
    def text(self) -> str:
        return " ".join((f"{COMMAND_PREFIX}{self.name}",) + self.args)

    def with_args(self, *args:object) -> "Command":
        return Command(self.name, self.args + tuple(str(a) for a in args))


def command(name:str, *args:object) -> Command:
    return Command(name.lower(), tuple(str(arg) for arg in args
                                       if str(arg) != ""))


def parse_chat(text:str) -> Command | None:
    text = text.strip()
    if not text.startswith(COMMAND_PREFIX):
        return None
    parts = text[len(COMMAND_PREFIX):].split()
    if not parts:
        return None
    word = parts[0].lower()
    return Command(ALIASES.get(word, word), tuple(parts[1:]))

from collections.abc import Callable
from types import FunctionType

from .work.model import Job


CALLABLES = ("ui", "items", "round_hook", "finish_hook", "idle_hook",
             "setup", "save", "greeter", "lock", "shift_ui", "info")


class Building:
    key: str = ""
    title: str = ""
    blurb: str = ""
    label: str = ""
    greeting: str = ""
    icon: str = ""
    order: int = 100
    help: str = ""
    owner: str = ""
    place: str = ""
    closed: str = ""
    cut: float = 0.0
    jobs: tuple[Job, ...] = ()
    menu: dict = {}
    menu_title: str = ""
    dish_kg: dict = {}
    commands: dict[str, Callable] = {}
    place_commands: tuple[str, ...] = ()
    counter: object = None
    session_lines: dict[str, list[str]] = {}
    job_words: dict[str, str] = {}
    ui: Callable | None = None
    items: Callable | None = None
    round_hook: Callable | None = None
    finish_hook: Callable | None = None
    idle_hook: Callable | None = None
    setup: Callable | None = None
    save: Callable | None = None
    greeter: Callable | None = None
    lock: Callable | None = None
    shift_ui: Callable | None = None
    info: Callable | None = None
    town: str = ""
    decency: int | None = None
    reaction: str = ""

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        for name in CALLABLES:
            value = cls.__dict__.get(name)
            if isinstance(value, FunctionType):
                setattr(cls, name, staticmethod(value))

    @property
    def renamed(self) -> bool:
        owner = {name: next(klass for klass in type(self).__mro__
                            if name in vars(klass)) for name in ("key", "title")}
        return owner["key"] is not owner["title"]

    @property
    def button(self) -> str:
        return self.label or self.title

    @property
    def command(self) -> str:
        return self.key

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {self.key!r} in {self.town!r}>"

from dataclasses import dataclass


@dataclass(frozen=True)
class Button:
    label: str
    command: str
    kind: str = ""
    enabled: bool = True


@dataclass(frozen=True)
class Row:
    text: str
    buttons: tuple[Button, ...] = ()


@dataclass(frozen=True)
class Bar:
    key: str
    label: str
    value: float
    maximum: float


@dataclass(frozen=True)
class Choice:
    name: str
    label: str
    options: tuple[tuple[str, str], ...] = ()
    kind: str = "radio"
    value: str = ""


@dataclass(frozen=True)
class Panel:
    title: str
    lines: tuple[str, ...] = ()
    buttons: tuple[Button, ...] = ()
    sections: tuple["Panel", ...] = ()
    timer: str = ""
    bars: tuple[Bar, ...] = ()
    choices: tuple[Choice, ...] = ()
    rows: tuple[Row, ...] = ()
    tabbed: bool = False

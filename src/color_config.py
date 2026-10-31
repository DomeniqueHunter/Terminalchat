import os
from typing import Callable

from rich.style import Style


NO_COLOR = bool(os.environ.get("NO_COLOR"))

USER_STYLE = "bold #008080"
ICON_STYLE = "bold #008080"
EICON_STYLE = "#af5fd7"
URL_STYLE = "underline #5f87ff"
SENDER_STYLE = "bold"
SPOILER_STYLE = "reverse"
OP_STYLE = "bold"
CHANNEL_LINK_STYLE = "bold #5fafff"
RULE_STYLE = "dim"
QUOTE_STYLE = "dim"

STATUS_SYMBOLS = {
    "looking": "+",
    "online": "•",
    "idle": "~",
    "away": "~",
    "busy": "-",
    "dnd": "x",
    "crown": "*",
}

STATUS_STYLES = {
    "looking": "#55ff55",
    "online": "#008080",
    "idle": "#a8a8a8",
    "away": "#a8a8a8",
    "busy": "#ffaf00",
    "dnd": "#ff5555",
    "crown": "#ffff55",
}

GENDER_STYLES = {
    "male": "#6699ff",
    "female": "#ff6699",
    "transgender": "#ee8822",
    "herm": "#9b30ff",
    "male-herm": "#007fff",
    "cunt-boy": "#00cc66",
    "shemale": "#cc66ff",
    "none": "#ffffbb",
}

NameStyle = Callable[[str], Style]

BBCODE_COLORS = {
    "red": "#ff5555",
    "blue": "#5f87ff",
    "white": "#ffffff",
    "yellow": "#ffff55",
    "pink": "#ff87d7",
    "gray": "#a8a8a8",
    "green": "#55ff55",
    "orange": "#ffaf00",
    "purple": "#af5fff",
    "black": "#5f5f5f",
    "brown": "#af8700",
    "cyan": "#55ffff",
}


def make_style(spec:str) -> Style:
    style = Style.parse(spec)
    if not NO_COLOR:
        return style
    return Style(bold=style.bold, dim=style.dim, italic=style.italic, underline=style.underline,
                 strike=style.strike, reverse=style.reverse, link=style.link)


def gender_style(gender:str | None) -> Style:
    color = GENDER_STYLES.get((gender or "").lower())
    return make_style(color) if color else Style()


def no_name_style(name:str) -> Style:
    return Style()


def main() -> None:
    print(f"NO_COLOR={NO_COLOR} user={make_style(USER_STYLE)} url={make_style(URL_STYLE)}")


if __name__ == "__main__":
    main()

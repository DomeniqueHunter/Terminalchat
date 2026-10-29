import os

from rich.style import Style


NO_COLOR = bool(os.environ.get("NO_COLOR"))

USER_STYLE = "bold #008080"
ICON_STYLE = "bold #008080"
EICON_STYLE = "#af5fd7"
URL_STYLE = "underline #5f87ff"
SENDER_STYLE = "bold"
SPOILER_STYLE = "reverse"

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


def main() -> None:
    print(f"NO_COLOR={NO_COLOR} user={make_style(USER_STYLE)} url={make_style(URL_STYLE)}")


if __name__ == "__main__":
    main()

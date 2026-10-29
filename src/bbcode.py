import re

from rich.style import Style
from rich.text import Text

from color_config import (BBCODE_COLORS, EICON_STYLE, ICON_STYLE, SPOILER_STYLE,
                          URL_STYLE, USER_STYLE, make_style)
from eicons import eicon_url


TAG_PATTERN = re.compile(r"\[(/?)([a-zA-Z]+)(?:=([^\]]*))?\]")

SIMPLE_STYLES = {
    "b": Style(bold=True),
    "i": Style(italic=True),
    "u": Style(underline=True),
    "s": Style(strike=True),
    "sub": Style(dim=True),
    "sup": Style(dim=True),
    "spoiler": make_style(SPOILER_STYLE),
}

CONTENT_TAGS = {"user", "icon", "eicon", "url", "noparse"}


def tag_style(name:str, value:str | None) -> Style | None:
    if name in SIMPLE_STYLES:
        return SIMPLE_STYLES[name]
    if name == "color" and value:
        color = BBCODE_COLORS.get(value.lower())
        return make_style(color) if color else Style()
    return None


def render_content_tag(text:Text, name:str, value:str | None, content:str, base:Style, show_eicons:bool) -> None:
    if name == "user":
        text.append(content, base + make_style(USER_STYLE))
    elif name == "icon":
        text.append(f"[{content}]", base + make_style(ICON_STYLE))
    elif name == "eicon":
        if not show_eicons:
            return
        text.append(f":{content}:", base + make_style(EICON_STYLE) + Style(link=eicon_url(content)))
    elif name == "url":
        url = value or content
        label = content or url
        text.append(label, base + make_style(URL_STYLE) + Style(link=url))
    else:
        text.append(content, base)


def find_close(source:str, name:str, start:int) -> int:
    match = re.compile(rf"\[/{name}\]", re.IGNORECASE).search(source, start)
    return match.start() if match else -1


def to_text(source:str, show_eicons:bool=True) -> Text:
    text = Text()
    stack: list[tuple[str, Style]] = []
    position = 0

    def current() -> Style:
        style = Style()
        for _, item in stack:
            style += item
        return style

    while position < len(source):
        match = TAG_PATTERN.search(source, position)
        if match is None:
            text.append(source[position:], current())
            break

        text.append(source[position:match.start()], current())
        closing, name, value = match.group(1) == "/", match.group(2).lower(), match.group(3)
        position = match.end()

        if not closing and name in CONTENT_TAGS:
            end = find_close(source, name, position)
            if end >= 0:
                render_content_tag(text, name, value, source[position:end], current(), show_eicons)
                position = end + len(name) + 3
                continue
            text.append(match.group(0), current())
            continue

        if closing:
            index = next((i for i in range(len(stack) - 1, -1, -1) if stack[i][0] == name), None)
            if index is None:
                text.append(match.group(0), current())
            else:
                del stack[index:]
            continue

        style = tag_style(name, value)
        if style is None:
            text.append(match.group(0), current())
        else:
            stack.append((name, style))

    return text


def main() -> None:
    from rich.console import Console
    console = Console()
    for sample in [
        "Hallo [user]H-Milk[/user], schau mal [eicon]wave[/eicon] [b]fett [i]kursiv[/i][/b]",
        "[color=red]rot[/color] [color=unknown]?[/color] [url=https://f-list.net]f-list[/url]",
        "kaputt [/b] und [b]offen und [noparse][b]roh[/b][/noparse] [foo]x[/foo]",
    ]:
        console.print(to_text(sample))


if __name__ == "__main__":
    main()

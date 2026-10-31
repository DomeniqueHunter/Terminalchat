import re

from rich.style import Style
from rich.text import Text

from color_config import (BBCODE_COLORS, CHANNEL_LINK_STYLE, EICON_STYLE, ICON_STYLE, QUOTE_STYLE, RULE_STYLE,
                          SPOILER_STYLE, URL_STYLE, USER_STYLE, NameStyle, make_style, no_name_style)
from eicons import eicon_url


TAG_PATTERN = re.compile(r"\[(/?)([a-zA-Z]+)(?:=([^\]]*))?\]")

SIMPLE_STYLES = {
    "b": Style(bold=True),
    "i": Style(italic=True),
    "u": Style(underline=True),
    "s": Style(strike=True),
    "sub": Style(dim=True),
    "sup": Style(dim=True),
    "big": Style(bold=True),
    "small": Style(dim=True),
    "heading": Style(bold=True, underline=True),
}

PASSTHROUGH_TAGS = {"center", "left", "right", "justify", "indent", "collapse"}
VOID_TAGS = {"hr"}
CONTENT_TAGS = {"user", "icon", "eicon", "url", "noparse", "session", "channel", "spoiler", "quote"}
RULE = "\u2500" * 24
QUOTE_BAR = "\u2502 "
SPOILER_LABEL = " spoiler "

USER_LINK = "fchat-user:"
CHANNEL_LINK = "fchat-channel:"
SPOILER_LINK = "fchat-spoiler:"
INTERNAL_LINKS = (USER_LINK, CHANNEL_LINK, SPOILER_LINK)


def tag_style(name:str, value:str | None) -> Style | None:
    if name in SIMPLE_STYLES:
        return SIMPLE_STYLES[name]
    if name in PASSTHROUGH_TAGS:
        return Style()
    if name == "color" and value:
        color = BBCODE_COLORS.get(value.lower())
        return make_style(color) if color else Style()
    return None


def append_quote(text:Text, quoted:Text, base:Style, author:str | None) -> None:
    if text.plain and not text.plain.endswith("\n"):
        text.append("\n")
    bar = base + make_style(QUOTE_STYLE)
    if author:
        text.append(QUOTE_BAR, bar)
        text.append(f"{author} wrote:", bar + Style(italic=True))
        text.append("\n")
    for line in quoted.split("\n"):
        text.append(QUOTE_BAR, bar)
        text.append_text(line)
        text.append("\n")


def render_content_tag(text:Text, name:str, value:str | None, content:str, base:Style, show_eicons:bool,
                       name_style:NameStyle, reveal_spoilers:bool) -> None:
    if name == "user":
        text.append(content, base + make_style(USER_STYLE) + name_style(content) + Style(link=USER_LINK + content.strip()))
    elif name == "icon":
        text.append(f"[{content}]", base + make_style(ICON_STYLE) + name_style(content) + Style(link=USER_LINK + content.strip()))
    elif name == "eicon":
        if not show_eicons:
            return
        text.append(f":{content}:", base + make_style(EICON_STYLE) + Style(link=eicon_url(content)))
    elif name == "session":
        link = Style(link=CHANNEL_LINK + content.strip())
        text.append(f"#{value or content}", base + make_style(CHANNEL_LINK_STYLE) + link)
    elif name == "channel":
        text.append(f"#{content}", base + make_style(CHANNEL_LINK_STYLE) + Style(link=CHANNEL_LINK + content.strip()))
    elif name == "spoiler":
        if reveal_spoilers:
            part = Text(style=base)
            part.append_text(to_text(content, show_eicons, name_style, True))
            text.append_text(part)
        else:
            text.append(SPOILER_LABEL, base + make_style(SPOILER_STYLE) + Style(link=SPOILER_LINK))
    elif name == "quote":
        quoted = Text(style=base)
        quoted.append_text(to_text(content.strip("\n"), show_eicons, name_style, reveal_spoilers))
        append_quote(text, quoted, base, value)
    elif name == "url":
        url = value or content
        label = content or url
        text.append(label, base + make_style(URL_STYLE) + Style(link=url))
    else:
        text.append(content, base)


def find_close(source:str, name:str, start:int) -> int:
    match = re.compile(rf"\[/{name}\]", re.IGNORECASE).search(source, start)
    return match.start() if match else -1


def to_text(source:str, show_eicons:bool=True, name_style:NameStyle | None=None, reveal_spoilers:bool=False) -> Text:
    name_style = name_style or no_name_style
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
                render_content_tag(text, name, value, source[position:end], current(), show_eicons, name_style,
                                   reveal_spoilers)
                position = end + len(name) + 3
                if name == "quote" and source.startswith("\n", position):
                    position += 1
                continue
            text.append(match.group(0), current())
            continue

        if name in VOID_TAGS:
            if not closing:
                text.append(RULE, make_style(RULE_STYLE))
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

    if text.plain.endswith("\n") and not source.endswith("\n"):
        text.right_crop(1)
    return text


def main() -> None:
    from rich.console import Console
    console = Console()
    for sample in [
        "Hallo [user]H-Milk[/user], schau mal [eicon]wave[/eicon] [b]fett [i]kursiv[/i][/b]",
        "[color=red]rot[/color] [color=unknown]?[/color] [url=https://f-list.net]f-list[/url]",
        "kaputt [/b] und [b]offen und [noparse][b]roh[/b][/noparse] [foo]x[/foo]",
        "Geheim: [spoiler]der [b]Butler[/b][/spoiler] war es",
        "[quote=Alice]zeile eins\n[i]zeile zwei[/i][/quote]\nmeine Antwort",
        "komm in [session=Mein Raum]ADH-123[/session] oder [channel]Development[/channel]",
    ]:
        console.print(to_text(sample))
        console.print(to_text(sample, reveal_spoilers=True))


if __name__ == "__main__":
    main()

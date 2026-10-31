from textual.binding import Binding
from textual.widgets import TextArea


FORMAT_TAGS = {"b": "b", "i": "i", "u": "u", "s": "s", "p": "spoiler", "q": "quote"}


class BBCodeArea(TextArea):

    BINDINGS = [Binding(f"alt+{key}", f"wrap('{tag}')", show=False) for key, tag in FORMAT_TAGS.items()]

    def action_wrap(self, tag:str) -> None:
        start, end = sorted(self.selection)
        selected = self.selected_text
        opening, closing = f"[{tag}]", f"[/{tag}]"
        result = self.replace(f"{opening}{selected}{closing}", start, end)
        if selected:
            self.move_cursor(result.end_location)
        else:
            row, column = result.end_location
            self.move_cursor((row, column - len(closing)))


def main() -> None:
    print(", ".join(f"alt+{key}: [{tag}]" for key, tag in FORMAT_TAGS.items()))


if __name__ == "__main__":
    main()

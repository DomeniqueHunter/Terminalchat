from textual.binding import Binding
from textual.widgets import TextArea


CURSOR = "{}"
FORMAT_TAGS = {"b": "b", "i": "i", "u": "u", "s": "s", "p": "spoiler", "q": "quote"}


class BBCodeArea(TextArea):

    BINDINGS = [Binding(f"alt+{key}", f"wrap('{tag}')", show=False) for key, tag in FORMAT_TAGS.items()]

    def action_wrap(self, tag:str) -> None:
        self.insert_template(f"[{tag}]{CURSOR}[/{tag}]")

    def insert_template(self, template:str) -> None:
        start, end = sorted(self.selection)
        selected = self.selected_text
        before, _, after = template.partition(CURSOR)
        result = self.replace(f"{before}{selected}{after}", start, end)
        if selected or not after:
            self.move_cursor(result.end_location)
        else:
            row, column = result.end_location
            self.move_cursor((row, column - len(after)))


def main() -> None:
    print(", ".join(f"alt+{key}: [{tag}]" for key, tag in FORMAT_TAGS.items()))


if __name__ == "__main__":
    main()

from typing import List, Set

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Header, Footer, Input, Static, ListView, ListItem


def load_chat(chat_id: int) -> List[str]:
    if chat_id == 0:
        return ["Hello!", "Hi!", "Chat 1"]
    if chat_id == 1:
        return ["Another chat", "More messages"]
    return ["Empty chat"]


class ChatApp(App):

    BINDINGS = [
        ("ctrl+x", "close_chat", "Close chat"),
    ]

    CSS = """
    #main {
        layout: horizontal;
        height: 1fr;
    }

    #chat_list {
        width: 25%;
        border: solid green;
    }

    #chat_container {
        width: 75%;
        layout: vertical;
    }

    #chat_view {
        height: 1fr;
        overflow-y: auto;
        border: solid blue;
    }

    ListItem {
        height: 1;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self.all_chats: List[str] = ["Chat 1", "Chat 2"]
        self.closed: Set[int] = set()
        self.active_chat: int = 0

    def compose(self) -> ComposeResult:
        yield Header()

        with Horizontal(id="main"):
            self.list_view = ListView(id="chat_list")
            yield self.list_view

            with Vertical(id="chat_container"):
                with VerticalScroll(id="chat_view"):
                    pass

                yield Input(placeholder="Type message...")

        yield Footer()

    def on_mount(self) -> None:
        self.rebuild_list()

        visible = self.visible_chats()
        if visible:
            self.open_chat(visible[0])

    def visible_chats(self) -> List[int]:
        return [i for i in range(len(self.all_chats)) if i not in self.closed]

    def rebuild_list(self) -> None:
        self.list_view.clear()

        for chat_id in self.visible_chats():
            self.list_view.append(
                ListItem(Static(self.all_chats[chat_id]))
            )

    def open_chat(self, chat_id: int) -> None:
        self.active_chat = chat_id

        view = self.query_one("#chat_view", VerticalScroll)
        view.remove_children()

        for msg in load_chat(chat_id):
            view.mount(Static(msg))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        visible = self.visible_chats()

        if 0 <= event.index < len(visible):
            self.open_chat(visible[event.index])

    # 🔥 KEYBOARD ACTION
    def action_close_chat(self) -> None:
        visible = self.visible_chats()

        if not visible:
            return

        chat_id = self.active_chat

        self.closed.add(chat_id)

        self.rebuild_list()

        visible = self.visible_chats()

        if visible:
            self.open_chat(visible[0])
        else:
            view = self.query_one("#chat_view", VerticalScroll)
            view.remove_children()
            view.mount(Static("No chats"))


def main() -> None:
    app = ChatApp()
    app.run()


if __name__ == "__main__":
    main()

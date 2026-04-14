
BINDINGS = [
        ("ctrl+x", "close_chat", "Close chat"),
        ("ctrl+c", "open_channels_list", "Channels List")
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
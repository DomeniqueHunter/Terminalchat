
APP_BINDINGS = [
        ("ctrl+x", "close_chat", "Close chat"),
        ("ctrl+c", "open_channels_list", "Channels List")
    ]


APP_CSS = """
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

CHANNELS_CSS = """
    ChannelsList {
        align: center middle;
    }

    #container {
        width: 80%;
        height: 70%;
        background: $panel;
        border: solid white;
        layout: horizontal;
    }

    .panel {
        width: 1fr;
        border: solid green;
        padding: 1;
    }

    Input {
        height: 1;
        padding: 0;
    }
    """
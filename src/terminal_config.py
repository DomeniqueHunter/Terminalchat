
APP_BINDINGS = [
        ("ctrl+o", "open_channels_list", "Channels"),
        ("ctrl+l", "close_chat", "Close chat"),
        ("ctrl+f", "toggle_sidebar", "Users"),
        ("ctrl+t", "minimize", "Minimize"),
        ("ctrl+r", "toggle_ad_mode", "Chat/Ads"),
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
        width: 1fr;
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
        padding: 0;
    }
    
    """

"""
Input {
        height: 1;
        padding: 0;
        color: white;
        background: $surface;
    }
"""
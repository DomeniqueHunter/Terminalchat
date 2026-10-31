import unicodedata

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, OptionList
from textual.widgets.option_list import Option


EMOJI_GROUPS = [
    ("smileys", "😀😃😄😁😆😅😂🤣😊😇🙂🙃😉😌😍🥰😘😗😙😚😋😛😝😜🤪🤨🧐🤓😎🥳😏😒😞😔😟😕🙁😣😖😫😩🥺😢😭😤😠😡🤬🤯😳🥵🥶😱😨😰😥😓🤗🤔🤭🤫🤥😶😐😑😬🙄😯😦😧😮😲🥱😴🤤😪😵🤐🥴🤢🤮🤧😷🤒🤕🤑🤠😈👿👻💀👽🤖💩🫠🫣🫡"),
    ("gestures", "👋🤚✋🖖👌🤌🤏✌🤞🤟🤘🤙👈👉👆👇👍👎✊👊🤛🤜👏🙌👐🤲🤝🙏💪💅"),
    ("hearts", "❤🧡💛💚💙💜🖤🤍🤎💔💕💞💓💗💖💘💝💋💯💢💥💫💦💨💤"),
    ("animals", "🐶🐱🐭🐹🐰🦊🐻🐼🐨🐯🦁🐮🐷🐸🐵🙈🙉🙊🐔🐧🐦🦆🦅🦉🦇🐺🐗🐴🦄🐝🦋🐌🐞🐢🐍🦖🐙🦑🦀🐠🐬🐳🦈🐊🐅🦓🦒🐘🐎🐑🐐🦌🐕🐈🐓🦚🦜🐉🐾"),
    ("nature", "🌵🎄🌲🌳🌴🌱🌿🍀🍁🍂🍄🌷🌹🥀🌺🌸🌼🌻🌞🌝🌛🌚🌙⭐🌟✨⚡🔥🌈☀⛅☁🌧⛈❄☃🌊💧🌍"),
    ("food", "🍏🍎🍐🍊🍋🍌🍉🍇🍓🍒🍑🥭🍍🥥🥝🍅🍆🥑🥦🌽🥕🥔🥐🍞🧀🥚🍳🥓🍔🍟🍕🌭🥪🌮🌯🍜🍝🍣🍤🍦🍩🍪🎂🍰🧁🍫🍬🍭🍯☕🍵🍺🍻🥂🍷🥃🍸🍹🧉🍾"),
    ("activities", "⚽🏀🏈⚾🎾🏐🎱🏓🏸🥊🎯🎳🎮🎲🧩🎭🎨🎬🎤🎧🎼🎹🥁🎷🎺🎸🎻🏆🥇🎉🎊🎈🎁🎀"),
    ("objects", "⌚📱💻⌨🖥📷🎥📺📻⏰⌛💡🔦🕯💸💵💰💎🔧🔨⚙🔫💣🔪🗡⚔🛡🔮💊💉🧸🔑🗝🚪🛏🛁🧻📦📫📝📖📚🔒🔓🔔🎵🎶💬💭🗯"),
    ("travel", "🚗🚕🚌🏎🚓🚑🚒🚲🛵🏍🚂✈🚀🛸🚁⛵🚢🏠🏰🗼🗽⛪🌋🗻🏕🏖🏝"),
    ("symbols", "✅❌❓❗⚠🚫⛔💤♻✔➕➖➗✖💲©®™🔞🆗🆒🆕🆘🔴🟠🟡🟢🔵🟣⚫⚪🔺🔻💠🏳🏴🚩"),
]

EXTRA_KEYWORDS = {
    "😂": "lol laugh", "🤣": "lol rofl", "😊": "happy blush", "😍": "love", "🥰": "love",
    "😘": "kiss", "😉": "wink", "😢": "sad", "😭": "sad sob", "😡": "angry", "😠": "angry",
    "🤔": "think hmm", "🙄": "eyeroll", "😳": "blush embarrassed", "😈": "evil devil",
    "👍": "like yes ok", "👎": "dislike no", "👌": "ok", "🙏": "please thanks pray",
    "❤": "heart love red", "💔": "broken heart", "🔥": "hot lit", "✨": "sparkle magic",
    "💯": "hundred perfect", "🎉": "party", "🍺": "beer", "☕": "coffee", "🍷": "wine",
    "💀": "dead skull", "👋": "hi bye wave", "🤗": "hug", "😴": "sleep tired", "🥺": "please puppy",
}


def emoji_name(emoji:str) -> str:
    return unicodedata.name(emoji[0], "").lower()


def emoji_entries() -> list[tuple[str, str, str]]:
    entries = []
    for group, emojis in EMOJI_GROUPS:
        for emoji in emojis:
            name = emoji_name(emoji)
            if name:
                entries.append((emoji, name, f"{name} {group} {EXTRA_KEYWORDS.get(emoji, '')}"))
    return entries


class EmojiScreen(ModalScreen[str | None]):

    DEFAULT_CSS = """
    EmojiScreen {
        align: center middle;
    }
    EmojiScreen > Vertical {
        width: 60;
        max-width: 90%;
        height: auto;
        max-height: 90%;
        background: $panel;
        border: round $accent;
        border-title-align: center;
        border-subtitle-align: center;
        padding: 0 1;
    }
    EmojiScreen OptionList {
        height: 16;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", show=False),
        Binding("down", "move(1)", show=False),
        Binding("up", "move(-1)", show=False),
        Binding("pagedown", "move(10)", show=False),
        Binding("pageup", "move(-10)", show=False),
    ]

    def __init__(self, query:str="") -> None:
        super().__init__()
        self.query_text = query
        self.entries = emoji_entries()
        self.shown: list[str] = []

    def compose(self) -> ComposeResult:
        with Vertical() as box:
            box.border_title = "Emoji"
            box.border_subtitle = "type to search · enter: insert · esc: close"
            yield Input(value=self.query_text, placeholder="search, e.g. heart, cat, laugh", id="emoji_search")
            yield OptionList(id="emoji_list")

    def on_mount(self) -> None:
        self.update_list(self.query_text)
        self.query_one("#emoji_search", Input).focus()

    def on_input_changed(self, event:Input.Changed) -> None:
        self.update_list(event.value)

    def update_list(self, query:str) -> None:
        words = query.lower().split()
        matches = [(emoji, name) for emoji, name, keywords in self.entries if all(word in keywords for word in words)]
        self.shown = [emoji for emoji, _ in matches]
        option_list = self.query_one("#emoji_list", OptionList)
        option_list.clear_options()
        option_list.add_options([Option(Text.assemble(f"{emoji}  ", (name, "dim"))) for emoji, name in matches])
        if matches:
            option_list.highlighted = 0

    def action_move(self, step:int) -> None:
        option_list = self.query_one("#emoji_list", OptionList)
        if not self.shown:
            return
        current = option_list.highlighted or 0
        option_list.highlighted = max(0, min(len(self.shown) - 1, current + step))

    def on_input_submitted(self, event:Input.Submitted) -> None:
        index = self.query_one("#emoji_list", OptionList).highlighted
        if index is not None and index < len(self.shown):
            self.dismiss(self.shown[index])

    def on_option_list_option_selected(self, event:OptionList.OptionSelected) -> None:
        self.dismiss(self.shown[event.option_index])

    def action_cancel(self) -> None:
        self.dismiss(None)


def main() -> None:
    entries = emoji_entries()
    print(len(entries), "emojis")
    missing = [emoji for _, emojis in EMOJI_GROUPS for emoji in emojis if not emoji_name(emoji)]
    print("without name:", "".join(missing))


if __name__ == "__main__":
    main()

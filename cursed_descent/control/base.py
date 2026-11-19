from dataclasses import dataclass


ALWAYS_OPEN = frozenset({
    "help", "status", "profile", "sheet", "inv", "needs", "spells", "top",
    "graveyard", "examine", "town", "talk", "chat", "meet", "rumors",
    "slave", "safeword"})


@dataclass(frozen=True)
class ControlKind:
    key: str
    title: str
    home_town: str = ""
    home_building: str = ""
    hours: float = 0.0
    safeword: bool = True
    can_end: bool = True
    ransom: int = 0
    open_commands: frozenset[str] = frozenset()
    start_text: str = "{holder} takes control of you."
    watch_text: str = ("You are not in control. All you can do is watch "
                       "what {holder} does with you.")
    release_text: str = "{holder} lets you go. You are your own again."
    expire_text: str = "{holder} loses interest. You are free again."
    end_ask: str = ("This ends your character for good: {holder} keeps "
                    "{name} as a slave, and you respawn like after a death. "
                    "Confirm with the button.")
    end_text: str = ("{name} belongs to {holder} now. You rise again like "
                     "after a death.")
    public_start: str = "{name} is taken by {holder}."
    public_end: str = "{name} is gone for good."
    examine_text: str = ("{name} is held by {holder} and cannot act: "
                         "watching, not choosing.")
    locked_text: str = ("You are on {holder}'s leash and cannot do that. "
                        "Watch, or use the buttons in the panel.")

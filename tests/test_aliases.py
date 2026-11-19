from cursed_descent.commands import ALIASES, parse_chat


def test_short_forms_resolve() -> None:
    assert parse_chat("!h").name == "hit"
    assert parse_chat("!H goblin").args == ("goblin",)
    assert parse_chat("!hit").name == "hit"
    assert parse_chat("!w Lyra: hi").name == "w"
    assert set(ALIASES) == {"h", "c", "f", "d", "g", "p", "e", "i", "s"}

from cursed_descent.commands import Command, command, parse_chat
from cursed_descent.controller import GameController


def test_parse_chat_splits_name_and_arguments() -> None:
    assert parse_chat("  !Buy 3 ") == Command("buy", ("3",))
    assert parse_chat("!cast fireball Wobbla") == Command(
        "cast", ("fireball", "Wobbla"))


def test_parse_chat_ignores_plain_text() -> None:
    assert parse_chat("hello") is None
    assert parse_chat("!") is None


def test_command_builder_stringifies_and_skips_empty() -> None:
    assert command("add", "str", 2) == Command("add", ("str", "2"))
    assert command("hit", "") == Command("hit")


def test_text_roundtrip() -> None:
    action = command("give", 3, "Beverley")
    assert parse_chat(action.text) == action


def test_with_args_appends() -> None:
    assert Command("hit").with_args("A1") == Command("hit", ("A1",))


def test_execute_runs_a_command_object(controller:GameController) -> None:
    messages = controller.execute("kerl", command("needs"))
    assert "Needs:" in messages[0].text


def test_handle_and_execute_agree(controller:GameController) -> None:
    assert (controller.handle("kerl", "!inv")
            == controller.execute("kerl", command("inv")))

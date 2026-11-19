from cursed_descent.config import SHOW_ACTION_HINTS
from cursed_descent.controller import GameController, strip_hints
from cursed_descent.models import Message


def test_action_lines_are_hidden_by_default() -> None:
    assert SHOW_ACTION_HINTS is False


def test_strip_hints_removes_only_the_action_lines() -> None:
    message = Message("Something happens.\nActions: [hit] | [guard] (40 s)")
    assert strip_hints([message])[0].text == "Something happens."


def test_messages_that_are_only_an_action_line_vanish() -> None:
    assert strip_hints([Message("Actions: [open] | [skip]")]) == []


def test_help_and_other_texts_stay_untouched() -> None:
    message = Message("Actions:\n  hit – attack")
    assert strip_hints([message]) == [message]


def test_the_controller_output_has_no_action_lines(
        controller:GameController) -> None:
    controller.handle("kerl", "!lobby", now=0.0)
    messages = controller.handle("kerl", "!start", now=1.0)
    controller.session.events.offer_location("sweatery", 2.0)
    messages += controller.handle("kerl", "!enter", now=3.0)
    assert messages
    assert not any(line.startswith("Actions:") for message in messages
                   for line in message.text.split("\n"))


def test_the_options_tail_of_an_invalid_command_is_cut() -> None:
    message = Message("That doesn't work here. Options: [sit] | [depart]")
    assert strip_hints([message])[0].text == "That doesn't work here."


def test_a_hint_in_the_middle_of_a_line_is_cut() -> None:
    message = Message("The fire burns. Actions: [sit] | [depart] (40 s)")
    assert strip_hints([message])[0].text == "The fire burns."

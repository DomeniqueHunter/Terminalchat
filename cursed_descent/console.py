#!/usr/bin/env python3
import argparse
import random
from pathlib import Path

from cursed_descent import GameController, Message


INTRO = """The Cursed Descent – console test
New player:  'Lyra: !create'  – then just answer the questions.
Without 'Name:' in front, input counts for the last named player.
'!force' resolves a round immediately (simulates the timeout), 'quit' exits."""


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Cursed Descent console")
    parser.add_argument("--data", type=Path, default=Path("game_data"))
    parser.add_argument("--seed", type=int, default=None)
    return parser.parse_args()


def print_messages(messages:list[Message]) -> None:
    for message in messages:
        prefix = (f"[DM → {message.recipient}]" if message.is_private
                  else "[#dungeon]")
        print(f"{prefix} {message.text}\n")


def split_line(line:str, last_sender:str) -> tuple[str, str]:
    sender, separator, text = line.partition(":")
    if not separator or line.startswith("!"):
        return last_sender, line
    return sender.strip(), text.strip()


def main() -> None:
    arguments = parse_arguments()
    if arguments.seed is not None:
        random.seed(arguments.seed)
    controller = GameController(arguments.data)
    print(INTRO)
    last_sender = ""
    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if line.lower() in ("quit", "exit"):
            break
        if not line:
            continue
        sender, text = split_line(line, last_sender)
        if not sender:
            print("Please give a name first: 'Name: !command'")
            continue
        last_sender = sender
        print_messages(controller.handle(sender, text))
        print_messages(controller.tick())


if __name__ == "__main__":
    main()

from typing import Callable

from .config import MAX_PARTY_SIZE
from .models import Message, Player


READY_SECONDS = 60.0


class ReadyCheck:
    def __init__(self, session, held_text:Callable[[Player], str]) -> None:
        self.session = session
        self.held_text = held_text
        self.pending: set[str] = set()
        self.chief = ""
        self.deadline = 0.0

    def active(self) -> bool:
        if self.pending and self.session.state != "lobby":
            self.cancel()
        return bool(self.pending)

    def waiting_for(self, name:str) -> bool:
        return self.active() and name in self.pending

    def cancel(self) -> None:
        self.pending = set()
        self.chief = ""

    def busy_lines(self) -> list[str]:
        lines = []
        for member in self.session.humans():
            reason = self.held_text(member)
            if reason:
                lines.append(f"{member.name}: {reason}")
        return lines

    def start(self, player:Player, now:float) -> list[Message]:
        session = self.session
        if session.state != "lobby" or session.member(player.name) is None:
            return session.start(player.name, now)
        if session.party[0].name != player.name:
            return [Message("Only the one who opened the lobby can call "
                            "the descent.", player.name)]
        busy = self.busy_lines()
        if busy:
            return [Message("The party cannot leave yet:\n"
                            + "\n".join(busy))]
        others = [member.name for member in session.humans()
                  if member.name != player.name]
        if not others:
            return session.start(player.name, now)
        self.pending = set(others)
        self.chief = player.name
        self.deadline = now + READY_SECONDS
        return [Message(f"🕯 {player.name} wants to descend. "
                        f"{', '.join(others)}: [ready] or [decline] within "
                        f"{int(READY_SECONDS)} seconds.")]

    def ready(self, player:Player, now:float) -> list[Message]:
        if not self.waiting_for(player.name):
            return [Message("Nobody is waiting for your answer.",
                            player.name)]
        reason = self.held_text(player)
        if reason:
            return [Message(reason, player.name)]
        self.pending.discard(player.name)
        if self.pending:
            return [Message(f"{player.name} is ready. Waiting for "
                            f"{', '.join(sorted(self.pending))}.")]
        chief = self.chief
        busy = self.busy_lines()
        self.cancel()
        if busy:
            return [Message("The party cannot leave yet:\n"
                            + "\n".join(busy))]
        return self.session.start(chief, now)

    def decline(self, player:Player) -> list[Message]:
        if not self.waiting_for(player.name):
            return [Message("Nobody is waiting for your answer.",
                            player.name)]
        self.cancel()
        return [Message(f"{player.name} is not ready. The descent is "
                        f"called off.")]

    def tick(self, now:float) -> list[Message]:
        if not self.active() or now < self.deadline:
            return []
        missing = ", ".join(sorted(self.pending))
        self.cancel()
        return [Message(f"⏳ No answer from {missing}. The descent is "
                        f"called off.")]

    def void(self) -> list[Message]:
        if not self.active():
            return []
        self.cancel()
        return [Message("The party changed. The start check is void.")]

    def kick(self, player:Player, text:str) -> list[Message]:
        session = self.session
        if session.state != "lobby" or session.member(player.name) is None:
            return [Message("There is no lobby to kick from.", player.name)]
        if session.party[0].name != player.name:
            return [Message("Only the one who opened the lobby can kick.",
                            player.name)]
        target = next((member for member in session.party
                       if member.name.casefold() == text.casefold()
                       or member.name.casefold().startswith(
                           f"{text.casefold()} ")), None)
        if not text or target is None or target.name == player.name:
            return [Message("Kick whom? [kick <name>]", player.name)]
        self.cancel()
        session.party.remove(target)
        return [Message(f"{target.name} is sent out of the lobby "
                        f"({len(session.party)}/{MAX_PARTY_SIZE}).")]

from typing import Any

from .commands import Command
from .config import CAFE_LOCK, SLEEP_VOTE_SECONDS
from .home_scene import knocked_out
from .house_visit import state_of
from .models import Message, Player


DUNGEON_SLEEP = {"hut": "sleep", "mage_tower": "sleep", "bivouac": "rest"}
YES, NO = ("yes", "y", "accept"), ("no", "n", "decline")


class GroupSleep:
    def __init__(self, controller:Any) -> None:
        self.controller = controller
        self.pending: dict[str, Any] | None = None
        self.passed: set[str] = set()

    def kind_of(self, player:Player, command:str, args:list[str]) -> str:
        session = self.controller.session
        if (command == "home" and args and args[0].casefold() == "sleep"
                and not session.in_run(player.name)):
            return "home"
        phase = session.events.event.get("phase", "")
        if (session.state == "event" and session.in_run(player.name)
                and DUNGEON_SLEEP.get(phase) == command and not args):
            return "dungeon"
        return ""

    def humans(self, player:Player) -> list[Player]:
        session = self.controller.session
        return [member for member in session.party
                if member.name != player.name and not member.npc
                and not session.is_auto(member)
                and not member.records.get(CAFE_LOCK)]

    def busy(self, member:Player) -> str:
        state = state_of(member)
        if self.controller.town.on_shift(member):
            return "is working a shift"
        if member.profile.get("home_sex"):
            return "is in a private scene"
        if state is not None and state.get("held_by"):
            return "is pinned"
        if knocked_out(member):
            return "is out cold"
        return ""

    def gate(self, player:Player, command:str, args:list[str],
             now:float) -> list[Message] | None:
        if command == "sleep" and args and (
                args[0].casefold() in YES + NO):
            return self.answer(player, args[0].casefold() in YES, now)
        kind = self.kind_of(player, command, args)
        if not kind:
            return None
        if player.name in self.passed:
            self.passed.discard(player.name)
            return None
        others = self.humans(player)
        if not others:
            return None
        blockers = [f"{member.name} {self.busy(member)}"
                    for member in others if self.busy(member)]
        if blockers:
            return [Message("Nobody sleeps yet: " + "; ".join(blockers)
                            + ".", player.name)]
        self.pending = {"by": player.name, "command": command,
                        "args": list(args), "kind": kind, "until":
                        now + SLEEP_VOTE_SECONDS,
                        "waiting": {member.name for member in others}}
        messages = [Message("You ask everyone to go to sleep. Waiting for "
                            + ", ".join(sorted(self.pending["waiting"]))
                            + ".", player.name)]
        for member in others:
            member.profile["sleep_offer"] = {"from": player.name}
            self.controller.repository.save(member)
            messages.append(Message(
                f"🛏 {player.name} wants everyone to sleep. Confirm with "
                f"[sleep yes] or [sleep no].", member.name))
        return messages

    def clear(self) -> None:
        if self.pending is None:
            return
        for name in self.pending["waiting"]:
            member = self.controller.repository.load(name)
            if member is not None and member.profile.pop("sleep_offer",
                                                         None):
                self.controller.repository.save(member)

    def answer(self, player:Player, yes:bool, now:float) -> list[Message]:
        pending = self.pending
        if (pending is None or player.name not in pending["waiting"]
                or now > pending["until"]):
            if pending is not None and now > pending["until"]:
                self.clear()
                self.pending = None
            player.profile.pop("sleep_offer", None)
            self.controller.repository.save(player)
            return [Message("Nobody is asking you to sleep.", player.name)]
        player.profile.pop("sleep_offer", None)
        self.controller.repository.save(player)
        if not yes:
            by = pending["by"]
            self.clear()
            self.pending = None
            return [Message(f"{player.name} does not want to sleep yet.",
                            by),
                    Message("You decline.", player.name)]
        pending["waiting"].discard(player.name)
        if pending["waiting"]:
            return [Message("You agree. Waiting for the others.",
                            player.name)]
        self.pending = None
        return self.run(pending, now)

    def run(self, pending:dict[str, Any], now:float) -> list[Message]:
        names = [pending["by"]]
        if pending["kind"] == "home":
            names += [member.name for member in self.controller.session.party
                      if member.name != pending["by"] and not member.npc
                      and not self.controller.session.is_auto(member)
                      and not member.records.get(CAFE_LOCK)]
        messages = [Message("🛏 Everyone agrees: time to sleep.")]
        for name in names:
            self.passed.add(name)
            messages += self.controller.execute_raw(
                name, Command(pending["command"], tuple(pending["args"])),
                now)
            self.passed.discard(name)
        return messages

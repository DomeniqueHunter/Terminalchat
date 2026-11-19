import random
import re
from typing import Any

from ...config import (
    NULL_EXP_BASE, NULL_EXP_PER_STAGE, NULL_RIDDLE_COUNT,
    ROUND_TIMEOUT_SECONDS,
)
from ...captivity import take
from ...dungeon import give_item, grant_exp, roll_item, stage_gold
from ...models import Message, Player
from ..common import options_text, their
from .content import EVENT_TEXTS, RIDDLES


NULL_OPTIONS = ("answer", "depart")
DRONE_QUOTES = ("...", "(The drone does not react. It squats, hands on "
                       "its knees.)", "(A faint hum. Nothing more.)")


def correct_answer(text:str, answers:tuple[str, ...]) -> bool:
    spoken = re.sub(r"[^a-z ]", "", text.casefold())
    return any(answer in spoken for answer in answers)


def make_drone(player:Player, repository:Any, day:int=0) -> int:
    repository.bury(player, "drone: taken by the Null Master")
    return take(player, repository, "drone", {
        "kind": "drone", "role": "Drone of the Null Master",
        "look": "A hooded figure squats motionless, hands on its knees, "
                "eyes empty, a faint hum in the air around it.",
        "quotes": list(DRONE_QUOTES)}, day)


class NullMasterMixin:
    session: Any
    event: dict[str, Any]

    def offer_null(self) -> list[str]:
        texts = EVENT_TEXTS["null_master"]
        riddles = random.sample(RIDDLES, NULL_RIDDLE_COUNT)
        self.event["phase"] = "null"
        self.event["data"].update(
            {"riddles": riddles, "index": 0, "correct": 0})
        return ["", texts["intro"], self.null_question(),
                self.strip_timer(texts["options"]).format(
                    seconds=int(ROUND_TIMEOUT_SECONDS))]

    def null_question(self) -> str:
        data = self.event["data"]
        question, _ = data["riddles"][data["index"]]
        return EVENT_TEXTS["null_master"]["ask"].format(
            nr=data["index"] + 1, total=len(data["riddles"]),
            question=question)

    def null_action(self, player:Player, command:str, args:list[str],
                    now:float) -> list[Message]:
        texts = EVENT_TEXTS["null_master"]
        if command == "depart":
            self.save_party()
            return self.finish([texts["depart"]], now)
        data = self.event["data"]
        if not args:
            return [Message("Answer with [answer <word>].", player.name)]
        _, answers = data["riddles"][data["index"]]
        stage = self.session.stage
        lines: list[str] = []
        if correct_answer(" ".join(args), answers):
            exp = NULL_EXP_BASE + NULL_EXP_PER_STAGE * stage
            gold = stage_gold(stage)
            data["correct"] += 1
            lines.append(texts["right"].format(name=player.name, exp=exp,
                                               gold=gold))
            for member in self.session.living():
                lines += grant_exp(member, exp)
                member.gold += gold
        else:
            lines.append(texts["wrong"].format(name=player.name))
            lines += self.null_drone(player)
        data["index"] += 1
        return self.null_next(lines, now)

    def null_drone(self, player:Player) -> list[str]:
        session = self.session
        text = EVENT_TEXTS["null_master"]["drone"].format(
            name=player.name, their=their(player))
        lines = session.kill_outside(player, "nulled", text,
                                     "the Null Master", "void")
        make_drone(player, session.repository, session.today())
        return lines

    def null_next(self, lines:list[str], now:float) -> list[Message]:
        session = self.session
        texts = EVENT_TEXTS["null_master"]
        data = self.event["data"]
        if not session.living():
            self.reset()
            return [Message("\n".join(lines + session.end_run()))]
        if data["index"] < len(data["riddles"]):
            session.deadline = self.idle_deadline(now)
            lines += [self.null_question(), self.strip_timer(
                texts["options"]).format(
                    seconds=int(ROUND_TIMEOUT_SECONDS))]
            return [Message("\n".join(lines))]
        if data["correct"] == len(data["riddles"]):
            lines += [texts["done"], texts["reward"]]
            finder = random.choice(session.living())
            lines.append(give_item(finder, roll_item(session.stage)))
        else:
            lines.append(texts["ended"])
        self.save_party()
        return self.finish(lines, now)

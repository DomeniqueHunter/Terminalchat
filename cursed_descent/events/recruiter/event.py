from typing import Any

from ...content import EVENT_TEXTS
from ...models import Message, Player
from ...captivity import take
from ...towns.last_light_humans.maidschool.school import (
    UNIFORM, buyback_price,
)
from ...locations.common import pronouns


class RecruiterMixin:
    repository: Any
    recruit_offers: set[str]

    def member(self, name:str) -> Player | None:
        raise NotImplementedError

    def recruit_notes(self, fallen:list[Player]) -> list[str]:
        notes: list[str] = []
        for player in fallen:
            if player.last_fate != "recruited":
                continue
            self.recruit_offers.add(player.name)
            notes.append(EVENT_TEXTS["recruiter"]["offer"].format(
                name=player.name, price=buyback_price(player)))
        return notes

    def recruit_pending(self, name:str) -> list[Message]:
        if name not in self.recruit_offers:
            return []
        return [Message(EVENT_TEXTS["recruiter"]["pending"].format(
            name=name), name)]

    def answer_recruit(self, name:str, command:str) -> list[Message]:
        texts = EVENT_TEXTS["recruiter"]
        player = self.member(name) or self.repository.load(name)
        self.recruit_offers.discard(name)
        if player is None:
            return []
        if command == "decline":
            return [Message(texts["decline"].format(name=player.name))]
        _, them, _ = pronouns(player.gender)
        price = buyback_price(player)
        self.repository.bury(player, "maid: recruited by the school")
        take(player, self.repository, "maid", {"graduate": True},
             self.today())
        player.equipment["chest"] = UNIFORM
        self.repository.save(player)
        return [Message(texts["accept"].format(
            name=player.name, them=them, price=price))]

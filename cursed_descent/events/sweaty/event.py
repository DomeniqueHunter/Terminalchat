import random
from typing import Any

from ...body import muscle_tier, shape_of
from ...config import (
    SWEATY_TASTES, SWEATY_TASTE_BONUS, SWEATY_TIP_PER_TIER,
    SWEATY_WANDERER_CHANCE, SWEATY_WANDERER_TIER, WANDERER_THEFT_CHANCE,
    WANDERER_THEFT_SHARE,
)
from ...content import EVENT_TEXTS
from ...models import Message, Player
from ...needs_runtime import relieve_arousal
from ...sweat import sweat_tier
from .content import SWEATY_TEASES, SWEATY_TEXTS


class SweatyMixin:
    session: Any
    event: dict[str, Any]

    def offer_sweaty(self, wanderer:str) -> list[str]:
        sweaty = max(self.session.living(), key=sweat_tier, default=None)
        if (sweaty is None or sweat_tier(sweaty) < SWEATY_WANDERER_TIER
                or random.random() >= SWEATY_WANDERER_CHANCE):
            return []
        self.event["data"]["sweaty"] = sweaty.name
        self.event["data"]["taste"] = random.choice(SWEATY_TASTES)
        return [SWEATY_TEXTS["intro"].format(wanderer=wanderer,
                                             name=sweaty.name)]

    def indulge_action(self, player:Player) -> list[Message]:
        data = self.event["data"]
        values = {"name": player.name, "wanderer": data["wanderer"],
                  "sweaty": data["sweaty"]}
        if player.name != data["sweaty"]:
            return [Message(SWEATY_TEXTS["other"].format(**values),
                            player.name)]
        self.event["used"].add("indulge")
        tier = sweat_tier(player)
        lines = [random.choice(SWEATY_TEASES[tier]).format(**values)]
        if muscle_tier(player.stats, player.body) == "leather":
            lines.append(SWEATY_TEXTS["muscle"].format(**values))
        if shape_of(player.gender, player.body) == "Equine":
            lines.append(SWEATY_TEXTS["stallion"].format(**values))
        lines += [SWEATY_TEXTS["blush"].format(**values),
                  SWEATY_TEXTS["fade"]]
        tip = round(data["gold"] * tier * SWEATY_TIP_PER_TIER)
        if player.gender in data["taste"]:
            tip = round(tip * SWEATY_TASTE_BONUS)
            lines.append(SWEATY_TEXTS["taste"].format(**values))
        player.gold += tip
        player.sweat = 0
        relieve_arousal(player)
        lines.append(SWEATY_TEXTS["after"].format(tip=tip, **values))
        if random.random() < WANDERER_THEFT_CHANCE and player.gold:
            stolen = max(1, round(player.gold * WANDERER_THEFT_SHARE))
            player.gold -= stolen
            lines.append(EVENT_TEXTS["wanderer"]["theft"].format(
                stolen=stolen, **values))
        self.save_party()
        return self.continue_event(lines)

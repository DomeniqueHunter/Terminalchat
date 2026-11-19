from ....formulas import apply_buff
from ....models import Message, Player
from ..death import fall
from .content import (
    BOX, CURED, FULL_PAY, SHORT_PAY, SHORT_RISK, SHORT_TEXT, WHEEL,
    WHEEL_TEXT,
)


def reward(services, player:Player, pay:int, buff:str) -> None:
    player.gold += pay
    if buff not in player.buffs:
        apply_buff(player, buff)
    services.repository.save(player)


def short(services, player:Player, offer) -> list[Message]:
    if services.rng.random() < SHORT_RISK:
        return fall(services, player, "hall_smoked")
    reward(services, player, SHORT_PAY, "smoke_short")
    return [Message(SHORT_TEXT.format(pay=SHORT_PAY), player.name)]


def box(services, player:Player, offer) -> list[Message]:
    rng = services.rng
    pick = rng.choices([name for name, _ in WHEEL],
                       [weight for _, weight in WHEEL])[0]
    risk, scene = BOX[pick]
    intro = WHEEL_TEXT.format(pick=pick, scene=scene)
    if rng.random() < risk:
        return [Message(intro, player.name),
                *fall(services, player, "hall_smoked")]
    reward(services, player, FULL_PAY, "smoke_cured")
    return [Message("\n".join((intro, CURED.format(pay=FULL_PAY))),
                    player.name)]

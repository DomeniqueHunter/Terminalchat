from ....formulas import apply_buff, max_hp
from ....models import Message, Player
from ..death import fall
from .content import (
    FEAST_DAY, FEAST_FLAG, FEAST_PRICE, JOIN, MERCY, MERCY_PAY, NO_FEAST,
    SPIT, SPIT_PAY, SPIT_RISK, SURVIVED, WHEEL, WHEEL_INTRO,
)


def expire(services, player:Player) -> bool:
    if (player.profile.get(FEAST_FLAG)
            and player.profile.get(FEAST_DAY) != services.world.day):
        player.profile.pop(FEAST_FLAG, None)
        player.profile.pop(FEAST_DAY, None)
        services.repository.save(player)
        return True
    return False


def join(services, player:Player, offer) -> list[Message]:
    expire(services, player)
    if player.gold < FEAST_PRICE:
        return [Message(f"That costs {FEAST_PRICE} gold.", player.name)]
    player.gold -= FEAST_PRICE
    player.profile[FEAST_FLAG] = True
    player.profile[FEAST_DAY] = services.world.day
    player.hp = max_hp(player)
    if "feast_fed" not in player.buffs:
        apply_buff(player, "feast_fed")
    services.repository.save(player)
    return [Message("\n".join((JOIN, f"💰 Gold: {player.gold}")),
                    player.name)]


def wheel(services, player:Player, offer) -> list[Message]:
    if expire(services, player) or not player.profile.get(FEAST_FLAG):
        return [Message(NO_FEAST, player.name)]
    rng = services.rng
    pick = rng.choices([name for name, _ in WHEEL],
                       [weight for _, weight in WHEEL])[0]
    intro = WHEEL_INTRO.format(pick=pick)
    if pick == "mercy":
        player.gold += MERCY_PAY
        services.repository.save(player)
        return [Message("\n".join((intro, MERCY.format(pay=MERCY_PAY))),
                        player.name)]
    if rng.random() < SPIT_RISK:
        return [Message("\n".join((intro, SPIT)), player.name),
                *fall(services, player, "roasted")]
    player.gold += SPIT_PAY
    if "feast_roast" not in player.buffs:
        apply_buff(player, "feast_roast")
    services.repository.save(player)
    return [Message("\n".join((intro, SPIT, SURVIVED.format(pay=SPIT_PAY))),
                    player.name)]


def lock(services, player:Player, command:str) -> list[Message]:
    expire(services, player)
    return []

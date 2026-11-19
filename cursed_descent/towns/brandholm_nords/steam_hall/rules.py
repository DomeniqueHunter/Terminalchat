from ....formulas import apply_buff, max_hp
from ....models import Message, Player
from ..death import fall
from .content import CHAMBERS, SIT, SIT_COST, SIT_PAY, SURVIVED


def mask(services, player:Player, offer) -> list[Message]:
    label, price, risk, heal, buff, text = CHAMBERS[offer.item]
    if player.gold < price:
        return [Message(f"That costs {price} gold. {player.name} only has "
                        f"{player.gold}.", player.name)]
    player.gold -= price
    if services.rng.random() < risk:
        return fall(services, player, "sweated")
    gain = round(max_hp(player) * heal)
    player.hp = min(max_hp(player), player.hp + gain)
    if buff not in player.buffs:
        apply_buff(player, buff)
    services.repository.save(player)
    return [Message("\n".join((text, SURVIVED, f"❤ +{gain} HP.",
                               f"💰 Gold: {player.gold}")), player.name)]


def sit(services, player:Player, offer) -> list[Message]:
    loss = min(player.hp - 1, round(max_hp(player) * SIT_COST))
    player.hp -= max(0, loss)
    player.gold += SIT_PAY
    if "steam_sweater" not in player.buffs:
        apply_buff(player, "steam_sweater")
    services.repository.save(player)
    return [Message("\n".join((SIT.format(pay=SIT_PAY), f"❤ −{loss} HP.",
                               f"💰 Gold: {player.gold}")), player.name)]

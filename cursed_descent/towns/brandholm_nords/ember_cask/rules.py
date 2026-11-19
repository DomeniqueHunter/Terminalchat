from ....formulas import apply_buff, max_hp
from ....intimacy import fertility
from ....locations.common import pronouns
from ....models import Message, Player
from .content import (
    COUNT_KEY, DAY_KEY, DRINKS, EXPECTING, HALL_LIMIT, PAID, SOLD_OUT,
)


def drink(services, player:Player, offer) -> list[Message]:
    label, price, heal, buff, tier, chance, text = DRINKS[offer.item]
    if player.gold < price:
        return [Message(f"That costs {price} gold. {player.name} only has "
                        f"{player.gold}.", player.name)]
    day = services.world.day
    if tier == "hall":
        if player.profile.get(DAY_KEY) != day:
            player.profile[DAY_KEY] = day
            player.profile[COUNT_KEY] = 0
        if player.profile[COUNT_KEY] >= HALL_LIMIT:
            return [Message(SOLD_OUT, player.name)]
        player.profile[COUNT_KEY] += 1
    player.gold -= price
    gain = round(max_hp(player) * heal)
    player.hp = min(max_hp(player), player.hp + gain)
    lines = [PAID.format(name=player.name, price=price), text,
             f"❤ +{gain} HP."]
    if buff and buff not in player.buffs:
        apply_buff(player, buff)
    if chance and fertility(player) > 0 and (
            services.rng.random() < chance * fertility(player)):
        player.pregnant = "party"
        player.profile["pregnant_by"] = label
        player.profile["pregnant_by_id"] = ""
        lines.append(f"👶 {EXPECTING.format(
            name=player.name, their=pronouns(player.gender)[2])}")
    lines.append(f"💰 Gold: {player.gold}")
    services.repository.save(player)
    return [Message("\n".join(lines), player.name)]

from .config import (
    NEED_RELIEF_INDULGE, NEED_REST_RELIEF, NEED_STARVE_DAMAGE, NEEDS,
)
from .formulas import max_hp
from .models import Player
from .needs import (
    advance, item_needs, label_of, satisfy, starving,
)
from .sweat import sweat_tier


RISE_TEXTS = {
    "hunger": "{name}'s stomach growls – {label}.",
    "thirst": "{name}'s throat is dry – {label}.",
    "sleep": "{name} can barely keep their eyes open – {label}.",
    "arousal": "{name} squirms, heat building – {label}.",
}


def tick_needs(player:Player) -> list[str]:
    extra = {"thirst": sweat_tier(player)}
    lines = [RISE_TEXTS[need].format(name=player.name,
                                     label=label_of(need,
                                                    player.needs[need]))
             for need, _ in advance(player.needs, extra)]
    if starving(player.needs) and player.hp > 1:
        loss = min(player.hp - 1,
                   max(1, round(max_hp(player) * NEED_STARVE_DAMAGE)))
        player.hp -= loss
        lines.append(f"{player.name} weakens from want: -{loss} HP.")
    return lines


def rest_needs(player:Player) -> None:
    satisfy(player.needs, NEED_REST_RELIEF)


def relieve_arousal(player:Player) -> None:
    satisfy(player.needs, NEED_RELIEF_INDULGE)


def reset_needs(player:Player) -> None:
    for need in NEEDS:
        player.needs[need] = 0


def consume(player:Player, item_id:str) -> dict[str, int]:
    return satisfy(player.needs, item_needs(item_id))


def change_text(changes:dict[str, int]) -> str:
    return ", ".join(f"{need} {amount:+d}" for need, amount in changes.items())

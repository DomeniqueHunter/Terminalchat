from ...control.engine import die
from ...models import Message, Player
from .fates import FATES


def fall(services, player:Player, fate:str) -> list[Message]:
    text = services.rng.choice(FATES[fate]["any"]).format(name=player.name)
    return die(services, player, fate, f"💀 {text}")

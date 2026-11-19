import random

from ...models import Player
from ...sweat import sweat_tier
from ...towns import resident
from ...npcs.visit_profile import VisitProfile
from .content import BREWERY_TEXTS


def keeper_greeting(player:Player) -> str:
    pool = list(BREWERY_TEXTS["greet"])
    if sweat_tier(player):
        pool += BREWERY_TEXTS["greet_sweaty"] * 2
    return random.choice(pool).format(name=player.name)


ASTRID = resident("astrid")


VISITS = (
    VisitProfile(
        "astrid", kinds=("brewery",), likes=(("cafe", 2), ("brothel", 1)),
        quirks=(
            ("cafe_arrive", (
                "Astrid Creamworth flares her nostrils, settles her broad "
                "hips and sighs: 'Mmm. Fresh stock.'",)),
            ("cafe_round", (
                "Astrid pats her heavy balls and hums a brewing song "
                "while she grinds down.",
                "'Steady, love,' Astrid purrs. 'Good brew takes time.'")),
            ("brothel_arrive", (
                "Astrid Creamworth ducks under the lintel, counts out her "
                "coins on the bar: 'Everything has a price, darling. I "
                "came to pay mine.'",)))),
)

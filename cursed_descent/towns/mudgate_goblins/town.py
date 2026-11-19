from ...races import RACES
from .. import Town
from .content import BLURB, HAPPENINGS, RUMORS


TOWN = Town(
    key="mudgate",
    name="Mudgate",
    race=RACES["goblin"].plural,
    race_key="goblin",
    blurb=BLURB,
    happenings=HAPPENINGS,
    rumors=RUMORS,
    decency=1,
    lines=("cogsworth",),
)

from ...races import RACES
from .. import Town
from .content import BLURB, HAPPENINGS, RUMORS


TOWN = Town(
    key="dusk_hollow",
    name="Dusk Hollow",
    race=RACES["vampire"].plural,
    race_key="vampire",
    blurb=BLURB,
    happenings=HAPPENINGS,
    rumors=RUMORS,
    decency=0,
    lines=("cogsworth",),
)

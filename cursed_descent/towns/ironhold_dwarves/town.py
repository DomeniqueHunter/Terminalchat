from ...races import RACES
from .. import Town
from .content import BLURB, HAPPENINGS, RUMORS


TOWN = Town(
    key="ironhold",
    name="Ironhold",
    race=RACES["dwarf"].plural,
    race_key="dwarf",
    blurb=BLURB,
    happenings=HAPPENINGS,
    rumors=RUMORS,
    decency=3,
    lines=("cogsworth",),
)

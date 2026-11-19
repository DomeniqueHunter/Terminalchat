from ...races import RACES
from .. import Town
from .content import BLURB, GAZE, HAPPENINGS, RUMORS


TOWN = Town(
    key="brandholm",
    name="Brandholm",
    race=RACES["nord"].plural,
    race_key="nord",
    blurb=BLURB,
    happenings=HAPPENINGS,
    rumors=RUMORS,
    decency=1,
    lines=("cogsworth",),
    gaze=GAZE,
)

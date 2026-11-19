from ...races import RACES
from .. import Town
from .content import BLURB, HAPPENINGS, RUMORS


TOWN = Town(
    key="last_light",
    name="Last Light",
    race=RACES["human"].plural,
    race_key="human",
    blurb=BLURB,
    happenings=HAPPENINGS,
    rumors=RUMORS,
    decency=4,
    lines=("cogsworth",),
)

from ...races import RACES
from .. import Town
from .content import BLURB, HAPPENINGS, RUMORS


TOWN = Town(
    key="cogsworth",
    name="Cogsworth",
    race=RACES["gnome"].plural,
    race_key="gnome",
    blurb=BLURB,
    happenings=HAPPENINGS,
    rumors=RUMORS,
    hub=True,
    decency=2,
    lines=("last_light", "ironhold", "mudgate", "dusk_hollow",
           "brandholm"),
)

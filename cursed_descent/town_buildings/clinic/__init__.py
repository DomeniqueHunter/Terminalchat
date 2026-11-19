from ..base import Building
from . import content


def ui(services, player):
    from ...locations.clinic.ui import panel
    return panel(services, player)


def greeter(player, rng) -> str:
    from ...locations.clinic.location import clinic_advice
    from ...towns import town_of
    from ..greeting import keeper_greeting
    advice = " ".join(clinic_advice(player, town_of(player).key))
    return keeper_greeting(player, "clinic", rng,
                           content.OFFER.format(advice=advice))


class Clinic(Building):
    decency = -1
    key = "clinic"
    icon = "💉"
    greeting = content.OFFER
    help = content.HELP
    greeter = greeter
    ui = ui
    title = "Clinic"
    label = "Clinic"
    blurb = "Dr. <<npc.vane_first>> reshapes bodies for gold."
    order = 40

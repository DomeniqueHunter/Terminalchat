from ...towns import resident
from ...npcs.visit_profile import VisitProfile


GRIZZLE = resident("grizzle")

TINKERWICK = resident("tinkerwick")

SWEATERY_STAFF = {"goblin": (GRIZZLE,), "gnome": (TINKERWICK,)}


VISITS = (
    VisitProfile(
        "grizzle", likes=(("brothel", 1),),
        quirks=(("brothel_arrive", (
            "Grizzle labels the bed, the lamp and you. 'Naked is best, "
            "boots are fine!'",)),)),
    VisitProfile(
        "tinkerwick", likes=(("cafe", 2), ("brothel", 1)),
        quirks=(
            ("cafe_arrive", (
                "Professor Tinkerwick consults a brass instrument, nods "
                "and lowers herself with scientific precision.",)),
            ("cafe_round", (
                "Tinkerwick takes notes with a stub of pencil while she "
                "sits, murmuring: 'Fascinating. Hold still.'",)),
            ("brothel_arrive", (
                "Professor Tinkerwick sets a stopwatch on the nightstand. "
                "'For science, dear.'",)))),
)

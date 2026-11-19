from ...towns import resident
from ...npcs.visit_profile import VisitProfile


JORVEIG = resident("jorveig")

SNIK = resident("snik")

BROKK = resident("brokk")

GRASH = resident("grash")

SMOKERY_STAFF = (JORVEIG, SNIK, BROKK, GRASH)


VISITS = (
    VisitProfile(
        "jorveig", kinds=("smokery",), likes=(("cafe", 3), ("brothel", 1)),
        cruel=2,
        quirks=(
            ("cafe_arrive", (
                "Jorveig Brandsson kicks off her boots at the door. Her "
                "bare feet are enormous, soot-dark at the soles and "
                "unmistakable, and the whole café smells of smoke and "
                "warm skin.",)),
            ("cafe_round", (
                "One of Jorveig's huge bare feet rests on your shoulder, "
                "toes curling against your ear, heavy and warm and "
                "smelling of smokehouse.",
                "Jorveig wiggles her soot-dark toes against your chest "
                "and grinds down. 'Everybody remembers the feet, "
                "darling.'",
                "Jorveig's broad foot presses your cheek sideways while "
                "she sits, as if you were a footstool within a "
                "footstool.")),
            ("brothel_arrive", (
                "Jorveig Brandsson drops her boots by the door. 'Mind "
                "the feet, darling. Everybody remembers the feet.'",)))),
    VisitProfile(
        "snik", likes=(("brothel", 1),),
        quirks=(("brothel_arrive", (
            "Snik Tallyhand counts his coins twice and asks for an "
            "itemised bill.",)),)),
    VisitProfile(
        "brokk", likes=(("brothel", 1),),
        quirks=(("brothel_arrive", (
            "Brokk Ironlatch tests the bed frame with a wrench before "
            "he sits down. 'Sound. Mostly.'",)),)),
    VisitProfile(
        "grash", likes=(("brothel", 1),),
        quirks=(("brothel_arrive", (
            "Grash Longtusk ducks in tusks first. 'Orcs pay in advance. "
            "Orcs also pay extra for polite.'",)),)),
)

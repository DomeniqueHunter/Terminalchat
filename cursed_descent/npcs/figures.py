from ..settings import defaults
from ..towns import resident
from .visit_profile import VisitProfile


BOUTIQUE = defaults("boutique")
MAGE = defaults("mage_tower")

REGINALD = resident("reginald")

VESPER = resident("vesper")

ISOLDE = resident("isolde")

HAMHOCK = resident("hamhock")

TROTTER = resident("old_trotter")

STARCH = resident("starch")

NULL_MASTER = resident("null_master")

ORLEN = resident("archmage_orlen")

ADEPT_BOY = resident("adept_pip")

FIGURES = (REGINALD, VESPER, ISOLDE, HAMHOCK, TROTTER, STARCH,
           NULL_MASTER, ORLEN, ADEPT_BOY)

VISITS = (
    VisitProfile(
        "reginald", kinds=("hunter", "hut"), likes=(("brothel", 1),),
        stance="dominant", cruel=2,
        quirks=(("brothel_arrive", (
            "Sir Reginald Thornbury strides in and sets down his "
            "blunderbuss: 'I do not kneel, old thing. I hunt. Hold "
            "still.'",)),)),
    VisitProfile(
        "vesper", kinds=("boutique", "couture"),
        likes=(("cafe", 2), ("brothel", 1)),
        quirks=(
            ("cafe_arrive", (
                "<<boutique.figure_first>> <<boutique.figure_last>> unwinds her measuring tape, "
                "looks you over like a bolt of cloth and sits down "
                "with a sniff of approval.",)),
            ("cafe_round", (
                "<<boutique.figure_short>> runs the tape along your jaw while she presses "
                "down. 'Strong bone. Good material.'",)),
            ("brothel_arrive", (
                "<<boutique.figure_first>> <<boutique.figure_last>> measures you from head to toe "
                "before she says a word. 'Stand straighter, darling.'",)))),
    VisitProfile(
        "hamhock", kinds=("butcher_shop",), likes=(("brothel", 1),),
        quirks=(("brothel_arrive", (
            "Hamhock wipes his hands on his apron and grins. 'Bring me "
            "something nice and plump.'",)),)),
    VisitProfile(
        "old_trotter", kinds=("farm",), likes=(("brothel", 1),),
        quirks=(("brothel_arrive", (
            "Old Trotter knocks out his pipe and squints. 'A good worker "
            "is worth keeping. Let's see.'",)),)),
    VisitProfile(
        "starch", kinds=("recruiter",), likes=(("cafe", 1), ("brothel", 1)),
        cruel=2,
        quirks=(
            ("cafe_arrive", (
                "Miss Prudence Starch smooths her pinafore, sits with "
                "perfect posture and notes your posture on her "
                "clipboard.",)),
            ("cafe_round", (
                "Starch taps her cane against the floorboards. "
                "'Posture, dear. Even down there.'",)),
            ("brothel_arrive", (
                "Miss Prudence Starch checks her clipboard. 'Quota "
                "first. Then, perhaps, pleasure.'",)))),
    VisitProfile(
        "archmage_orlen", kinds=("mage_tower",), likes=(("brothel", 1),),
        quirks=(("brothel_arrive", (
            "<<mage_tower.owner_short>> sweeps in, rings glittering. 'Do try not to stare. "
            "Everyone does.'",)),)),
    VisitProfile(
        "adept_pip", kinds=("adept",), likes=(("brothel", 1),),
        quirks=(("brothel_arrive", (
            "Pip Primrose tugs the ribbon in his hair, blushing to the "
            "ears. 'I'm n-not nervous. It's a spell. A nervous spell.'",
        )),)),
)

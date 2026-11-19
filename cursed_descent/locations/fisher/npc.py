from ...towns import resident
from ...npcs.visit_profile import VisitProfile


GORM = resident("old_gorm")


VISITS = (
    VisitProfile(
        "old_gorm", kinds=("fisher",), likes=(("brothel", 1),),
        quirks=(("brothel_arrive", (
            "Gorm brings the smell of tar, kelp and old fish into the "
            "room and waits, hat in his huge hands: 'Gentle with fish. "
            "Gentle with you, if you let me.'",)),)),
)

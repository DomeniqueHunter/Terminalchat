from ....routines import Schedule, Stop, Window

ROUTINES = (
    Schedule("alexandra", (
        Stop("blood_bank", 19, 20),
        Stop("tavern", 21, 23),
        Stop("salon", 23, 1),
        Stop("brothel", 1, 2),
    ), uses=("order_drink", "serve_order", "sex_with_slave", "rough_anal",
         "sleep_beside", "feed_slave", "leash_walk", "face_sit"),
        windows=(Window("sleep", 4, 6), Window("eat", 6, 7))),
)

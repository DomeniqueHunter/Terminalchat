from ....routines import Schedule, Stop

ROUTINES = (
    Schedule("bertha", (
        Stop("bank", 10, 11),
        Stop("tavern", 20, 23),
    ), uses=("order_drink", "serve_order")),
)

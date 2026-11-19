from cursed_descent.config import LOCATION_MARK
from cursed_descent.controller import GameController
from cursed_descent.locations.venues import VENUE_KINDS
from tests.test_maid import start_pair


def test_every_location_announcement_carries_the_mark(
        controller:GameController) -> None:
    start_pair(controller)
    events = controller.session.events
    for kind in VENUE_KINDS:
        lines = events.offer_location(kind, 1.0)
        first = next(line for line in lines if line.strip())
        assert first.startswith(LOCATION_MARK), kind
        events.reset()

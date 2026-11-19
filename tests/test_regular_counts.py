import json
import random as rnd
from tests.test_cafe import setup_pair, arrive
from cursed_descent.towns.last_light_humans.cafe.guests import DEADLY, new_guest
from cursed_descent.town_buildings.regulars import slug


def test_random_regular_kills_and_visits(controller) -> None:
    setup_pair(controller)
    controller.handle("Kerl", "!job cafe seat")
    kerl = controller.repository.load("Kerl")
    store = controller.town.regulars_of(kerl)
    store.add("cafe", {"name": "Mrs. Fenwick", "age": 50, "weight": 120,
                       "butt": 150, "cruel": 1})
    guest = None
    for seed in range(200):
        guest = new_guest(rnd.Random(seed), store)
        if guest.name == "Mrs. Fenwick":
            break
    assert guest.name == "Mrs. Fenwick"
    path = store.folder("cafe") / f"{slug(guest.name)}.json"
    visits = json.loads(path.read_text())["visits"]
    assert visits > 1
    arrive(controller, "kerl", guest)
    DEADLY["on"] = True
    try:
        controller.handle("Kerl", "!lick")
    finally:
        DEADLY["on"] = False
    raw = json.loads(path.read_text())
    assert raw.get("kills") == 1, raw

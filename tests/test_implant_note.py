from cursed_descent.content import ITEMS
from cursed_descent.locations.butcher.location import register_implants


def test_implant_size_is_only_in_the_note() -> None:
    entry = {"id": "x1", "name": "Plastica",
             "victim": {"implants": {"butt": 350}}}
    register_implants(entry)
    item = ITEMS["meat_x1_ir"]
    assert "350 cc" in item["note"] and "350" not in item["name"]

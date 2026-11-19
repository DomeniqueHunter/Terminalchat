import json
from pathlib import Path

from cursed_descent.config import HUNG_GENDERS
from cursed_descent.town_buildings.regular_body import (
    body_line, body_values, complete,
)
from cursed_descent.town_buildings.regulars import Regulars
from cursed_descent.town_buildings.visits import status_line


def test_body_values_are_stable_per_name() -> None:
    assert body_values("cafe", "Mrs. Bell") == body_values("cafe", "mrs. bell")


def test_endowment_only_for_hung_genders() -> None:
    for index in range(60):
        values = body_values("brothel", f"Client {index}")
        assert (values["endowment"] > 0) == (values["gender"] in HUNG_GENDERS)
        if values["gender"] == "Male":
            assert values["bust"] <= 50


def test_complete_keeps_existing_values() -> None:
    record = complete("cafe", {"name": "Bell", "gender": "Male", "bust": 7})
    assert record["gender"] == "Male" and record["bust"] == 7
    assert "endowment" in record


def test_new_regular_gets_a_body(tmp_path:Path) -> None:
    store = Regulars(tmp_path, "town", "kerl")
    store.add("cafe", {"name": "Mrs. Bell"})
    record = store.get("cafe", "Mrs. Bell")
    assert {"gender", "bust", "endowment"} <= record.keys()
    assert record["gender"] in ("Female", "Herm", "Cunt-boy")


def test_old_regular_files_are_upgraded(tmp_path:Path) -> None:
    store = Regulars(tmp_path, "town", "kerl")
    path = store.folder("brothel") / "old_man.json"
    path.write_text(json.dumps({"name": "Old Man", "visits": 4}))
    record = store.all("brothel")[0]
    assert record["visits"] == 4 and "gender" in record
    assert "gender" in json.loads(path.read_text())


def test_status_line_shows_the_body() -> None:
    record = {"name": "A", "gender": "Female", "bust": 500, "endowment": 0}
    line = status_line(record)
    assert line.startswith("Female, Large bust (500 cc).") or "500 cc" in line
    assert body_line({"name": "B"}) == ""


def test_cafe_regulars_are_never_cunt_boys(tmp_path:Path) -> None:
    for index in range(200):
        assert body_values("cafe", f"Lady {index}")["gender"] != "Cunt-boy"
    old = complete("cafe", {"name": "Lady X", "gender": "Cunt-boy",
                            "bust": 5})
    assert old["gender"] in ("Female", "Herm")
    assert complete("brothel", {"name": "Y", "gender": "Cunt-boy"}
                    )["gender"] == "Cunt-boy"


def test_regulars_get_family_and_changing_smell(tmp_path:Path) -> None:
    store = Regulars(tmp_path, "town", "kerl")
    store.add("cafe", {"name": "Mrs. Bell", "married": True,
                       "spouse": "Bruno"})
    record = store.get("cafe", "Mrs. Bell")
    assert record["son"] and record["girlfriend"]
    line = body_line(record)
    assert "Family:" in line and "spouse Bruno" in line
    assert "sweat" in line and "musk" in line
    seen = {record["sweat"]}
    for _ in range(12):
        record = store.remember("cafe", record)
        seen.add(record["sweat"])
        assert 0 <= record["sweat"] <= 10 and 0 <= record["musk"] <= 10
    assert len(seen) > 1


def test_handwritten_family_and_smell_are_kept(tmp_path:Path) -> None:
    record = complete("cafe", {"name": "Volena", "son": "Tim", "sweat": 9})
    assert record["son"] == "Tim" and record["sweat"] == 9


def test_smell_notes_scale_with_the_levels() -> None:
    from cursed_descent.town_buildings.regular_body import smell_note
    assert smell_note("Bell", 0, 0) == ""
    assert "musk" in smell_note("Bell", 0, 10)
    assert "sweat" in smell_note("Bell", 10, 0)


def test_musk_drains_the_air_faster() -> None:
    from cursed_descent.towns.last_light_humans.cafe.guests import Guest, smell_drain
    clean = Guest("A", 90, 120)
    musky = Guest("A", 90, 120, musk=10)
    sweaty = Guest("A", 90, 120, sweat=10)
    assert smell_drain(clean) == 0
    assert smell_drain(musky) > smell_drain(sweaty) > 0


def test_heavy_musk_makes_the_home_seat_deadlier() -> None:
    import random
    from cursed_descent.models import Player
    from cursed_descent.towns.last_light_humans.cafe.home_seat import home_sittings

    def deaths(musk:int) -> int:
        record = {"name": "Mrs. Bell", "weight": 130, "butt": 150,
                  "musk": musk, "sweat": musk}
        return sum(bool(home_sittings(Player(name="kerl"), record,
                                      random.Random(seed))[2])
                   for seed in range(200))
    assert deaths(10) > deaths(0)


def test_home_seat_mentions_the_smell() -> None:
    import random
    from cursed_descent.models import Player
    from cursed_descent.towns.last_light_humans.cafe.home_seat import home_sittings
    record = {"name": "Mrs. Bell", "weight": 90, "butt": 120, "sweat": 10,
              "musk": 10}
    lines, _, _ = home_sittings(Player(name="kerl"), record,
                                random.Random(1))
    assert "musk" in lines[0] and "sweat" in lines[0]


def test_out_of_range_cruelty_is_clamped_and_does_not_crash() -> None:
    import random
    from cursed_descent.towns.last_light_humans.cafe.guests import Guest
    from cursed_descent.towns.last_light_humans.cafe.seat import npc_action
    guest = Guest("Lady Volena Wilde", 102, 193, cruel=7)
    assert guest.cruel == 2
    for seed in range(50):
        npc_action(guest, random.Random(seed), [])
    assert complete("cafe", {"name": "V", "cruel": 7})["cruel"] == 2
    assert complete("cafe", {"name": "V", "cruel": -3})["cruel"] == 0


def test_shared_hand_made_regulars_are_picked_and_copied(
        tmp_path:Path) -> None:
    import random
    shared = tmp_path / "npcs" / "regulars" / "town" / "cafe"
    shared.mkdir(parents=True)
    (shared / "lady_volena_wilde.json").write_text(json.dumps(
        {"name": "Lady Volena Wilde", "weight": 102, "butt": 193,
         "age": 63, "cruel": 7}))
    store = Regulars(tmp_path, "town", "kerl")
    assert store.all("cafe") == []
    picked = {store.pick("cafe", random.Random(seed))["name"]
              for seed in range(60)
              if store.pick("cafe", random.Random(seed))}
    assert picked == {"Lady Volena Wilde"}
    from cursed_descent.towns.last_light_humans.cafe.guests import new_guest
    guests = [new_guest(random.Random(seed), store) for seed in range(80)]
    assert any(guest.name == "Lady Volena Wilde" for guest in guests)
    assert store.has("cafe", "Lady Volena Wilde")
    assert store.get("cafe", "Lady Volena Wilde")["cruel"] == 2

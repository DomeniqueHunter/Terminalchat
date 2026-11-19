from cursed_descent.content import ITEMS
from cursed_descent.controller import GameController
from cursed_descent.locations.butcher.location import (
    implant_names, meat_piece_ids, meat_profile, prime_names, register_meat,
)
from cursed_descent.locations.butcher.npc import butcher_comment
from cursed_descent.body import default_body, normalize_body
from cursed_descent.models import Player


def person(name:str, gender:str, **body) -> Player:
    data = default_body()
    data.update(body)
    return Player(name=name, gender=gender, body=normalize_body(data))


def entry_of(player:Player, entry_id:str="e1") -> dict:
    return {"id": entry_id, "name": player.name, "stage": 4,
            "victim": meat_profile(player)}


def test_a_man_gets_prairie_oysters_and_no_breast_fillets() -> None:
    man = person("m", "Male", **{"bust": 0})
    entry = entry_of(man)
    assert prime_names(entry) == ["Prairie Oysters"]


def test_a_busty_woman_gets_breast_fillets_and_rump_roast() -> None:
    woman = person("w", "Female", **{"bust": 600, "butt": 118})
    entry = entry_of(woman)
    assert prime_names(entry) == ["Prime Breast Fillets", "Rump Roast"]
    register_meat(entry)
    ids = meat_piece_ids(entry)
    assert "meat_e1_b" in ids and "meat_e1_r" in ids
    assert ITEMS["meat_e1_b"]["raw_meat"] and "cooked_e1_b" in ITEMS


def test_implants_are_not_meat_and_do_not_count_as_real_bust() -> None:
    woman = person("s", "Female", **{"bust": 900, "fake": {"bust": 900}})
    entry = entry_of(woman, "e2")
    assert prime_names(entry) == []
    assert implant_names(entry) == ["Silicone Breast Implants"]
    register_meat(entry)
    item = ITEMS["meat_e2_ib"]
    assert not item.get("raw_meat") and not item.get("heal")
    assert item["price"] > 25 and "cooked_e2_ib" not in ITEMS


def test_part_real_and_part_fake_bust_gives_fillets_and_implants() -> None:
    woman = person("p", "Female", **{"bust": 900, "fake": {"bust": 300}})
    entry = entry_of(woman, "e3")
    assert prime_names(entry) == ["Prime Breast Fillets"]
    assert implant_names(entry) == ["Silicone Breast Implants"]


def test_fake_balls_are_implants_but_real_balls_are_meat() -> None:
    fake = person("f", "Male", **{"balls": 8, "fake": {"balls": 8}})
    assert implant_names(entry_of(fake, "e4")) == [
        "Silicone Testicle Implants"]
    assert prime_names(entry_of(fake, "e4")) == ["Prairie Oysters"]


def test_old_entries_without_the_new_fields_still_work() -> None:
    entry = {"id": "old", "name": "x", "stage": 1,
             "victim": {"level": 1, "build": "Average", "vitality": 5,
                        "breasts": "None", "shape": "", "weight": 65}}
    assert prime_names(entry) == [] and implant_names(entry) == []
    register_meat(entry)


def test_hamhock_comments_on_prime_cuts_and_implants() -> None:
    woman = person("c", "Female", **{"bust": 900, "fake": {"bust": 300}})
    text = "\n".join(butcher_comment(entry_of(woman, "e5")))
    assert "prime cuts" in text and "Prime Breast Fillets" in text
    assert "Silicone Breast Implants" in text and "curiosity" in text


def test_selling_yourself_to_the_butcher_stocks_the_prime_cuts(
        controller:GameController) -> None:
    session = controller.session
    controller.handle("kerl", "!lobby", now=0.0)
    controller.handle("kerl", "!start", now=1.0)
    session.stage = 8
    session.events.offer_location("butcher_shop", 2.0)
    controller.handle("kerl", "!enter", now=3.0)
    controller.handle("kerl", "!sellself", now=4.0)
    entry = session.remains.entries[-1]
    assert entry["fate"] == "butchered"
    assert any(item.endswith("_t") for item in meat_piece_ids(entry))

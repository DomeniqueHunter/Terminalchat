import random

from cursed_descent.content import BUFFS
from cursed_descent.controller import GameController
from cursed_descent.formulas import max_hp
from cursed_descent.locations.citystop.location import pick_town
from cursed_descent.models import Player
from cursed_descent.races import RACES
from cursed_descent.town_buildings import registry
from cursed_descent.town_buildings.offers import take
from cursed_descent.towns import TOWNS
from tests.test_houses import rich, texts
from tests.test_specials import go_to


TOWN = TOWNS["dusk_hollow"]
COUNTERS = {key: registry.get(key).counter
            for key in ("blood_bank", "salon", "castle")}
WITCHES = {"alexandra", "mina_vasek", "kasia", "nadia"}


class Scripted(random.Random):
    def __init__(self, rolls:list[float]) -> None:
        super().__init__(1)
        self.rolls = list(rolls)

    def random(self) -> float:
        return self.rolls.pop(0) if self.rolls else 0.99

    def choice(self, seq):
        return seq[0]

    def randint(self, low:int, high:int) -> int:
        return low


def hero(name:str="Rex", gender:str="Male") -> Player:
    player = Player(name=name, gold=500, gender=gender)
    player.hp = max_hp(player)
    return player


def test_town_is_registered_with_vampires_and_its_buildings() -> None:
    assert TOWN.name == "Dusk Hollow"
    assert TOWN.race_key == "vampire" and RACES["vampire"].adventurers is False
    assert {"blood_bank", "salon", "castle"} <= set(TOWN.buildings)
    assert len(TOWN.residents) == 23
    for resident in TOWN.residents:
        assert resident.building in TOWN.buildings, resident.key


def test_castle_residents_match_the_plan() -> None:
    by_key = {resident.key: resident for resident in TOWN.residents}
    duchess = by_key["alexandra"]
    assert (duchess.first_name, duchess.last_name) == ("Alexandra", "Markov")
    assert duchess.gender == "Herm" and duchess.age == 340
    assert dict(duchess.body)["bust"] == 1800
    assert by_key["edric_vane"].gender == by_key["tomas_wren"].gender == "Male"
    assert {key for key, resident in by_key.items()
            if resident.building == "castle"} >= WITCHES | {
                "edric_vane", "tomas_wren"}


def test_blood_witches_are_female_or_herm() -> None:
    by_key = {resident.key: resident for resident in TOWN.residents}
    for key in WITCHES:
        assert by_key[key].gender in ("Female", "Herm"), key


def test_donating_pays_costs_hp_and_may_make_faint() -> None:
    from cursed_descent.towns.dusk_hollow_vampires.blood_bank.rules import (
        donate,
    )
    player = hero()
    first = donate(player, None, 0, Scripted([]), 1)
    assert player.gold == 530 and "❤ −" not in " ".join(first)
    assert "blood_faint" in player.buffs
    again = donate(player, None, 0, Scripted([]), 1)
    assert player.gold == 560 and "❤ −" in " ".join(again)
    assert player.hp > 1
    for _ in range(3):
        player.hp = max_hp(player)
        donate(player, None, 0, Scripted([0.0]), 1)
    assert player.hp == 1


def test_a_weak_donor_is_sent_away() -> None:
    player = hero()
    player.hp = 1
    from cursed_descent.towns.dusk_hollow_vampires.blood_bank.rules import (
        donate,
    )
    reply = donate(player, None, 0, random.Random(1), 1)
    assert player.gold == 500 and "Not today" in reply[0]


def test_a_vial_heals_costs_gold_and_resets_the_streak() -> None:
    player = hero()
    player.profile["donations"] = 3
    player.hp = 1
    take(player, COUNTERS["blood_bank"], 2, random.Random(1))
    assert player.hp > 1 and player.gold == 460
    assert player.profile["donations"] == 0
    assert "blood_vigor" in player.buffs


def test_presenting_needs_favor_and_refunds_the_fee() -> None:
    player = hero()
    reply = take(player, COUNTERS["salon"], 5, random.Random(1))
    assert player.gold == 500 and not player.profile.get("castle_invite")
    assert "Not yet" in reply[0].text
    for number in (1, 2):
        take(player, COUNTERS["salon"], number, Scripted([0.99, 0.99]))
    assert player.profile["salon_favor"] == 2
    take(player, COUNTERS["salon"], 5, random.Random(1))
    assert player.profile["castle_invite"] is True
    assert player.gold == 500 - 15 + 20 - 30


def test_a_bite_pays_and_gives_the_pale_kiss() -> None:
    player = hero()
    take(player, COUNTERS["salon"], 3, random.Random(1))
    assert player.gold == 525 and "pale_kiss" in player.buffs
    assert player.profile["salon_favor"] == 1


def test_the_castle_stays_shut_without_an_invitation() -> None:
    player = hero()
    for number in (1, 2):
        reply = take(player, COUNTERS["castle"], number, random.Random(1))
        assert "invitation" in reply[0].text.lower() or (
            "letter" in reply[0].text.lower())
    assert player.gold == 500


def test_audience_outcomes_follow_the_roll() -> None:
    cases = [(0.1, "duchess_favor", 560), (0.5, "", 600), (0.8, "", 500)]
    for roll, buff, gold in cases:
        player = hero()
        player.profile["castle_invite"] = True
        take(player, COUNTERS["castle"], 1, Scripted([roll]))
        assert player.gold == gold, roll
        assert (buff in player.buffs) if buff else True
    man = hero("Rex", "Male")
    woman = hero("Ria", "Female")
    for player, expected in ((man, "castle_leash"), (woman, "castle_rings")):
        player.profile["castle_invite"] = True
        take(player, COUNTERS["castle"], 1, Scripted([0.95]))
        assert expected in player.buffs and player.hp >= 1


def test_banquet_heals_or_bites() -> None:
    player = hero()
    player.profile["castle_invite"] = True
    player.hp = 1
    take(player, COUNTERS["castle"], 2, Scripted([0.1]))
    assert player.hp == max_hp(player)
    take(player, COUNTERS["castle"], 2, Scripted([0.9]))
    assert "castle_bitten" in player.buffs and player.hp < max_hp(player)


def test_all_new_buffs_are_registered() -> None:
    for key in ("blood_faint", "blood_vigor", "salon_poise", "pale_kiss",
                "duchess_favor", "castle_leash", "castle_rings",
                "castle_bitten"):
        assert key in BUFFS and BUFFS[key]["label"]


def test_the_town_can_be_picked_at_the_city_stop() -> None:
    picked = {pick_town([hero()], random.Random(seed)) for seed in range(60)}
    assert "dusk_hollow" in picked


def test_buildings_work_through_the_controller(
        controller:GameController) -> None:
    rich(controller, 100)
    kerl = controller.repository.load("kerl")
    kerl.hp = max_hp(kerl)
    controller.repository.save(kerl)
    go_to(controller, "dusk_hollow")
    reply = texts(controller.handle("kerl", "!blood_bank"))
    assert "Ambrose" in reply and "[blood_bank 1]" in reply
    gold = controller.repository.load("kerl").gold
    reply = texts(controller.handle("kerl", "!blood_bank 1"))
    assert controller.repository.load("kerl").gold == gold + 30, reply
    assert "Vesna" in texts(controller.handle("kerl", "!salon"))
    assert "Mina" in texts(controller.handle("kerl", "!castle"))


def test_other_towns_have_no_vampire_buildings(
        controller:GameController) -> None:
    for key in ("blood_bank", "salon", "castle"):
        assert key not in TOWNS["last_light"].buildings
        assert "no" in texts(controller.handle("kerl", f"!{key}")).lower()


def test_velvet_vein_nightforge_and_crimson_elegance() -> None:
    from cursed_descent.towns.localize import localize_text
    assert {"brothel", "smith", "clinic"} <= set(TOWN.buildings)
    by_key = {resident.key: resident for resident in TOWN.residents}
    staff = [r for r in TOWN.residents if r.building == "brothel"]
    assert staff[0].key == "camilla"
    assert staff[0].first_name == "Mistress Camilla"
    assert (staff[0].last_name, len(staff)) == ("Buxomire", 6)
    assert sorted(r.gender for r in staff[1:]) == [
        "Female", "Female", "Female", "Male", "Male"]
    assert (by_key["ignatius"].last_name, by_key["ignatius"].building) == (
        "Corvan", "smith")
    assert (by_key["leopoldine"].last_name, by_key["leopoldine"].building) == (
        "Graves", "clinic")
    titles = {b.key: b.title for b in TOWN.building_list()}
    assert titles["brothel"] == "The Velvet Vein"
    assert titles["smith"] == "Nightforge"
    assert titles["clinic"] == "Crimson Elegance"
    text = localize_text("Madame <<npc.rose_first>> greets you in the Rose "
                         "Chamber.", TOWN)
    assert "Mistress Camilla" in text and "Madame Mistress" not in text
    assert "Velvet Vein" in text

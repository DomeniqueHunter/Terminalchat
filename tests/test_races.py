from cursed_descent.models import Player
from cursed_descent.npcs.seed import resident_player
from cursed_descent.races import RACES, race_named, race_of, race_of_town
from cursed_descent.towns import TOWNS


def test_every_town_has_a_registered_race() -> None:
    for town in TOWNS.values():
        assert town.race_key in RACES
        assert town.race == RACES[town.race_key].plural


GIANTS = {"camille"}


def test_residents_fit_the_body_range_of_their_race() -> None:
    for town in TOWNS.values():
        for resident in town.residents:
            race = RACES[resident.race or town.race_key]
            body = dict(resident.body)
            if resident.key in GIANTS:
                continue
            assert race.fits(body["height"], body["weight"]), (
                resident.first_name)


def test_residents_get_their_race_and_players_default_to_human() -> None:
    town = TOWNS["mudgate"]
    resident = resident_player(town.residents[0], town="mudgate")
    assert race_of(resident).key == "goblin"
    resident.race = ""
    assert race_of(resident).key == "goblin"
    assert race_of(Player(name="Kerl")).key == "human"
    assert race_named("nonsense").key == "human"


def test_race_data_drives_roughness_and_the_goblin_clinic() -> None:
    assert race_of_town("mudgate").implant_only
    assert not race_of_town("ironhold").implant_only
    rough = [race_of_town(key).roughness for key in
             ("last_light", "cogsworth", "ironhold", "mudgate")]
    assert rough == sorted(rough) and rough[0] == 1.0


def test_race_dialogue_offers_and_drop_ins_differ() -> None:
    from cursed_descent.town_buildings.greeting import greeting_for
    player = Player(name="Kerl")
    player.profile["town"] = "mudgate"
    assert "mud stays outside" in greeting_for(player, "brothel")
    player.profile["town"] = "last_light"
    assert "mud stays outside" not in greeting_for(player, "brothel")
    assert RACES["goblin"].drop_in_sub != RACES["gnome"].drop_in_sub


def test_customers_of_a_race_lean_towards_its_taste() -> None:
    from cursed_descent.town_buildings.body_taste import taste_of
    names = [f"Guest{number}" for number in range(200)]
    for key, part, real in (("goblin", "bust", "fake"),
                            ("dwarf", "butt", "real")):
        hits = sum(taste_of(name, key)[part][1] == real for name in names)
        base = sum(taste_of(name)[part][1] == real for name in names)
        assert hits > base + 40


def test_children_take_the_parents_race_and_grown_goblins_leave() -> None:
    from cursed_descent.births import add_child, age_offspring
    from cursed_descent.config import GROWN_UP_RUNS
    mother = Player(name="Ida", gender="Female")
    mother.race = "dwarf"
    mother.pregnant = "party"
    child = add_child(mother)
    assert child["species"] == "dwarf"
    mother.offspring[0]["runs"] = GROWN_UP_RUNS - 1
    assert "adventurer" in " ".join(age_offspring(mother))
    mother.race = "goblin"
    mother.pregnant = "party"
    add_child(mother)
    mother.offspring[0]["runs"] = GROWN_UP_RUNS - 1
    assert "goblin" in " ".join(age_offspring(mother))


def test_implant_only_bodies_milk_next_to_nothing() -> None:
    from cursed_descent.town_buildings.work.jobs import (
        MILK_FLOOR, milk_yield, real_share)
    futa = Player(name="Fay", gender="Herm")
    futa.body.update({"breasts": "Large", "bust": 900, "balls": 8,
                      "fake": {"bust": 900, "balls": 8}})
    assert real_share(futa) == 0 and milk_yield(futa) == MILK_FLOOR
    futa.body["fake"] = {}
    assert milk_yield(futa) == 1.0


def test_member_values_per_race() -> None:
    assert RACES["human"].member == (15, 12, 5)
    assert RACES["dwarf"].member_shape == "Stout"
    assert RACES["gnome"].member == (9, 8, 3)
    assert RACES["goblin"].member_shape == "Knobbed"


def test_residents_carry_the_member_of_their_race() -> None:
    town = TOWNS["ironhold"]
    resident = resident_player(town.residents[0], town="ironhold")
    assert resident.body["girth"] >= 4
    assert resident.body["endowment_shape"] == "Stout"


def test_proportion_note_depends_on_height() -> None:
    from cursed_descent.partner_detail import proportion_note
    small = Player(name="a", gender="male")
    small.body = {"endowment": 16, "height": 105}
    tall = Player(name="b", gender="male")
    tall.body = {"endowment": 10, "height": 190}
    assert "small frame" in proportion_note(small)
    assert "tall frame" in proportion_note(tall)


def test_creamworth_sisters_are_human_shemales_in_every_town() -> None:
    sisters = [resident for town in TOWNS.values()
               for resident in town.residents
               if resident.building == "brewhouse"]
    assert len(sisters) == 4
    for sister in sisters:
        assert sister.gender == "Shemale" and sister.last_name == "Creamworth"
        player = resident_player(sister, town="ironhold")
        assert race_of(player).key == "human"

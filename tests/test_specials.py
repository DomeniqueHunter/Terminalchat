import random

from cursed_descent.controller import GameController
from cursed_descent.town_buildings import registry
from cursed_descent.town_buildings.offers import offer_price, take
from cursed_descent.towns import TOWNS
from tests.test_houses import rich, texts


SPECIALS = {spec.key: spec.counter for spec in registry.specs().values()
           if spec.counter is not None}


def go_to(controller:GameController, key:str) -> None:
    kerl = controller.repository.load("kerl")
    kerl.profile["town"] = key
    controller.repository.save(kerl)


def test_each_town_has_unique_buildings_only_it_offers() -> None:
    expected = {"ironhold": {"rune_forge", "mine_guild"},
                "cogsworth": {"workshop", "lab"},
                "mudgate": {"black_market", "arena"},
                "dusk_hollow": {"blood_bank", "salon", "castle", "tailor"},
                "brandholm": {"ember_cask", "steam_hall", "sole_hall",
                              "smoke_hall", "snow_ring",
                              "cream_room", "carrying_house", "hall",
                              "feast_hall"}}
    for key, names in expected.items():
        assert names <= set(TOWNS[key].buildings)
        assert not names & set(TOWNS["last_light"].buildings)
    assert set(SPECIALS) - {"brewhouse"} == {name for names in expected.values()
                                             for name in names}
    assert all("brewhouse" in town.buildings for town in TOWNS.values()
               if town.key not in ("dusk_hollow", "brandholm"))


def test_special_menu_and_purchase_in_its_own_town(
        controller:GameController) -> None:
    rich(controller)
    kerl = controller.repository.load("kerl")
    kerl.inventory = []
    controller.repository.save(kerl)
    go_to(controller, "ironhold")
    reply = texts(controller.handle("kerl", "!rune_forge"))
    assert "Rurik" in reply and "[rune_forge 1]" in reply
    before = controller.repository.load("kerl")
    gold, bag = before.gold, len(before.inventory)
    reply = texts(controller.handle("kerl", "!rune_forge 2"))
    after = controller.repository.load("kerl")
    assert "Ring of Vigor" in reply
    assert after.gold < gold
    assert len(after.inventory) == bag + 1


def test_a_special_is_missing_in_other_towns(
        controller:GameController) -> None:
    assert "no" in texts(controller.handle("kerl", "!arena")).lower()
    go_to(controller, "ironhold")
    assert "no" in texts(controller.handle("kerl", "!arena")).lower()


def test_experiment_and_bet_move_gold_and_stay_alive(
        controller:GameController) -> None:
    kerl = controller.repository.load("kerl")
    kerl.gold = 1000
    kerl.hp = 30
    kerl.inventory = []
    rng = random.Random(3)
    for key in ("lab", "arena"):
        gold = kerl.gold
        take(kerl, SPECIALS[key], 1, rng)
        assert kerl.hp >= 1
        assert kerl.gold != gold or key == "lab"


def test_offers_are_priced_and_too_poor_is_refused() -> None:
    assert offer_price(SPECIALS["lab"].offers[0]) == 100
    assert offer_price(SPECIALS["black_market"].offers[0]) > 0
    from cursed_descent.models import Player
    poor = Player(name="Pia", gold=1)
    messages = take(poor, SPECIALS["black_market"], 1, random.Random(1))
    assert "costs" in messages[0].text and poor.gold == 1


def test_guild_jobs_are_timed_shifts(controller:GameController) -> None:
    go_to(controller, "ironhold")
    kerl = controller.repository.load("kerl")
    kerl.hp = kerl.hp or 1
    gold = kerl.gold
    controller.repository.save(kerl)
    reply = texts(controller.handle("kerl", "!mine_guild 1", now=0.0))
    assert "ore hauler" in reply and "5 rounds" in reply
    for step in range(1, 6):
        reply = texts(controller.handle("kerl", "!round", now=float(step)))
    assert "Shift over" in reply and "Foreman Ulgrim keeps" in reply
    assert controller.repository.load("kerl").gold > gold
    reply = texts(controller.handle("kerl", "!rune_forge 4", now=10.0))
    assert "rune carver" in reply and "4 rounds" in reply

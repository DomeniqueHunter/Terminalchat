from cursed_descent.controller import GameController
from cursed_descent.towns.dusk_hollow_vampires.castle import kept_content
from tests.test_houses import rich, texts


def enter_castle(controller:GameController, invited:bool=True) -> None:
    player = controller.repository.load("kerl")
    player.profile.update(town="dusk_hollow", where="castle")
    if invited:
        player.profile["castle_invite"] = True
    player.gold = 1000
    controller.repository.save(player)


def number_of(controller:GameController, master:str) -> int:
    from cursed_descent.towns.dusk_hollow_vampires.castle.content import SPECIAL
    return next(index for index, offer in enumerate(SPECIAL.offers, 1)
                if offer.kind == "kept_contract" and offer.item == master)


def action(controller:GameController, kind:str) -> int:
    from cursed_descent.towns.dusk_hollow_vampires.castle.content import SPECIAL
    return next(index for index, offer in enumerate(SPECIAL.offers, 1)
                if offer.kind == kind)


def sign(controller:GameController, master:str="delphine") -> str:
    return texts(controller.handle(
        "kerl", f"!castle {number_of(controller, master)}"))


def test_contract_needs_the_castle_invitation(
        controller:GameController) -> None:
    enter_castle(controller, invited=False)
    reply = sign(controller)
    assert "Mistress Delphine" not in reply
    assert not controller.repository.load("kerl").profile.get("kept")


def test_signing_makes_the_hero_kept_for_24_hours(
        controller:GameController) -> None:
    enter_castle(controller)
    reply = sign(controller)
    state = controller.repository.load("kerl").profile["kept"]
    assert "Delphine" in reply and state["master"] == "delphine"
    assert round(state["until"] - controller.town.now) == (
        kept_content.HOURS * 3600)
    again = sign(controller, "cassian")
    assert "already kept" in again


def test_kept_hero_cannot_start_a_run_and_can_serve(
        controller:GameController) -> None:
    enter_castle(controller)
    sign(controller, "cassian")
    blocked = texts(controller.handle("kerl", "!start"))
    assert "kept by Master Cassian" in blocked
    gold = controller.repository.load("kerl").gold
    reply = texts(controller.handle(
        "kerl", f"!castle {action(controller, 'kept_serve')}"))
    assert "gold for the service (1/" in reply
    assert controller.repository.load("kerl").gold > gold


def test_serving_is_limited(controller:GameController) -> None:
    enter_castle(controller)
    sign(controller)
    number = action(controller, "kept_serve")
    for _ in range(kept_content.MAX_SERVES):
        controller.handle("kerl", f"!castle {number}")
    reply = texts(controller.handle("kerl", f"!castle {number}"))
    assert "served" in reply and "enough" in reply


def test_contract_ends_after_24_hours_with_pay_and_glow(
        controller:GameController) -> None:
    enter_castle(controller)
    sign(controller)
    gold = controller.repository.load("kerl").gold
    player = controller.repository.load("kerl")
    player.profile["kept"]["until"] = 1.0
    controller.repository.save(player)
    reply = texts(controller.handle("kerl", "!start"))
    player = controller.repository.load("kerl")
    assert "The contract ends" in reply
    assert not player.profile.get("kept")
    assert player.gold == gold + kept_content.PAY
    assert kept_content.GLOW_BUFF in player.buffs


def test_buying_out_costs_gold_and_ends_the_contract(
        controller:GameController) -> None:
    enter_castle(controller)
    sign(controller)
    gold = controller.repository.load("kerl").gold
    reply = texts(controller.handle(
        "kerl", f"!castle {action(controller, 'kept_free')}"))
    player = controller.repository.load("kerl")
    assert "unclips" in reply and not player.profile.get("kept")
    assert player.gold == gold - kept_content.FREE_PRICE


def test_every_master_has_text_and_a_town_for_bondage() -> None:
    assert set(kept_content.MASTERS) == {
        "delphine", "camilla", "cassian", "ignatius", "leopoldine"}
    for master in kept_content.MASTERS.values():
        assert master.title in ("Mistress", "Master")
        assert master.sign and master.serve


def test_bondage_act_exists_only_in_dusk_hollow() -> None:
    from cursed_descent.town_buildings.brothel.practices import (
        acts_in, options_for, parse_choice,
    )
    assert "bondage" in acts_in("dusk_hollow")
    assert "bondage" not in acts_in("last_light")
    assert ("bondage", "give") in options_for("Female", None, "dusk_hollow")
    assert ("bondage", "give") not in options_for("Female", None, "ironhold")
    assert parse_choice(["bondage", "give"], "dusk_hollow") == (
        "bondage", "give")
    assert parse_choice(["bondage", "give"], "ironhold") == ("", "give")

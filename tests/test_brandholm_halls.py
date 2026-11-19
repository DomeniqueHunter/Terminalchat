from cursed_descent.controller import GameController
from cursed_descent.towns.brandholm_nords.sole_hall import content as sole
from cursed_descent.towns.brandholm_nords.steam_hall import content as steam
from cursed_descent.towns.brandholm_nords.smoke_hall import content as smoke


def text(messages) -> str:
    return "\n".join(message.text for message in messages)


def setup(controller:GameController, where:str, gold:int=1000) -> None:
    player = controller.repository.load("Kerl")
    player.profile.update(town="brandholm", where=where)
    player.gold = gold
    player.hp = 10
    controller.repository.save(player)


def test_steam_mask_pays_heals_and_buffs(controller, monkeypatch) -> None:
    setup(controller, "steam_hall")
    entry = steam.CHAMBERS["young"]
    monkeypatch.setitem(steam.CHAMBERS, "young",
                        (entry[0], entry[1], 0.0, *entry[3:]))
    reply = text(controller.handle("Kerl", "!steam_hall 2"))
    player = controller.repository.load("Kerl")
    assert player.gold == 1000 - entry[1] and player.hp > 10
    assert "steam_young" in player.buffs and "Ketil" in reply


def test_steam_mask_can_kill_and_respawns(controller, monkeypatch) -> None:
    setup(controller, "steam_hall")
    entry = steam.CHAMBERS["young"]
    monkeypatch.setitem(steam.CHAMBERS, "young",
                        (entry[0], entry[1], 1.0, *entry[3:]))
    reply = text(controller.handle("Kerl", "!steam_hall 2"))
    player = controller.repository.load("Kerl")
    assert player.deaths.get("sweated") == 1 and "💀" in reply
    assert player.profile["where"] == "town"


def test_steam_herrin_chamber_is_hidden_without_feast(
        controller) -> None:
    setup(controller, "steam_hall")
    assert "Herrin" not in text(controller.handle("Kerl", "!steam_hall"))


def test_sit_in_the_chamber_pays(controller) -> None:
    setup(controller, "steam_hall", gold=0)
    controller.handle("Kerl", "!steam_hall 5")
    player = controller.repository.load("Kerl")
    assert player.gold == steam.SIT_PAY and "steam_sweater" in player.buffs


def test_sole_contract_serve_free_and_lock(controller) -> None:
    setup(controller, "sole_hall")
    assert "Ingibjorg" in text(controller.handle("Kerl", "!sole_hall 1"))
    reply = text(controller.handle("Kerl", "!sole_hall 2"))
    assert "serve 1 of" in reply
    assert "Sole Hall contract" in text(controller.handle("Kerl", "!lobby"))
    controller.handle("Kerl", "!sole_hall 3")
    assert "kept" not in controller.repository.load("Kerl").profile
    assert not controller.repository.load("Kerl").profile.get(sole.STATE_KEY)


def test_sole_contract_pays_after_a_day(controller) -> None:
    setup(controller, "sole_hall", gold=0)
    controller.handle("Kerl", "!sole_hall 1")
    player = controller.repository.load("Kerl")
    player.profile[sole.STATE_KEY]["until"] = 0
    controller.repository.save(player)
    controller.handle("Kerl", "!sole_hall 2")
    player = controller.repository.load("Kerl")
    assert player.gold >= sole.PAY and "sole_glow" in player.buffs


def test_smokehouse_box_can_kill_or_cure(controller, monkeypatch) -> None:
    setup(controller, "smoke_hall", gold=0)
    monkeypatch.setitem(smoke.BOX, "feet", (0.0, smoke.BOX["feet"][1]))
    monkeypatch.setitem(smoke.BOX, "balls", (0.0, smoke.BOX["balls"][1]))
    controller.handle("Kerl", "!smoke_hall 3")
    player = controller.repository.load("Kerl")
    assert player.gold == smoke.FULL_PAY and "smoke_cured" in player.buffs
    monkeypatch.setitem(smoke.BOX, "feet", (1.0, smoke.BOX["feet"][1]))
    monkeypatch.setitem(smoke.BOX, "balls", (1.0, smoke.BOX["balls"][1]))
    controller.handle("Kerl", "!smoke_hall 3")
    assert controller.repository.load("Kerl").deaths.get("hall_smoked") == 1


def test_snow_ring_bet_and_fight(controller, monkeypatch) -> None:
    setup(controller, "snow_ring")
    reply = text(controller.handle("Kerl", "!snow_ring 2"))
    assert "gold" in reply
    reply = text(controller.handle("Kerl", "!snow_ring 3"))
    assert "ring" in reply.lower()


def test_cream_fill_then_blessing_then_fee(controller) -> None:
    setup(controller, "cream_room", gold=1000)
    for _ in range(3):
        controller.handle("Kerl", "!cream_room 2")
    menu = text(controller.handle("Kerl", "!cream_room"))
    assert "blessing" in menu.lower()
    reply = text(controller.handle("Kerl", "!cream_room 3"))
    assert "blessed" in reply
    assert "Matriarch" in text(controller.handle("Kerl", "!lobby"))
    player = controller.repository.load("Kerl")
    player.profile["blessing"]["until"] = 0
    gold = player.gold
    controller.repository.save(player)
    assert "hall thanks you" in text(controller.handle("Kerl", "!lobby"))
    player = controller.repository.load("Kerl")
    assert "blessing" not in player.profile and player.gold == gold - 200
    assert "ember_blessed" in player.buffs


def test_blessing_needs_a_full_belly(controller) -> None:
    setup(controller, "cream_room")
    assert "blessing" not in text(controller.handle("Kerl", "!cream_room"))


def test_carrying_house_ride_and_hire(controller) -> None:
    setup(controller, "carrying_house", gold=100)
    controller.handle("Kerl", "!carrying_house 2")
    player = controller.repository.load("Kerl")
    assert player.gold == 80 and "carried" in player.buffs
    controller.handle("Kerl", "!carrying_house 3")
    assert controller.repository.load("Kerl").gold == 115


def test_feast_opens_the_herrin_casks_and_wheel(controller,
                                                monkeypatch) -> None:
    from cursed_descent.towns.brandholm_nords.feast_hall import content
    setup(controller, "feast_hall")
    assert "Spin the wheel" not in text(
        controller.handle("Kerl", "!feast_hall"))
    controller.handle("Kerl", "!feast_hall 2")
    assert controller.repository.load("Kerl").profile["brandholm_feast"]
    monkeypatch.setattr(content, "WHEEL", (("spit", 1.0), ("mercy", 0.0)))
    monkeypatch.setattr(content, "SPIT_RISK", 1.0)
    from cursed_descent.towns.brandholm_nords.feast_hall import rules
    monkeypatch.setattr(rules, "WHEEL", content.WHEEL)
    monkeypatch.setattr(rules, "SPIT_RISK", 1.0)
    before = controller.repository.load("Kerl").deaths.get("roasted", 0)
    controller.handle("Kerl", "!feast_hall 3")
    after = controller.repository.load("Kerl").deaths.get("roasted", 0)
    assert after == before + 1


def test_herrin_cream_appears_at_the_ember_cask_after_the_feast(
        controller) -> None:
    setup(controller, "ember_cask")
    assert "Herrin's Cream" not in text(
        controller.handle("Kerl", "!ember_cask"))
    player = controller.repository.load("Kerl")
    player.profile.update(brandholm_feast=True, brandholm_feast_day=0)
    controller.repository.save(player)
    assert "Herrin's Cream" in text(controller.handle("Kerl", "!ember_cask"))


def test_men_get_a_gaze_in_brandholm(controller) -> None:
    from cursed_descent.towns import TOWNS
    from cursed_descent.town_buildings.greeting import gaze_line
    import random
    player = controller.repository.load("Kerl")
    player.profile.update(town="brandholm", where="ember_cask")
    player.gender = "Male"
    assert gaze_line(player, "Hjordis", random.Random(1))
    assert TOWNS["brandholm"].gaze

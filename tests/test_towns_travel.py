from cursed_descent.controller import GameController
from cursed_descent.towns import TOWNS, fare_between, town_key
from tests.test_houses import rich, texts


def open_lines(controller:GameController, *keys:str) -> None:
    kerl = controller.repository.load("kerl")
    kerl.profile["rail_pass"] = list(keys)
    controller.repository.save(kerl)


def test_four_towns_each_with_the_shared_services() -> None:
    assert {"last_light", "ironhold", "cogsworth", "mudgate"} <= set(TOWNS)
    for key, town in TOWNS.items():
        if town.wip:
            continue
        services = ("station", "shop", "bank", "tavern", "brothel")
        for service in services:
            assert service in town.buildings, (key, service)
    assert "cafe" not in TOWNS["ironhold"].buildings
    assert TOWNS["cogsworth"].hub


def test_fares_are_cheaper_through_the_gnome_hub() -> None:
    assert fare_between("last_light", "cogsworth") == 30
    assert fare_between("ironhold", "mudgate") == 60
    assert fare_between("mudgate", "mudgate") == 0


def test_station_lists_towns_and_travel_changes_the_town(
        controller:GameController) -> None:
    rich(controller)
    open_lines(controller, "cogsworth")
    reply = texts(controller.handle("kerl", "!station"))
    assert "Cogsworth" in reply and "Ironhold" not in reply
    assert "no rail pass" in texts(controller.handle("kerl",
                                                     "!travel Ironhold"))
    controller.handle("kerl", "!travel Cogsworth")
    assert "Ironhold" not in texts(controller.handle("kerl", "!station"))
    open_lines(controller, "cogsworth", "ironhold")
    assert "Ironhold" in texts(controller.handle("kerl", "!station"))
    gold = controller.repository.load("kerl").gold
    reply = texts(controller.handle("kerl", "!travel Ironhold"))
    assert "Ironhold" in reply
    kerl = controller.repository.load("kerl")
    assert town_key(kerl) == "ironhold" and kerl.gold == gold - 30
    assert "Last Light" in texts(controller.handle("kerl", "!station"))
    assert "no cafe" in texts(controller.handle("kerl", "!cafe")).lower()
    assert "Brenna" in texts(controller.handle("kerl", "!meet"))
    assert "Hilda" not in texts(controller.handle("kerl", "!meet"))
    assert "already" in texts(controller.handle("kerl", "!travel Ironhold"))


def test_travel_needs_the_fare(controller:GameController) -> None:
    kerl = controller.repository.load("kerl")
    kerl.gold = 5
    kerl.profile["rail_pass"] = ["cogsworth"]
    controller.repository.save(kerl)
    assert "fare" in texts(controller.handle("kerl", "!travel cogsworth"))
    assert town_key(controller.repository.load("kerl")) == "last_light"


def test_each_town_has_its_own_house(controller:GameController) -> None:
    rich(controller)
    controller.handle("kerl", "!home buy hut")
    open_lines(controller, "cogsworth")
    controller.handle("kerl", "!travel Cogsworth")
    assert "no house" in texts(controller.handle(
        "kerl", "!home sleep")).lower()


def test_a_visited_town_stays_open_from_anywhere(
        controller:GameController) -> None:
    rich(controller)
    open_lines(controller, "cogsworth", "mudgate")
    controller.handle("kerl", "!travel Cogsworth")
    controller.handle("kerl", "!travel Mudgate")
    controller.handle("kerl", "!travel Cogsworth")
    controller.handle("kerl", "!travel Last Light")
    reply = texts(controller.handle("kerl", "!station"))
    assert "Mudgate" in reply and "Cogsworth" in reply
    assert "Ironhold" not in reply and "still closed" in reply


def test_the_rail_pass_comes_from_the_stationmaster(
        controller:GameController) -> None:
    rich(controller)
    kerl = controller.repository.load("kerl")
    kerl.profile["town"] = "cogsworth"
    controller.repository.save(kerl)
    reply = texts(controller.handle("kerl", "!ticket"))
    assert "Tobble" in reply and "[ticket pay]" in reply
    gold = controller.repository.load("kerl").gold
    reply = texts(controller.handle("kerl", "!ticket pay"))
    kerl = controller.repository.load("kerl")
    assert kerl.gold == gold - 150 and "cogsworth" in kerl.profile[
        "rail_pass"]
    assert "already" in texts(controller.handle("kerl", "!ticket sleep"))


def test_sleeping_with_the_stationmaster_opens_the_line(
        controller:GameController) -> None:
    rich(controller)
    kerl = controller.repository.load("kerl")
    kerl.profile["town"] = "mudgate"
    controller.repository.save(kerl)
    assert "Klink" in texts(controller.handle("kerl", "!ticket sleep"))
    assert "mudgate" in controller.repository.load("kerl").profile[
        "rail_pass"]

from cursed_descent.town_buildings.menu import MENUS, find_dish


def text(messages) -> str:
    return "\n".join(message.text for message in messages)


def test_menus_list_and_order_by_number_or_name(controller) -> None:
    assert "Menu" in text(controller.handle("Kerl", "!order tavern"))
    assert "Bowl of hot stew" in text(controller.handle("Kerl", "!tavern"))
    assert "cheesecake" in text(controller.handle("Kerl", "!cafe"))
    player = controller.repository.load("Kerl")
    player.needs["hunger"] = 80
    player.gold = 100
    controller.repository.save(player)
    reply = text(controller.handle("Kerl", "!order tavern stew"))
    assert "eats Bowl of hot stew" in reply and "hunger -45" in reply
    after = controller.repository.load("Kerl")
    assert after.needs["hunger"] == 35 and after.gold == 92
    player = controller.repository.load("Kerl")
    player.needs["thirst"] = 50
    controller.repository.save(player)
    assert "thirst -40" in text(controller.handle("Kerl", "!order cafe 1"))
    assert controller.repository.load("Kerl").gold == 89


def test_order_needs_gold_and_a_known_building(controller) -> None:
    player = controller.repository.load("Kerl")
    player.gold = 0
    controller.repository.save(player)
    assert "costs" in text(controller.handle("Kerl", "!order cafe feast"))
    assert "[order tavern" in text(controller.handle("Kerl", "!order"))


def test_find_dish() -> None:
    assert find_dish("cafe", "2") == "slice"
    assert find_dish("tavern", "Mug of ale") == "ale"
    assert find_dish("tavern", "nothing") == ""
    assert all(len(menu) == 5 for menu in MENUS.values())


def test_consume_works_in_combat_without_losing_the_turn(controller) -> None:
    player = controller.repository.load("Kerl")
    player.inventory = ["stew_jar"]
    player.needs["hunger"] = 60
    controller.repository.save(player)
    controller.handle("Kerl", "!lobby")
    controller.handle("Kerl", "!start")
    assert controller.session.state == "combat"
    reply = text(controller.handle("Kerl", "!consume 1"))
    assert "consumes" in reply and "hunger" in reply
    assert controller.repository.load("Kerl").inventory == []
    assert controller.session.state == "combat"


def test_consume_in_town_heals_and_feeds(controller) -> None:
    player = controller.repository.load("Kerl")
    player.inventory = ["potion_small"]
    controller.repository.save(player)
    assert "consumes" in text(controller.handle("Kerl", "!consume 1"))
    assert "Usage" in text(controller.handle("Kerl", "!consume 1"))


def test_order_to_go_goes_into_the_bag_and_can_be_consumed(controller) -> None:
    player = controller.repository.load("Kerl")
    player.gold = 50
    player.inventory = []
    player.needs["hunger"] = 70
    controller.repository.save(player)
    reply = text(controller.handle("Kerl", "!order tavern stew take"))
    assert "to go" in reply
    mid = controller.repository.load("Kerl")
    assert mid.gold == 42 and mid.inventory == ["dish_tavern_stew"]
    assert mid.needs["hunger"] == 70
    assert "consumes" in text(controller.handle("Kerl", "!consume 1"))
    after = controller.repository.load("Kerl")
    assert after.needs["hunger"] == 25 and after.inventory == []
    assert "to go" in text(controller.handle("Kerl", "!order cafe 3 take"))


def test_takeaway_needs_a_free_bag_slot(controller) -> None:
    player = controller.repository.load("Kerl")
    player.gold = 50
    player.inventory = ["potion_small"] * player.bag_size
    controller.repository.save(player)
    assert "bag is full" in text(controller.handle(
        "Kerl", "!order tavern ale take"))
    assert controller.repository.load("Kerl").gold == 50


def test_eating_while_sitting_makes_the_lady_heavier(controller) -> None:
    from cursed_descent.towns.last_light_humans.cafe.guests import Guest
    from cursed_descent.towns.last_light_humans.cafe.stools import Stool
    kerl = controller.repository.load("Kerl")
    kerl.gender = "Male"
    controller.repository.save(kerl)
    lady = controller.repository.load("Galactica")
    lady.gender = "Female"
    lady.gold = 200
    lady.inventory = []
    controller.repository.save(lady)
    controller.handle("Kerl", "!job cafe seat", now=0.0)
    controller.handle("Galactica", "!sit Kerl", now=1.0)
    weight = controller.town.shifts["kerl"].client.weight
    reply = controller.handle("Galactica", "!order cafe feast", now=2.0)
    assert any(m.recipient == "kerl" and "6 kg heavier" in m.text
               for m in reply)
    assert controller.town.shifts["kerl"].client.weight == weight + 6
    controller.handle("Galactica", "!order cafe tea", now=3.0)
    assert controller.town.shifts["kerl"].client.weight == weight + 6
    controller.handle("Galactica", "!rise", now=4.0)
    assert controller.town.shifts["kerl"].client is None
    controller.handle("Kerl", "!quit", now=5.0)
    controller.town.stools = [Stool("Tom", 30, 190, 90, "Muscular", 70,
                                    "eager")]
    controller.handle("Galactica", "!sit 1", now=6.0)
    assert "heavier on Tom" in text(controller.handle(
        "Galactica", "!order tavern roast", now=7.0))
    assert controller.town.rides["Galactica"].extra == 3
    controller.handle("Galactica", "!order tavern stew take", now=8.0)
    assert "heavier on Tom" in text(controller.handle(
        "Galactica", "!consume 1", now=9.0))
    assert controller.town.rides["Galactica"].extra == 5
    controller.handle("Galactica", "!rise", now=10.0)
    assert controller.town.rides == {}
    assert Guest

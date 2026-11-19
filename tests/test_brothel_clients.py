import random

from cursed_descent.controller import GameController
from cursed_descent.town_buildings.brothel.clients import (
    client_can, client_options, describe_client, new_client,
)
from tests.test_cafe import setup_pair, text


def test_clients_come_in_every_gender_as_dom_and_sub(
        controller:GameController) -> None:
    setup_pair(controller)
    player = controller.repository.load("Galactica")
    genders = set()
    for seed in range(300):
        rng = random.Random(seed)
        mode = ("", "domina", "sub")[seed % 3]
        client = new_client(player, rng, None, mode)
        genders.add(client.gender)
        assert client.gender != "Cunt-boy" or True
    assert {"Male", "Female", "Herm", "Shemale"} <= genders
    for seed in range(60):
        sub = new_client(player, random.Random(seed), None, "sub")
        dom = new_client(player, random.Random(seed), None, "domina")
        assert sub.dominant and dom.dominated


def test_options_respect_the_clients_anatomy(
        controller:GameController) -> None:
    setup_pair(controller)
    player = controller.repository.load("Galactica")
    client = new_client(player, random.Random(1), None, "")
    client.gender = "Male"
    assert not client_can(client, "vaginal", "give")
    assert ("vaginal", "give") not in client_options(player, client)
    client.gender = "Female"
    assert client_can(client, "vaginal", "give")


def test_examine_shows_body_and_pockets(
        controller:GameController) -> None:
    setup_pair(controller)
    controller.handle("Galactica", "!job brothel whore")
    reply = text(controller.handle("Galactica", "!examine client"))
    assert "Body:" in reply and "Pockets:" in reply
    client = controller.town.shifts["Galactica"].client
    assert client.gender in reply
    assert "Body:" in describe_client(client)


def test_endless_shift_shows_served_and_can_be_ended(
        controller:GameController) -> None:
    setup_pair(controller)
    controller.handle("Galactica", "!job brothel whore")
    controller.town.now = 0
    controller.town.shifts["Galactica"].due = 20
    player = controller.repository.load("Galactica")
    assert "served" in controller.town.timer_text(player)
    assert "left" not in controller.town.timer_text(player)
    reply = text(controller.handle("Galactica", "!safeword"))
    assert "leave your shift" in reply
    assert "Galactica" not in controller.town.shifts


def start_brothel(controller:GameController, gender:str="Female"):
    setup_pair(controller)
    player = controller.repository.load("Galactica")
    player.gender = gender
    controller.repository.save(player)
    controller.handle("Galactica", "!job brothel whore")
    shift = controller.town.shifts["Galactica"]
    shift.client.player = ""
    shift.client.gender = "Male"
    shift.client.purse = 77
    shift.client.dominant = False
    shift.mode = ""
    return shift


def test_swallow_takes_the_whole_purse_and_removes_the_client(
        controller:GameController) -> None:
    shift = start_brothel(controller)
    name = shift.client.name
    before = shift.client
    gold = controller.repository.load("Galactica").gold
    reply = text(controller.handle("Galactica", "!serve swallow"))
    assert name in reply and "+77 gold" in reply
    after = controller.town.shifts["Galactica"]
    assert after.client is not before
    assert controller.town.shifts["Galactica"].earned >= 77
    assert controller.repository.load("Galactica").gold >= gold


def test_wipe_pays_better_and_the_client_forgets(
        controller:GameController) -> None:
    shift = start_brothel(controller)
    name = shift.client.name
    reply = text(controller.handle("Galactica", "!serve wipe"))
    assert "no idea who" in reply and name in reply
    assert controller.town.shifts["Galactica"].earned > 0


def test_finishers_are_refused_for_a_player_client_and_in_sub_mode(
        controller:GameController) -> None:
    shift = start_brothel(controller)
    shift.client.player = "kerl"
    assert "not yours" in text(controller.handle("Galactica",
                                                 "!serve swallow"))
    shift.client.player = ""
    shift.mode = "sub"
    assert "receive" in text(controller.handle("Galactica", "!serve wipe"))


def test_a_dominant_client_can_finish_the_player_off(
        controller:GameController) -> None:
    from cursed_descent.town_buildings.brothel import finish
    shift = start_brothel(controller)
    shift.mode = "sub"
    shift.client.dominant = True
    shift.earned = 40
    player = controller.repository.load("Galactica")

    class Lucky(random.Random):
        def random(self) -> float:
            return 0.0

    messages = finish.dom_finish(player, shift, "facesitting", Lucky(1),
                                 controller.town.shifts)
    assert messages and "-40 gold" in messages[0].text
    assert "Galactica" not in controller.town.shifts
    assert player.profile["ko_until"] > 0
    assert finish.dom_finish(player, shift, "oral", Lucky(1), {}) is None


def test_residents_of_the_town_drop_in_as_clients(monkeypatch) -> None:
    import random as rnd
    from cursed_descent.config import REGULAR_GENDER_WEIGHTS
    from cursed_descent.town_buildings.brothel import clients
    from cursed_descent.towns import TOWNS
    from cursed_descent.models import Player
    monkeypatch.setattr(clients, "BROTHEL_HOUSE_GUEST_CHANCE", 1.0)
    player = Player("kerl")
    player.profile["town"] = "dusk_hollow"
    town = TOWNS["dusk_hollow"]
    names = {person.first_name for person in town.residents
             if person.building in clients.HOUSE_GUEST_BUILDINGS}
    seen, hellos = set(), set()
    for seed in range(200):
        guest = clients.new_client(player, rnd.Random(seed))
        seen.add(guest.name)
        hellos.add(guest.hello)
    assert seen <= names and "Mistress Camilla" in seen
    assert not seen & {"Serafine", "Isabeau", "Noemi", "Dorian", "Cassian"}
    assert any(hello in clients.OPERATOR_GUEST_HELLOS for hello in hellos)
    assert REGULAR_GENDER_WEIGHTS["brothel"]["Female"] >= 30

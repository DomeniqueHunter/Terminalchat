from pathlib import Path

from cursed_descent.models import Message
from cursed_descent.web import audience
from cursed_descent.web.hub import GameHub


def put(hub:GameHub, name:str, where:str) -> None:
    player = hub.controller.repository.load(name)
    player.profile["where"] = where
    hub.controller.repository.save(player)


def test_witnesses_see_the_actor_by_name(data_path:Path) -> None:
    hub = GameHub(data_path)
    put(hub, "kerl", "cafe")
    put(hub, "galactica", "cafe")
    message = Message("You sit.", "kerl", witness="You see {actor} sit.")
    names, entry = audience.witnesses(hub.controller, "kerl", message)
    assert "Galactica" in names and "kerl" not in names
    assert entry["text"] == "You see kerl sit." and entry["kind"] == "witness"


def test_other_places_see_nothing(data_path:Path) -> None:
    hub = GameHub(data_path)
    put(hub, "kerl", "cafe")
    put(hub, "galactica", "shop")
    message = Message("x", "kerl", witness="You see {actor}.")
    assert audience.witnesses(hub.controller, "kerl", message) is None


def test_private_places_stay_private(data_path:Path) -> None:
    hub = GameHub(data_path)
    put(hub, "kerl", "brothel")
    put(hub, "galactica", "brothel")
    message = Message("x", "kerl", witness="You see {actor}.")
    assert audience.witnesses(hub.controller, "kerl", message) is None


def test_no_witness_text_means_no_item(data_path:Path) -> None:
    hub = GameHub(data_path)
    put(hub, "kerl", "cafe")
    put(hub, "galactica", "cafe")
    assert audience.witnesses(hub.controller, "kerl",
                              Message("x", "kerl")) is None


def test_the_cafe_emitters_carry_witness_text() -> None:
    from cursed_descent.towns.last_light_humans.cafe import content
    for text in (content.WITNESS_SEAT, content.WITNESS_DONE,
                 content.WITNESS_QUIT, content.WITNESS_FURNITURE,
                 *content.WITNESS_DEATH.values()):
        assert "{actor}" in text

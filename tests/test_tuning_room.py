from pathlib import Path

import pytest

from cursed_descent.commands import parse_chat
from cursed_descent.config import TUNING_PRICE
from cursed_descent.orientation import likes_of
from cursed_descent.settings import PROTOTYPES, ensure_loaded
from cursed_descent.towns.last_light_humans.tuning_room.content import COACHES
from cursed_descent.towns.last_light_humans.tuning_room.rules import options
from cursed_descent.towns import TOWNS
from cursed_descent.web.hub import GameHub


def prepare(hub:GameHub, gender:str, gold:int=1000, likes:str="both",
            town:str="last_light"):
    player = hub.controller.repository.load("kerl")
    player.gender = gender
    player.gold = gold
    player.profile["orientation"] = likes
    player.profile["where"] = "tuning_room"
    player.profile["town"] = town
    player.profile.pop("tuning_day", None)
    hub.controller.repository.save(player)
    return player


def run(hub:GameHub, line:str) -> list:
    return hub.controller.execute("kerl", parse_chat(f"!{line}"))


def texts(messages:list) -> str:
    return " ".join(message.text for message in messages)


def kinds(gender:str) -> dict[str, str]:
    from cursed_descent.models import Player
    stub = Player.from_dict({"name": "x", "gender": gender})
    return {option.coach: option.kind for option in options(stub)}


def test_the_five_coaches_exist_in_last_light() -> None:
    ensure_loaded()
    keys = {resident.key for resident in TOWNS["last_light"].residents
            if resident.building == "tuning_room"}
    assert keys == set(COACHES)
    assert "tuning_room" in TOWNS["last_light"].buildings
    assert all(PROTOTYPES[key]["race"] == "human" for key in COACHES)
    assert PROTOTYPES["camille"]["gender"] == "Herm"
    assert PROTOTYPES["camille"]["profile"]["nickname"] == "One-Way Ticket"


def test_offers_by_gender() -> None:
    assert kinds("Male") == {"seraphine": "straight", "taren": "fag",
                             "camille": "fag", "ilaria": "bi"}
    assert kinds("Female") == {"seraphine": "straight", "ysolde": "lesbian",
                               "ilaria": "bi"}
    assert kinds("Shemale") == {"seraphine": "straight", "camille": "homo",
                                "ilaria": "bi"}
    assert kinds("Cunt-boy") == {"seraphine": "straight", "camille": "homo",
                                 "ilaria": "bi"}
    assert kinds("Herm") == {"ilaria": "bi"}
    assert kinds("None") == {}


def test_fag_training_for_a_man(data_path:Path) -> None:
    hub = GameHub(data_path)
    prepare(hub, "Male", likes="vagina")
    text = texts(run(hub, "tuning_room taren"))
    assert "Fag training" in text
    player = hub.controller.repository.load("kerl")
    assert likes_of(player) == "penis" and player.gold == 1000 - TUNING_PRICE


def test_lesbian_straight_and_bi(data_path:Path) -> None:
    hub = GameHub(data_path)
    prepare(hub, "Female", likes="penis")
    run(hub, "tuning_room ysolde")
    assert likes_of(hub.controller.repository.load("kerl")) == "vagina"
    prepare(hub, "Female", likes="vagina")
    run(hub, "tuning_room seraphine")
    assert likes_of(hub.controller.repository.load("kerl")) == "penis"
    prepare(hub, "Female", likes="penis")
    run(hub, "tuning_room ilaria")
    assert likes_of(hub.controller.repository.load("kerl")) == "both"


def test_one_training_per_game_day(data_path:Path) -> None:
    hub = GameHub(data_path)
    prepare(hub, "Male", likes="vagina")
    run(hub, "tuning_room taren")
    assert "Once a day" in texts(run(hub, "tuning_room ilaria"))
    hub.controller.town.world.day += 1
    assert "Bi training" in texts(run(hub, "tuning_room ilaria"))


def test_admins_train_free_and_without_waiting(data_path:Path) -> None:
    hub = GameHub(data_path)
    hub.controller.is_admin = lambda name: True
    prepare(hub, "Male", gold=10, likes="vagina")
    assert "Fag training" in texts(run(hub, "tuning_room taren"))
    assert "Bi training" in texts(run(hub, "tuning_room ilaria"))
    assert hub.controller.repository.load("kerl").gold == 10
    assert "free" in texts(run(hub, "tuning_room"))


def test_the_wrong_coach_and_the_same_wish(data_path:Path) -> None:
    hub = GameHub(data_path)
    prepare(hub, "Female", likes="vagina")
    assert "not my kind of teaching" in texts(run(hub, "tuning_room taren"))
    assert "Nothing to change" in texts(run(hub, "tuning_room ysolde"))
    assert hub.controller.repository.load("kerl").gold == 1000


def test_poor_guests_pay_nothing(data_path:Path) -> None:
    hub = GameHub(data_path)
    prepare(hub, "Male", gold=10, likes="vagina")
    assert "do not have it" in texts(run(hub, "tuning_room taren"))
    assert likes_of(hub.controller.repository.load("kerl")) == "vagina"


def test_closed_in_other_towns(data_path:Path) -> None:
    hub = GameHub(data_path)
    prepare(hub, "Male", town="ironhold")
    assert "no tuning_room in Ironhold" in texts(run(hub, "tuning_room"))


def test_training_is_seen_by_the_room(data_path:Path) -> None:
    hub = GameHub(data_path)
    prepare(hub, "Male", likes="vagina")
    messages = run(hub, "tuning_room taren")
    assert any("silk screen" in message.witness for message in messages)


def test_menu_lists_the_offers(data_path:Path) -> None:
    hub = GameHub(data_path)
    prepare(hub, "Female")
    text = texts(run(hub, "tuning_room"))
    assert "Mother Ysolde Marrow: Lesbian training" in text
    assert "Taren" not in text


def test_the_panel_shows_the_offers(data_path:Path) -> None:
    hub = GameHub(data_path)
    prepare(hub, "Male", likes="vagina")
    from cursed_descent.towns.last_light_humans.tuning_room.ui import panel
    shown = panel(hub.controller.town, hub.controller.repository.load("kerl"))
    commands = [button.command for button in shown.buttons]
    assert "!tuning_room taren" in commands and "!tuning_room ilaria" in commands
    assert all(button.enabled for button in shown.buttons
               if "ilaria" in button.command)

from cursed_descent.combat import RoundResult, kill_player
from cursed_descent.content import ENEMIES, EVENT_TEXTS, FATES
from cursed_descent.controller import GameController
from cursed_descent.dungeon import build_enemy
from cursed_descent.spawns import RULES_BY_KIND


def texts(messages) -> str:
    return "\n".join(message.text for message in messages)


def recruiter_defeats(controller:GameController, name:str) -> list[str]:
    session = controller.session
    player = controller.repository.load(name)
    session.party = [player]
    session.state = "combat"
    enemy = build_enemy(1, "school_recruiter", ENEMIES["school_recruiter"], 4)
    player.last_hit_by = enemy
    result = RoundResult()
    kill_player(player, result)
    assert player.last_fate == "recruited"
    return session.record_deaths(result.fallen, 4)


def test_recruiter_is_a_registered_event_enemy() -> None:
    assert RULES_BY_KIND["recruiter"].min_stage == 3
    assert ENEMIES["school_recruiter"]["fates"] == ["recruited"]
    assert "recruiter" in EVENT_TEXTS and "recruited" in FATES


def test_defeat_offers_the_contract(controller:GameController) -> None:
    notes = recruiter_defeats(controller, "kerl")
    assert "[accept]" in "\n".join(notes) and "[decline]" in "\n".join(notes)
    assert "kerl" in controller.session.recruit_offers


def test_accept_turns_the_character_into_a_maid(
        controller:GameController) -> None:
    recruiter_defeats(controller, "kerl")
    output = texts(controller.handle("kerl", "!accept"))
    assert "buyback" in output and "gold" in output
    player = controller.repository.load("kerl")
    assert player.npc == "maid"
    assert controller.repository.npc_path("kerl").exists()
    assert not controller.repository.path("kerl").exists()
    assert "kerl" not in controller.session.recruit_offers


def test_decline_keeps_the_adventurer(controller:GameController) -> None:
    recruiter_defeats(controller, "kerl")
    output = texts(controller.handle("kerl", "!decline"))
    assert "over for kerl" in output
    assert controller.repository.load("kerl").npc == ""
    assert "kerl" not in controller.session.recruit_offers


def test_open_offer_blocks_a_new_lobby(controller:GameController) -> None:
    recruiter_defeats(controller, "kerl")
    controller.session.reset()
    output = texts(controller.handle("kerl", "!lobby"))
    assert "[accept] or [decline]" in output
    controller.handle("kerl", "!decline")
    assert "opens the gate" in texts(controller.handle("kerl", "!lobby"))


def test_accept_without_an_offer_is_not_hijacked(
        controller:GameController) -> None:
    controller.handle("kerl", "!accept")
    assert controller.repository.load("kerl").npc == ""

from pathlib import Path

from cursed_descent.controller import GameController
from cursed_descent.events.null_master.content import RIDDLES
from cursed_descent.events.null_master.event import correct_answer
from cursed_descent.models import Player
from tests.ready import confirm
from cursed_descent.spawns import RULES_BY_KIND


def say(controller:GameController, name:str, text:str) -> str:
    return "\n".join(m.text for m in controller.handle(name, text))


def start(tmp_path:Path) -> GameController:
    controller = GameController(tmp_path, debug=True)
    controller.repository.save(Player(name="Hero", gold=5000))
    controller.repository.save(Player(name="Pal"))
    say(controller, "Hero", "!lobby")
    say(controller, "Pal", "!join")
    say(controller, "Hero", "!start")
    confirm(controller)
    say(controller, "Hero", "!trigger null_master")
    return controller


def answers_now(controller:GameController) -> tuple[str, ...]:
    data = controller.session.events.event["data"]
    return data["riddles"][data["index"]][1]


def test_null_master_is_registered() -> None:
    assert RULES_BY_KIND["null_master"].min_stage == 6
    assert len(RIDDLES) >= 12


def test_answers_match_loosely() -> None:
    assert correct_answer("It is an ECHO!", ("echo",))
    assert not correct_answer("a mirror", ("echo",))


def test_three_right_answers_reward_the_party(tmp_path:Path) -> None:
    controller = start(tmp_path)
    assert controller.session.events.event["kind"] == "null_master"
    gold = controller.session.party[0].gold
    for _ in range(3):
        word = answers_now(controller)[0]
        output = say(controller, "Hero", f"!answer {word}")
        assert "right" in output
    assert "Three" in output
    assert controller.session.party[0].gold > gold
    assert controller.session.state != "event"


def test_a_wrong_answer_makes_a_drone(tmp_path:Path) -> None:
    controller = start(tmp_path)
    output = say(controller, "Pal", "!answer definitely wrong xyz")
    assert "wrong" in output and "Quiet now" in output
    pal = controller.repository.load("Pal")
    assert pal.npc == "drone" and pal.profile["kind"] == "drone"
    assert controller.repository.npc_path("Pal").exists()
    assert "Pal" not in controller.repository.names()
    assert controller.session.events.event["data"]["index"] == 1


def test_everyone_failing_ends_the_run(tmp_path:Path) -> None:
    controller = start(tmp_path)
    say(controller, "Pal", "!answer zzz")
    output = say(controller, "Hero", "!answer zzz")
    assert "fallen" in output
    assert controller.session.state in ("idle", "lobby")


def test_ransom_frees_a_drone(tmp_path:Path) -> None:
    controller = start(tmp_path)
    say(controller, "Pal", "!answer zzz")
    controller.session.reset()
    assert "Pal" in say(controller, "Hero", "!ransom")
    assert "pays" in say(controller, "Hero", "!ransom pal")
    pal = controller.repository.load("Pal")
    assert pal.npc == "" and "Pal" in controller.repository.names()
    assert not controller.repository.npc_path("Pal").exists()


def test_ransomed_drone_keeps_its_preferences(tmp_path:Path) -> None:
    controller = start(tmp_path)
    pal = controller.repository.load("Pal")
    pal.profile["consent"] = "deny"
    controller.repository.save(pal)
    say(controller, "Pal", "!answer zzz")
    controller.session.reset()
    say(controller, "Hero", "!ransom pal")
    assert controller.repository.load("Pal").profile["consent"] == "deny"


def test_depart_refuses_the_game(tmp_path:Path) -> None:
    controller = start(tmp_path)
    assert "Refusing" in say(controller, "Hero", "!depart")

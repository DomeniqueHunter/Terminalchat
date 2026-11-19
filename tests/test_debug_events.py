from pathlib import Path

from cursed_descent.controller import GameController
from cursed_descent.spawns import SPAWN_RULES


def texts(messages) -> str:
    return "\n".join(message.text for message in messages)


def start_run(controller:GameController) -> None:
    controller.handle("kerl", "!lobby")
    controller.handle("kerl", "!start")


def test_commands_are_ignored_without_debug(
        controller:GameController) -> None:
    assert controller.handle("kerl", "!events") == []
    assert controller.handle("kerl", "!trigger wanderer") == []


def test_events_lists_every_spawn_rule(data_path:Path) -> None:
    controller = GameController(data_path, debug=True)
    output = texts(controller.handle("kerl", "!events"))
    assert all(rule.kind in output for rule in SPAWN_RULES)


def test_trigger_needs_a_run_and_a_known_event(data_path:Path) -> None:
    controller = GameController(data_path, debug=True)
    assert "Start a run" in texts(controller.handle("kerl",
                                                    "!trigger wanderer"))
    start_run(controller)
    assert "Unknown event" in texts(controller.handle("kerl",
                                                      "!trigger nothing"))
    assert "Usage" in texts(controller.handle("kerl", "!trigger"))


def test_trigger_starts_each_event_kind(data_path:Path) -> None:
    for rule in SPAWN_RULES:
        controller = GameController(data_path, debug=True)
        start_run(controller)
        output = texts(controller.handle("kerl",
                                         f"!trigger {rule.kind}"))
        assert output, rule.kind
        assert controller.session.state in ("event", "combat"), rule.kind


def test_trigger_recruiter_starts_the_bonus_fight(data_path:Path) -> None:
    controller = GameController(data_path, debug=True)
    start_run(controller)
    controller.handle("kerl", "!trigger recruiter")
    assert controller.session.bonus_fight == "recruiter"
    assert controller.session.enemies[0].name == "Miss Prudence Starch"


def test_events_are_listed_one_per_line(data_path:Path) -> None:
    controller = GameController(data_path, debug=True)
    lines = texts(controller.handle("kerl", "!events")).splitlines()
    assert lines[0] == "Events:"
    assert len(lines) == len(SPAWN_RULES) + 1


def test_no_event_runs_on_the_round_timer(data_path:Path) -> None:
    for rule in SPAWN_RULES:
        controller = GameController(data_path, debug=True)
        start_run(controller)
        controller.handle("kerl", f"!trigger {rule.kind}")
        session = controller.session
        if session.state != "event":
            continue
        assert session.deadline > 1000, rule.kind
        assert session.tick(60.0) == [], rule.kind


def test_cities_and_teleport_are_debug_only(data_path:Path) -> None:
    plain = GameController(data_path)
    assert plain.handle("kerl", "!cities") == []
    assert plain.handle("kerl", "!teleport ironhold") == []
    from cursed_descent.towns import town_key
    controller = GameController(data_path, debug=True)
    listing = texts(controller.handle("kerl", "!cities"))
    assert "ironhold" in listing and "you are here" in listing
    assert "Usage" in texts(controller.handle("kerl", "!teleport"))
    reply = texts(controller.handle("kerl", "!teleport Mudgate"))
    assert "Teleported to Mudgate" in reply
    kerl = controller.repository.load("kerl")
    assert town_key(kerl) == "mudgate"
    assert "Usage" in texts(controller.handle("kerl", "!teleport nowhere"))


def test_mage_tower_is_listed_and_can_be_triggered(data_path:Path) -> None:
    controller = GameController(data_path, debug=True)
    assert "mage_tower" in texts(controller.handle("kerl", "!events"))
    start_run(controller)
    controller.handle("kerl", "!trigger mage_tower")
    assert controller.session.events.event["kind"] == "mage_tower"


def test_enemies_lists_every_enemy(data_path:Path) -> None:
    from cursed_descent.content import ENEMIES
    controller = GameController(data_path, debug=True)
    output = texts(controller.handle("kerl", "!enemies"))
    assert all(key in output for key in ENEMIES)
    assert controller.handle("kerl", "!enemies") != []


def test_enemies_and_spawn_are_ignored_without_debug(
        controller:GameController) -> None:
    assert controller.handle("kerl", "!enemies") == []
    assert controller.handle("kerl", "!spawn mimic") == []


def test_spawn_needs_a_run_and_a_known_enemy(data_path:Path) -> None:
    controller = GameController(data_path, debug=True)
    assert "Start a run" in texts(controller.handle("kerl", "!spawn mimic"))
    start_run(controller)
    assert "Usage" in texts(controller.handle("kerl", "!spawn nothing"))


def test_spawn_starts_a_fight_with_any_enemy(data_path:Path) -> None:
    from cursed_descent.content import ENEMIES
    for key, template in ENEMIES.items():
        controller = GameController(data_path, debug=True)
        start_run(controller)
        controller.handle("kerl", f"!spawn {key}")
        assert controller.session.state == "combat", key
        assert controller.session.enemies[0].name == template["name"], key
        assert controller.session.bonus_fight == "spawn", key


def test_a_spawned_fight_can_be_won(data_path:Path) -> None:
    controller = GameController(data_path, debug=True)
    start_run(controller)
    controller.handle("kerl", "!spawn rat")
    session = controller.session
    session.enemies[0].hp = 0
    reply = "\n".join(session.clear_bonus(5.0))
    assert "Debug fight won" in reply and session.bonus_fight == ""


def test_enemies_are_sorted_and_point_to_the_events(
        data_path:Path) -> None:
    controller = GameController(data_path, debug=True)
    lines = texts(controller.handle("kerl", "!enemies")).splitlines()
    keys = [line.split(":")[0].strip() for line in lines[1:-1]]
    assert keys == sorted(keys)
    assert "[events]" in lines[-1]


def test_stage_jumps_to_any_stage(data_path:Path) -> None:
    controller = GameController(data_path, debug=True)
    assert "Start a run" in texts(controller.handle("kerl", "!stage 20"))
    start_run(controller)
    assert "Usage" in texts(controller.handle("kerl", "!stage"))
    assert "Usage" in texts(controller.handle("kerl", "!stage x"))
    reply = texts(controller.handle("kerl", "!stage 47"))
    assert "stage 47" in reply and controller.session.stage == 47
    assert controller.session.state == "combat"


def test_stage_is_ignored_without_debug(
        controller:GameController) -> None:
    assert controller.handle("kerl", "!stage 5") == []


def test_biome_commands_are_ignored_without_debug(
        controller:GameController) -> None:
    assert controller.handle("kerl", "!biomes") == []
    assert controller.handle("kerl", "!nextbiome") == []


def test_biomes_lists_every_biome_and_marks_the_current_one(
        data_path:Path) -> None:
    from cursed_descent.content import BIOMES
    controller = GameController(data_path, debug=True)
    output = texts(controller.handle("kerl", "!biomes"))
    assert all(biome["name"] in output for biome in BIOMES)
    assert "you are here" not in output
    start_run(controller)
    assert "you are here" in texts(controller.handle("kerl", "!biomes"))


def test_nextbiome_needs_a_run(data_path:Path) -> None:
    controller = GameController(data_path, debug=True)
    assert "Start a run" in texts(controller.handle("kerl", "!nextbiome"))


def test_nextbiome_jumps_to_a_different_biome(data_path:Path) -> None:
    from cursed_descent.dungeon import current_biome, is_biome_start
    controller = GameController(data_path, debug=True)
    start_run(controller)
    session = controller.session
    before = current_biome(session.stage, session.run_id,
                           session.lobby_town)["name"]
    controller.handle("kerl", "!nextbiome")
    after = current_biome(session.stage, session.run_id,
                          session.lobby_town)["name"]
    assert after != before and is_biome_start(session.stage)


def test_nextbiome_with_a_name_finds_the_vine_swamp(
        data_path:Path) -> None:
    controller = GameController(data_path, debug=True)
    start_run(controller)
    reply = texts(controller.handle("kerl", "!nextbiome vine swamp"))
    assert "Vine Swamp" in reply and controller.session.stage >= 16
    assert "Unknown biome" in texts(controller.handle(
        "kerl", "!nextbiome nowhere"))



def test_item_commands_are_ignored_without_debug(
        controller:GameController) -> None:
    assert controller.handle("kerl", "!itemlist") == []
    assert controller.handle("kerl", "!giveitem wool_rug") == []


def test_itemlist_filters_and_pages(data_path:Path) -> None:
    controller = GameController(data_path, debug=True)
    output = texts(controller.handle("kerl", "!itemlist furniture"))
    assert "wool_rug: Wool Rug" in output and "page 1/1" in output
    assert "page 2/" in texts(controller.handle("kerl", "!itemlist 2"))
    assert "No items match" in texts(
        controller.handle("kerl", "!itemlist qqqq"))


def test_giveitem_by_id_or_name(data_path:Path) -> None:
    controller = GameController(data_path, debug=True)
    player = controller.repository.load("kerl")
    player.inventory = []
    controller.repository.save(player)
    controller.handle("kerl", "!giveitem wool_rug")
    controller.handle("kerl", "!giveitem Oak Table")
    inventory = controller.repository.load("kerl").inventory
    assert "wool_rug" in inventory and "oak_table" in inventory
    assert "No single item" in texts(
        controller.handle("kerl", "!giveitem nonsense"))

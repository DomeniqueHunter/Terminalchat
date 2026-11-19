from pathlib import Path

from cursed_descent.commands import parse_chat
from cursed_descent.web import audience
from cursed_descent.web.hub import GameHub


def put(hub:GameHub, name:str, where:str, gold:int=None,
        town:str="") -> None:
    player = hub.controller.repository.load(name)
    player.profile["where"] = where
    if town:
        player.profile["town"] = town
    if gold is not None:
        player.gold = gold
    hub.controller.repository.save(player)


def run(hub:GameHub, name:str, line:str) -> list:
    return hub.controller.execute(name, parse_chat(f"!{line}"))


def witness_of(messages:list) -> str:
    return next((m.witness for m in messages if m.witness), "")


def test_tavern_room_is_seen_by_the_bar(data_path:Path) -> None:
    hub = GameHub(data_path)
    put(hub, "kerl", "tavern", 500)
    put(hub, "galactica", "tavern")
    text = witness_of(run(hub, "kerl", "room common"))
    assert "You see {actor}" in text or "You see" in text
    assert "stairs" in text


def test_clinic_mod_is_seen_in_the_clinic(data_path:Path) -> None:
    from cursed_descent.locations.clinic.location import clinic_options
    hub = GameHub(data_path)
    put(hub, "kerl", "clinic", 100000)
    command = clinic_options(hub.controller.repository.load("kerl"))[0][0]
    assert "nurses" in witness_of(run(hub, "kerl", f"mod {command}"))


def test_smith_purchase_is_seen_at_the_forge(data_path:Path) -> None:
    hub = GameHub(data_path)
    put(hub, "kerl", "smith", 100000)
    player = hub.controller.repository.load("kerl")
    player.inventory = []
    hub.controller.repository.save(player)
    texts = {witness_of(run(hub, "kerl", f"forge {number}"))
             for number in range(1, 6)}
    assert any("steel" in text for text in texts)


def test_arrival_at_the_station_is_seen(data_path:Path) -> None:
    hub = GameHub(data_path)
    put(hub, "kerl", "station", 100000)
    player = hub.controller.repository.load("kerl")
    player.profile["rail_pass"] = ["ironhold"]
    hub.controller.repository.save(player)
    assert "train" in witness_of(run(hub, "kerl", "travel ironhold"))


def test_a_finished_mine_shift_is_seen(data_path:Path) -> None:
    hub = GameHub(data_path)
    put(hub, "kerl", "mine_guild", 0, "ironhold")
    run(hub, "kerl", "mine_guild 1")
    now = 0.0
    seen = []
    for _ in range(12):
        now += 10000
        seen += [m.witness for m in hub.controller.tick(now) if m.witness]
    assert any("shaft" in text for text in seen)


def test_poor_visitors_leave_no_scene(data_path:Path) -> None:
    hub = GameHub(data_path)
    put(hub, "kerl", "tavern", 0)
    assert witness_of(run(hub, "kerl", "room common")) == ""


def test_arena_bet_has_two_outcomes(data_path:Path) -> None:
    hub = GameHub(data_path)
    put(hub, "kerl", "arena", 100000, "mudgate")
    seen = {witness_of(run(hub, "kerl", "arena 1")) for _ in range(40)}
    assert any("wins" in text for text in seen)
    assert any("goes down" in text for text in seen)


def test_the_audience_reaches_the_same_building(data_path:Path) -> None:
    hub = GameHub(data_path)
    put(hub, "kerl", "arena", 100000, "mudgate")
    put(hub, "galactica", "arena", None, "mudgate")
    messages = run(hub, "kerl", "arena 1")
    entry = audience.witnesses(hub.controller, "kerl", messages[0])
    assert entry is not None and "Galactica" in entry[0]


def test_every_scene_text_names_the_actor() -> None:
    from cursed_descent.town_buildings import observers
    texts = [*observers.COUNTER_SCENES.values(),
             *observers.BANK_SCENES.values(),
             *observers.SHIFT_DONE.values(),
             *(text for _, text in observers.PAID_SCENES.values())]
    assert all("{actor}" in text for text in texts)


def test_blood_bank_and_castle_scenes(data_path:Path) -> None:
    hub = GameHub(data_path)
    put(hub, "kerl", "blood_bank", 100, "dusk_hollow")
    from cursed_descent.formulas import max_hp
    player = hub.controller.repository.load("kerl")
    player.hp = max_hp(player)
    hub.controller.repository.save(player)
    assert "sleeve" in witness_of(run(hub, "kerl", "blood_bank 1"))
    put(hub, "kerl", "castle", 100, "dusk_hollow")
    assert witness_of(run(hub, "kerl", "castle 2")) == ""
    player = hub.controller.repository.load("kerl")
    player.profile["castle_invite"] = True
    hub.controller.repository.save(player)
    assert "banquet" in witness_of(run(hub, "kerl", "castle 2"))


def test_bank_deposit_is_seen(data_path:Path) -> None:
    hub = GameHub(data_path)
    put(hub, "kerl", "bank", 500)
    assert "purse" in witness_of(run(hub, "kerl", "deposit gold 100"))

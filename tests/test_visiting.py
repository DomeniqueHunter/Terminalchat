import random

from cursed_descent import spawns
from cursed_descent.npcs.seed import default_npcs
from cursed_descent.npcs.visiting import (
    FEMININE, VisitBoard, npc_record, profiles, quirk_line, roles_of,
)
from cursed_descent.towns.last_light_humans.cafe.guests import new_guest
from cursed_descent.town_buildings.brothel.clients import new_client
from cursed_descent.towns import TOWNS


def text(messages) -> str:
    return "\n".join(message.text for message in messages)


def npcs_by_key() -> dict:
    return {npc.npc: npc for npc in default_npcs()}


class Store:
    def __init__(self, records:list[dict]) -> None:
        self.records = records

    def visiting(self, building:str) -> list[dict]:
        return self.records

    def pick(self, building:str, rng) -> None:
        return None

    def visit(self, building:str, record:dict) -> dict:
        return record


def test_every_profile_belongs_to_an_existing_npc() -> None:
    known = npcs_by_key()
    assert len(profiles()) == 15
    for key in profiles():
        assert key in known, key


def test_cafe_roles_are_only_for_ladies_and_reginald_has_none() -> None:
    known = npcs_by_key()
    assert roles_of(profiles()["reginald"], "Male") == [("brothel", 1)]
    assert [name for name, _ in roles_of(profiles()["jorveig"],
                                         known["jorveig"].gender)
            ] == ["cafe", "brothel"]
    for key, profile in profiles().items():
        gender = known[key].gender
        cafe = [name for name, _ in roles_of(profile, gender)
                if name == "cafe"]
        assert not cafe or gender in FEMININE, key


def test_visits_start_randomly_block_spawns_and_end() -> None:
    board = VisitBoard(random.Random(3))
    genders = {key: npc.gender for key, npc in npcs_by_key().items()
               if key in profiles()}
    now = 0.0
    for _ in range(400):
        now += 60
        board.tick(now, tuple(TOWNS), set(), genders)
        if board.visits:
            break
    assert board.visits
    visit = next(iter(board.visits.values()))
    assert visit.town in TOWNS and visit.building in ("cafe", "brothel")
    assert board.away_kinds() >= set(profiles()[visit.npc].kinds)
    board.tick(visit.until + 1, tuple(TOWNS), set(), {})
    assert visit.npc not in board.visits


def test_a_busy_location_keeps_its_keeper_at_home() -> None:
    board = VisitBoard(random.Random(1))
    genders = {key: npc.gender for key, npc in npcs_by_key().items()
               if key in profiles()}
    busy = {kind for profile in profiles().values()
            for kind in profile.kinds}
    now = 0.0
    for _ in range(300):
        now += 60
        board.tick(now, tuple(TOWNS), busy, genders)
    assert all(not profiles()[key].kinds for key in board.visits)


def test_away_kinds_are_removed_from_the_spawn_pool() -> None:
    try:
        spawns.AWAY_KINDS.add("brewery")
        kinds = {rule.kind for rule in spawns.eligible(60, "location")}
        assert "brewery" not in kinds
    finally:
        spawns.AWAY_KINDS.clear()
    assert "brewery" in {rule.kind
                         for rule in spawns.eligible(60, "location")}


def test_jorveig_sits_on_the_seat_with_her_unmistakable_feet() -> None:
    known = npcs_by_key()
    record = npc_record(known["jorveig"], profiles()["jorveig"])
    rng = random.Random(1)
    guest = new_guest(rng, Store([record]))
    for _ in range(20):
        if guest.npc == "jorveig":
            break
        guest = new_guest(rng, Store([record]))
    assert guest.npc == "jorveig" and guest.name == "Jorveig Brandsson"
    lines = {quirk_line("jorveig", "cafe_round", rng) for _ in range(40)}
    assert any("foot" in line or "feet" in line for line in lines)
    assert "feet" in quirk_line("jorveig", "cafe_arrive", rng)


def test_reginald_comes_as_a_dominant_client_never_as_a_seat() -> None:
    from cursed_descent.models import Player
    known = npcs_by_key()
    record = npc_record(known["reginald"], profiles()["reginald"])
    assert record["dominant"] and not record["dominated"]
    player = Player(name="Worker", gender="Female")
    rng = random.Random(5)
    found = None
    for _ in range(60):
        client = new_client(player, rng, Store([record]), "sub")
        if client.npc == "reginald":
            found = client
            break
    assert found is not None and found.dominant
    assert profiles()["reginald"].likes == (("brothel", 1),)


def test_visitors_show_up_in_meet_and_chat(controller) -> None:
    from cursed_descent.towns import START_TOWN
    controller.town.visits_on = True
    controller.town.visits.visits["jorveig"] = __import__(
        "cursed_descent.npcs.visiting", fromlist=["Visit"]).Visit(
        "jorveig", START_TOWN, "cafe", 10 ** 9)
    reply = text(controller.handle("Kerl", "!meet"))
    assert "Jorveig" in reply and "visiting the cafe" in reply
    assert "Jorveig" in text(controller.handle("Kerl", "!meet jorveig"))
    assert "Nobody" not in text(controller.handle("Kerl", "!chat jorveig"))


def test_the_adept_is_a_named_adult_boy() -> None:
    pip = npcs_by_key()["adept_pip"]
    assert pip.full_name == "Pip Primrose" and pip.gender == "Male"
    assert pip.age >= 18


def test_story_regular_is_a_reference_to_the_real_npc(tmp_path) -> None:
    import json
    from cursed_descent.town_buildings.regulars import Regulars
    jorveig = npc_record(npcs_by_key()["jorveig"], profiles()["jorveig"])
    store = Regulars(tmp_path, "town", "kerl")
    real = {"record": jorveig}
    ref = jorveig["id"]
    store.resolver = lambda wanted: real["record"] if wanted == ref else None
    store.visit("cafe", jorveig)
    again = store.visit("cafe", jorveig)
    path = store.folder("cafe") / "jorveig_brandsson.json"
    raw = json.loads(path.read_text())
    assert raw == {"type": "story_npc", "ref_id": ref, "visits": 2}
    assert again["weight"] == jorveig["weight"]
    real["record"] = dict(jorveig, weight=111)
    assert store.get("cafe", jorveig["name"])["weight"] == 111
    store.fill("cafe", jorveig["name"], {"weight": 5, "belly": 2})
    store.set("cafe", jorveig["name"], {"butt": 1})
    raw = json.loads(path.read_text())
    assert "weight" not in raw and "butt" not in raw and raw["belly"] == 2
    assert store.pool("cafe") == []
    real["record"] = None
    assert store.all("cafe") == []


def test_visitor_kills_count_per_regular_and_in_total(tmp_path) -> None:
    from cursed_descent.towns.last_light_humans.cafe.seat import record_kill
    from cursed_descent.town_buildings.regulars import Regulars
    jorveig = npc_record(npcs_by_key()["jorveig"], profiles()["jorveig"])
    totals = {"jorveig": 0}
    store = Regulars(tmp_path, "town", "kerl")
    store.resolver = lambda ref: jorveig
    store.credit = lambda ref: totals.update({ref: totals[ref] + 1})
    stored = store.visit("cafe", jorveig)
    guest = new_guest(random.Random(1), Store([jorveig]))
    guest.npc, guest.name, guest.kills = "jorveig", jorveig["name"], 0
    record_kill(guest, store)
    record_kill(guest, store)
    assert totals["jorveig"] == 2 and guest.kills == 2
    assert store.get("cafe", jorveig["name"])["kills"] == 2
    assert stored.get("kills", 0) == 0


def test_deadlydame_debug_command_forces_the_crush() -> None:
    from cursed_descent.towns.last_light_humans.cafe.guests import (
        DEADLY, crush_chance, deadly_toggle)
    try:
        assert crush_chance(100, 100, 0) == 0.0
        assert "ON" in deadly_toggle()
        assert crush_chance(100, 100, 0) == 1.0
    finally:
        DEADLY["on"] = False


def test_deadlydame_needs_debug_mode(data_path) -> None:
    from cursed_descent import GameController
    from cursed_descent.towns.last_light_humans.cafe.guests import DEADLY
    try:
        assert GameController(data_path).handle("kerl", "!deadlydame") == []
        reply = GameController(data_path, debug=True).handle(
            "kerl", "!deadlydame")
        assert "ON" in reply[0].text and DEADLY["on"]
    finally:
        DEADLY["on"] = False


def test_race_scent_and_skin_shape_lick_and_kiss(controller) -> None:
    from cursed_descent.races import RACES
    from cursed_descent.towns.last_light_humans.cafe.actions import skin_line
    from cursed_descent.towns.last_light_humans.cafe.guests import Guest
    goblin = Guest("Grisha", 90, 120, race="goblin")
    human = Guest("Mabel", 90, 120)
    assert RACES["goblin"].scent == (2, 2)
    assert "wet moss" in skin_line(goblin, True)
    assert "tangy" in skin_line(goblin, True)
    assert "stays on your lips" in skin_line(goblin, False)
    assert skin_line(human, True) == ""
    assert all(race.skin[0] and race.skin[1] for race in RACES.values())
    jorveig = npc_record(npcs_by_key()["jorveig"], profiles()["jorveig"])
    assert "race" in jorveig


def test_regular_happiness_moves_with_kisses_and_shows_in_the_list(
        tmp_path) -> None:
    from cursed_descent.config import HAPPY_DEFAULT, HAPPY_MAX
    from cursed_descent.town_buildings.regulars import Regulars
    from cursed_descent.town_buildings.services import mood_text
    store = Regulars(tmp_path, "town", "kerl")
    store.add("cafe", {"name": "Lady Mabel", "age": 40})
    assert store.mood("cafe", "Lady Mabel", 1) == HAPPY_DEFAULT + 1
    for _ in range(20):
        store.mood("cafe", "Lady Mabel", 1)
    assert store.get("cafe", "Lady Mabel")["happiness"] == HAPPY_MAX
    assert store.mood("cafe", "Nobody", 1) == HAPPY_DEFAULT
    assert "devoted" in mood_text({"happiness": HAPPY_MAX})
    assert "cold" in mood_text({"happiness": 0})

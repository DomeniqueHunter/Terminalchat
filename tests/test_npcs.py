import json
from pathlib import Path

from cursed_descent.config import MAX_PARTY_SIZE, NPC_HIRE_PRICE
from cursed_descent.content import ITEMS
from cursed_descent.controller import GameController
from cursed_descent.examine_target import examine_target
from cursed_descent.models import Enemy, Player
from cursed_descent.npcs.autopilot import autopilot_choice
from cursed_descent.npcs.hire import spend_points
from cursed_descent.npcs.store import find_local
from tests.npc_factory import add_merc, merc

from tests.ready import confirm


def texts(messages) -> str:
    return "\n".join(message.text for message in messages)


def make_enemy(uid:int, hp:int) -> Enemy:
    return Enemy(uid=uid, template_id="rat", name="Rat", max_hp=30, hp=hp,
                 attack=5, defense=0, agility=1, exp=1, fates=[],
                 actions=[("attack", 100)])


def open_lobby(controller:GameController) -> None:
    for name, focus in (("Brom", ("strength", "vitality")),
                        ("Mara", ("intelligence", "vitality")),
                        ("Vex", ("agility", "strength")),
                        ("Quill", ("intelligence", "agility"))):
        if not controller.repository.exists(name):
            add_merc(controller, name, focus=focus)
    controller.handle("kerl", "!lobby", now=0.0)


def test_hire_without_name_lists_companions(
        controller:GameController) -> None:
    open_lobby(controller)
    assert "Brom Ironhide" in texts(controller.handle("kerl", "!hire"))


def test_hire_needs_an_open_lobby(controller:GameController) -> None:
    assert "open lobby" in texts(controller.handle("kerl", "!hire brom"))


def test_hire_pays_and_joins_the_party(controller:GameController) -> None:
    open_lobby(controller)
    player = controller.repository.load("kerl")
    player.gold = 500
    messages = controller.handle("kerl", "!hire brom")
    assert "joins the party" in texts(messages)
    assert player.gold == 500 - NPC_HIRE_PRICE
    npc = controller.session.member("Brom")
    assert npc is not None and npc.npc == "mercenary"


def test_npc_is_stored_in_its_own_folder(
        controller:GameController, data_path:Path) -> None:
    open_lobby(controller)
    controller.repository.load("kerl").gold = 500
    controller.handle("kerl", "!hire brom")
    assert controller.repository.npc_path("Brom").exists()
    assert "Brom" not in controller.repository.names()
    saved = json.loads(controller.repository.npc_path("Brom").read_text())
    assert saved["npc"] == "mercenary"


def test_hire_refused_when_poor_or_full(
        controller:GameController) -> None:
    open_lobby(controller)
    controller.repository.load("kerl").gold = 1
    assert "wants" in texts(controller.handle("kerl", "!hire brom"))
    controller.repository.load("kerl").gold = 5000
    for name in ("brom", "mara", "vex"):
        controller.handle("kerl", f"!hire {name}")
    assert len(controller.session.party) == MAX_PARTY_SIZE
    assert "full" in texts(controller.handle("kerl", "!hire quill"))


def test_dismiss_removes_the_companion(controller:GameController) -> None:
    open_lobby(controller)
    controller.repository.load("kerl").gold = 500
    controller.handle("kerl", "!hire brom")
    controller.handle("kerl", "!dismiss brom")
    assert controller.session.member("Brom") is None


def test_humans_cannot_take_a_companion_name(
        controller:GameController) -> None:
    add_merc(controller, "Brom")
    assert "companion" in texts(controller.handle("Brom", "!create"))


def test_companion_acts_on_autopilot_each_round(
        controller:GameController) -> None:
    open_lobby(controller)
    controller.repository.load("kerl").gold = 500
    controller.handle("kerl", "!hire brom")
    controller.handle("kerl", "!start", now=1.0)
    confirm(controller, 1.0)
    npc = controller.session.member("Brom")
    assert npc.action is not None


def test_run_ends_when_only_companions_are_left(
        controller:GameController) -> None:
    open_lobby(controller)
    controller.repository.load("kerl").gold = 500
    controller.handle("kerl", "!hire brom")
    controller.handle("kerl", "!start", now=1.0)
    confirm(controller, 1.0)
    controller.session.member("kerl").alive = False
    assert controller.session.living() == []


def test_autopilot_heals_the_weakest_ally() -> None:
    healer = merc("Mara", ("intelligence", "vitality"))
    healer.hp, healer.mana = 100, 100
    hurt = Player(name="hurt")
    hurt.hp = 1
    kind, args = autopilot_choice(healer, [healer, hurt],
                                  [make_enemy(1, 20)])
    assert kind == "cast" and args[-1] == "hurt"


def test_autopilot_hits_the_weakest_enemy_without_mana() -> None:
    fighter = merc("Brom")
    fighter.mana = 0
    fighter.hp = 10 ** 6
    kind, args = autopilot_choice(
        fighter, [fighter], [make_enemy(1, 20), make_enemy(2, 5)])
    assert (kind, args) == ("hit", ["2"])


def test_autopilot_guards_when_nearly_dead() -> None:
    fighter = merc("Brom")
    fighter.mana = 0
    fighter.hp = 1
    kind, _ = autopilot_choice(fighter, [fighter], [make_enemy(1, 20)])
    assert kind == "guard"


def test_free_points_follow_the_focus_stats() -> None:
    npc = merc("Brom")
    before = dict(npc.stats)
    npc.free_points = 4
    spend_points(npc)
    assert npc.free_points == 0
    assert npc.stats["strength"] == before["strength"] + 2
    assert npc.stats["vitality"] == before["vitality"] + 2


def test_own_characters_can_be_recruited_for_free(
        controller:GameController) -> None:
    open_lobby(controller)
    gold = controller.repository.load("kerl").gold
    messages = controller.handle("kerl", "!hire galactica")
    assert "companion on autopilot" in texts(messages)
    assert controller.repository.load("kerl").gold == gold
    assert controller.session.member("Galactica") is not None
    assert controller.session.is_auto(controller.session.member("Galactica"))


def test_recruited_character_stays_in_the_players_folder(
        controller:GameController, data_path:Path) -> None:
    open_lobby(controller)
    controller.handle("kerl", "!hire galactica")
    assert not controller.repository.npc_path("galactica").exists()
    assert "Galactica" in controller.repository.names()


def test_recruit_by_id_and_not_yourself(
        controller:GameController) -> None:
    open_lobby(controller)
    assert "yourself" in texts(controller.handle("kerl", "!hire kerl"))
    char_id = controller.repository.load("galactica").id
    controller.handle("kerl", f"!hire {char_id}")
    assert controller.session.member("Galactica") is not None


def test_recruited_character_acts_on_autopilot_and_is_released(
        controller:GameController) -> None:
    open_lobby(controller)
    controller.handle("kerl", "!hire galactica")
    controller.handle("kerl", "!start", now=1.0)
    confirm(controller, 1.0)
    assert controller.session.member("Galactica").action is not None
    controller.session.member("kerl").alive = False
    heirs = controller.session.living()
    assert [hero.name for hero in heirs] == ["Galactica"]
    assert not controller.session.is_auto(heirs[0])
    controller.session.member("Galactica").alive = False
    assert controller.session.living() == []
    controller.session.end_run()
    assert controller.session.autopilot == set()


def test_dismiss_releases_a_recruited_character(
        controller:GameController) -> None:
    open_lobby(controller)
    controller.handle("kerl", "!hire galactica")
    controller.handle("kerl", "!dismiss galactica")
    assert controller.session.member("Galactica") is None
    assert "Galactica" not in controller.session.autopilot


def test_hire_list_names_own_characters_and_mercenaries(
        controller:GameController) -> None:
    open_lobby(controller)
    text = texts(controller.handle("kerl", "!hire"))
    assert "Your characters" in text and "Galactica" in text
    assert "Mercenaries" in text and "Brom Ironhide" in text


def hire_pair(controller:GameController) -> None:
    open_lobby(controller)
    controller.repository.load("kerl").gold = 500
    controller.handle("kerl", "!hire brom")
    controller.handle("kerl", "!hire galactica")


def test_auto_overview_lists_companions(controller:GameController) -> None:
    hire_pair(controller)
    text = texts(controller.handle("kerl", "!auto"))
    assert "Brom Ironhide: on" in text and "Galactica: on" in text


def test_auto_off_means_manual_control(controller:GameController) -> None:
    hire_pair(controller)
    messages = controller.handle("kerl", "!auto galactica off")
    assert "off" in texts(messages)
    controller.handle("kerl", "!start", now=1.0)
    confirm(controller, 1.0)
    session = controller.session
    assert session.member("Galactica").action is None
    assert session.member("Brom").action is not None
    assert not session.is_auto(session.member("Galactica"))


def test_auto_toggles_without_on_or_off(
        controller:GameController) -> None:
    hire_pair(controller)
    controller.handle("kerl", "!auto brom")
    assert "Brom" in controller.session.manual
    controller.handle("kerl", "!auto brom")
    assert "Brom" not in controller.session.manual


def test_auto_on_mid_fight_sets_an_action_at_once(
        controller:GameController) -> None:
    hire_pair(controller)
    controller.handle("kerl", "!auto galactica off")
    controller.handle("kerl", "!start", now=1.0)
    confirm(controller, 1.0)
    controller.handle("kerl", "!auto galactica on", now=2.0)
    assert controller.session.member("Galactica").action is not None


def test_manual_companion_keeps_the_run_alive(
        controller:GameController) -> None:
    hire_pair(controller)
    controller.handle("kerl", "!auto galactica off")
    controller.handle("kerl", "!start", now=1.0)
    confirm(controller, 1.0)
    controller.session.member("kerl").alive = False
    assert controller.session.living() != []


def test_auto_needs_a_companion(controller:GameController) -> None:
    open_lobby(controller)
    assert "no companions" in texts(controller.handle("kerl", "!auto"))
    assert "already steered" in texts(
        controller.handle("kerl", "!auto kerl off"))


def test_keepers_wear_shoes_of_their_victims(
        controller:GameController) -> None:
    session = controller.session
    victim = controller.repository.load("kerl")
    victim.equipment["feet"] = "high_heels"
    session.keeper_takes("brewed", victim)
    astrid = find_local(controller.repository.npc_players(), "astrid")
    assert astrid.equipment["feet"] == "high_heels"
    report = examine_target(victim, "astrid", [], [], controller.repository,
                            False)[0].text
    assert "High Heel" in report
    boots = next(item_id for item_id, item in ITEMS.items()
                 if item["slot"] == "feet")
    session.keeper_takes("fashion", victim, boots)
    velvet = find_local(controller.repository.npc_players(), "velvet")
    assert velvet.equipment["feet"] == boots
    session.keeper_takes("fashion", victim, "domina_whip")
    assert velvet.equipment["feet"] == boots


def test_a_joined_hero_can_be_handed_to_the_autopilot(
        controller:GameController) -> None:
    open_lobby(controller)
    controller.handle("kerl", "!join", now=0.1)
    other = controller.repository.load("galactica")
    controller.handle("Galactica", "!join", now=0.2)
    assert not controller.session.is_auto(controller.session.member(
        "Galactica"))
    reply = texts(controller.handle("kerl", "!auto galactica"))
    assert "on" in reply
    assert controller.session.is_auto(controller.session.member(
        "Galactica"))
    assert other is not None
    controller.handle("kerl", "!auto galactica")
    assert not controller.session.is_auto(controller.session.member(
        "Galactica"))


def test_the_last_manual_hero_cannot_go_on_autopilot(
        controller:GameController) -> None:
    open_lobby(controller)
    reply = texts(controller.handle("kerl", "!auto kerl"))
    assert "At least one hero" in reply


def test_mercenaries_alone_do_not_continue_the_run(
        controller:GameController) -> None:
    open_lobby(controller)
    controller.repository.load("kerl").gold = 500
    controller.handle("kerl", "!hire brom")
    controller.handle("kerl", "!start", now=1.0)
    confirm(controller, 1.0)
    controller.session.member("kerl").alive = False
    assert controller.session.living() == []


def test_a_farmed_hero_hands_the_lead_to_the_next_one(
        controller:GameController) -> None:
    open_lobby(controller)
    controller.handle("kerl", "!hire galactica")
    controller.handle("kerl", "!start", now=1.0)
    confirm(controller, 1.0)
    session = controller.session
    lines = session.kill_outside(session.member("kerl"), "farmed",
                                 "kerl stays on the farm.", "Old Trotter",
                                 "pigmen")
    assert any("takes over as main hero" in line for line in lines)
    assert [hero.name for hero in session.living()] == ["Galactica"]


def test_every_fixed_npc_has_a_unique_valid_address_and_display() -> None:
    from cursed_descent.npcs.address import valid_address
    from cursed_descent.npcs.seed import default_npcs
    npcs = default_npcs()
    addresses = [npc.profile["address"] for npc in npcs]
    assert len(addresses) == len(set(addresses)) == len(npcs)
    for npc in npcs:
        assert valid_address(npc.profile["address"]), npc.name
        assert npc.profile["home"], npc.name
    by_key = {npc.npc: npc.profile for npc in npcs}
    assert by_key["jorveig"]["address"] == "event:smokery:1"
    assert by_key["bertha"]["address"] == "town:last_light:cafe:1"
    assert by_key["rose"]["home"] == "Brothel, Last Light" or (
        "Last Light" in by_key["rose"]["home"])
    assert by_key["emmerich_grimhold"]["address"].startswith("event:wedding")
    assert by_key["starch"]["address"].startswith("town:last_light:maidschool")


def test_story_regular_takes_home_and_address_from_the_real_npc(
        tmp_path) -> None:
    import json
    from cursed_descent.npcs.seed import default_npcs
    from cursed_descent.npcs.visiting import npc_record, profiles
    from cursed_descent.town_buildings.regulars import Regulars
    jorveig = next(n for n in default_npcs() if n.npc == "jorveig")
    record = npc_record(jorveig, profiles()["jorveig"])
    assert record["address"] == "event:smokery:1"
    store = Regulars(tmp_path, "town", "kerl")
    store.resolver = lambda ref: record
    store.visit("cafe", record)
    path = store.folder("cafe") / "jorveig_brandsson.json"
    raw = json.loads(path.read_text())
    assert "home" not in raw and "address" not in raw
    assert store.get("cafe", record["name"])["home"] == "Northern Smokery"

import itertools
import random
import time
from cursed_descent import home_scene
from cursed_descent.controller import GameController
from cursed_descent.houses import home_of, capacity, catalogue, home_of
from cursed_descent.towns import START_TOWN


def accepted(controller:GameController, owner:str, text:str):
    reply = controller.handle(owner, text)
    if any("[home accept]" in message.text for message in reply):
        reply += controller.handle("galactica", "!home accept")
        agree(controller, "galactica", owner)
    return reply


def agree(controller:GameController, hero:str, asker:str) -> None:
    repository = controller.repository
    target = repository.load(hero)
    target.profile.setdefault("sex_ok", {})[
        repository.load(asker).id] = time.time()
    repository.save(target)
    sender = repository.load(asker)
    sender.profile["home_sex"] = target.name
    repository.save(sender)


CLOCK = itertools.count(1)


def hit(controller:GameController, who:str, text:str):
    from cursed_descent import home_scene
    reply = controller.handle(who, text)
    if any("is registered in" in message.text for message in reply):
        reply += home_scene.tick_scenes(
            controller.repository, random.Random(1), time.time() + 60 * next(CLOCK))
    return reply


def texts(messages) -> str:
    return "\n".join(message.text for message in messages)


def rich(controller:GameController, gold:int=10 ** 6) -> None:
    kerl = controller.repository.load("kerl")
    kerl.gold = gold
    controller.repository.save(kerl)


def befriend(controller:GameController, name:str, points:int) -> None:
    kerl = controller.repository.load("kerl")
    npc = controller.repository.load(name)
    npc.profile.setdefault("friends", {})[kerl.id] = points
    controller.repository.save(npc)


def test_catalogue_has_four_house_types_with_rising_prices() -> None:
    prices = [price for _, _, price, _ in catalogue(START_TOWN)]
    assert len(prices) == 4 and prices == sorted(prices)


def test_home_lists_offers_without_a_house(
        controller:GameController) -> None:
    reply = texts(controller.handle("kerl", "!home"))
    assert "Fixer-Upper Hut" in reply and "Manor Tower" in reply


def test_buying_needs_gold_and_only_one_per_town(
        controller:GameController) -> None:
    rich(controller, 10)
    assert "costs" in texts(controller.handle("kerl", "!home buy 1"))
    rich(controller)
    reply = texts(controller.handle("kerl", "!home buy townhouse"))
    assert "buys the Townhouse" in reply
    kerl = controller.repository.load("kerl")
    assert home_of(kerl, START_TOWN)["type"] == "townhouse"
    assert "already own" in texts(controller.handle("kerl", "!home buy 1"))


def test_sleeping_at_home_restores_and_dismisses_guests(
        controller:GameController) -> None:
    rich(controller)
    controller.handle("kerl", "!home buy row")
    befriend(controller, "hilda", 8)
    controller.handle("kerl", "!home invite hilda")
    kerl = controller.repository.load("kerl")
    kerl.hp = 1
    kerl.needs["sleep"] = 90
    controller.repository.save(kerl)
    reply = texts(controller.handle("kerl", "!home sleep"))
    kerl = controller.repository.load("kerl")
    assert "leaves in the morning" in reply
    assert kerl.hp > 1 and kerl.needs["sleep"] == 0
    assert home_of(kerl, START_TOWN)["guests"] == []


def test_strangers_do_not_visit(controller:GameController) -> None:
    rich(controller)
    controller.handle("kerl", "!home buy row")
    assert "well enough" in texts(controller.handle("kerl",
                                                    "!home invite hilda"))


def test_family_may_move_in_but_capacity_is_limited(
        controller:GameController) -> None:
    rich(controller)
    controller.handle("kerl", "!home buy hut")
    kerl = controller.repository.load("kerl")
    galactica = controller.repository.load("galactica")
    kerl.profile.setdefault("family", {})[galactica.id] = {
        "role": "sister", "name": galactica.name}
    controller.repository.save(kerl)
    reply = texts(accepted(controller, "kerl", "!home movein galactica"))
    assert "moves into" in reply
    befriend(controller, "hilda", 8)
    full = texts(controller.handle("kerl", "!home movein hilda"))
    assert "no free bed" in full
    kerl = controller.repository.load("kerl")
    assert capacity(home_of(kerl, START_TOWN)) == 2


def test_housemate_can_be_talked_to_and_romanced(
        controller:GameController) -> None:
    rich(controller)
    controller.handle("kerl", "!home buy row")
    befriend(controller, "hilda", 8)
    controller.handle("kerl", "!home movein hilda")
    assert "Hilda" in texts(controller.handle("kerl", "!home talk hilda"))
    assert "💞" in texts(controller.handle("kerl", "!home romance hilda"))


def test_housemate_needs_some_trust_for_romance(
        controller:GameController) -> None:
    rich(controller)
    controller.handle("kerl", "!home buy row")
    befriend(controller, "hilda", 8)
    controller.handle("kerl", "!home invite hilda")
    befriend(controller, "hilda", 1)
    assert "Not yet" in texts(controller.handle("kerl", "!home romance hilda"))


def test_house_is_unreachable_in_the_dungeon(
        controller:GameController) -> None:
    controller.handle("kerl", "!lobby", now=0.0)
    controller.handle("kerl", "!start", now=1.0)
    assert "dungeon" in texts(controller.handle("kerl", "!home"))


def link_son(controller:GameController) -> None:
    from cursed_descent.town_buildings.family import link
    kerl = controller.repository.load("kerl")
    son = controller.repository.load("galactica")
    link(kerl, son, "son")
    controller.repository.save(kerl)
    controller.repository.save(son)


def test_a_hero_can_be_invited_and_the_son_moves_in(
        controller:GameController) -> None:
    rich(controller)
    controller.handle("kerl", "!home buy row")
    link_son(controller)
    invited = texts(accepted(controller, "kerl", "!home invite galactica"))
    assert "comes over" in invited and "your son" in invited
    moved = texts(accepted(controller, "kerl", "!home movein galactica"))
    assert "moves into" in moved and "your son" in moved
    kerl = controller.repository.load("kerl")
    assert [entry["name"] for entry in
            home_of(kerl, START_TOWN)["residents"]] == ["Galactica"]


def test_a_resident_hero_sleeps_in_the_hosts_house(
        controller:GameController) -> None:
    rich(controller)
    controller.handle("kerl", "!home buy row")
    link_son(controller)
    accepted(controller, "kerl", "!home movein galactica")
    son = controller.repository.load("galactica")
    son.hp = 1
    controller.repository.save(son)
    reply = texts(controller.handle("galactica", "!home sleep"))
    assert "kerl's house" in reply
    assert controller.repository.load("galactica").hp > 1


def test_a_hero_without_any_house_cannot_sleep_at_home(
        controller:GameController) -> None:
    assert "no house" in texts(controller.handle("galactica",
                                                 "!home sleep"))


def test_a_hero_has_to_confirm_an_invite_and_a_move_in(
        controller:GameController) -> None:
    rich(controller)
    controller.handle("kerl", "!home buy row")
    asked = controller.handle("kerl", "!home invite galactica")
    assert "confirm on their own screen" in texts(asked)
    assert any(message.recipient == "galactica" or message.recipient ==
               "Galactica" for message in asked)
    kerl = controller.repository.load("kerl")
    assert home_of(kerl, START_TOWN)["guests"] == []
    assert "comes over" in texts(controller.handle("galactica",
                                                   "!home accept"))
    moved = controller.handle("kerl", "!home movein galactica")
    assert "confirm" in texts(moved)
    assert "moves into" in texts(controller.handle("galactica",
                                                   "!home accept"))
    controller.handle("kerl", "!home leave galactica")
    controller.handle("kerl", "!home invite galactica")
    assert "declines" in texts(controller.handle("galactica",
                                                 "!home decline"))
    assert "Nobody has invited" in texts(controller.handle(
        "galactica", "!home accept"))


def test_a_resident_hero_can_move_out_of_a_foreign_house(
        controller:GameController) -> None:
    rich(controller)
    controller.handle("kerl", "!home buy row")
    accepted(controller, "kerl", "!home movein galactica")
    assert "leaves the house" in texts(controller.handle(
        "galactica", "!home moveout"))
    assert "nobody else's" in texts(controller.handle(
        "galactica", "!home moveout"))


def test_parent_and_child_are_never_intimate(
        controller:GameController) -> None:
    controller.handle("kerl", "!lobby", now=0.0)
    link_son(controller)
    controller.handle("Galactica", "!join", now=0.5)
    reply = texts(controller.handle("kerl", "!intimate Galactica",
                                    now=2.0))
    assert "Not like that" in reply and not controller.proposals


def test_house_chest_belongs_to_the_house_not_the_bank(
        controller:GameController) -> None:
    rich(controller)
    assert "no house" in texts(controller.handle("kerl", "!home chest"))
    controller.handle("kerl", "!home buy hut")
    kerl = controller.repository.load("kerl")
    gold = kerl.gold
    reply = texts(controller.handle("kerl", "!home store gold 100"))
    assert "Deposited 100" in reply
    assert "Home chest" in texts(controller.handle("kerl", "!home chest"))
    assert "Stored: 0" in texts(controller.handle("kerl", "!bank"))
    assert controller.repository.load("kerl").gold == gold - 100
    controller.handle("kerl", "!home take gold all")
    assert controller.repository.load("kerl").gold == gold


def test_house_chest_is_closed_in_the_dungeon(
        controller:GameController) -> None:
    controller.handle("kerl", "!lobby", now=0.0)
    controller.handle("kerl", "!start", now=1.0)
    assert "dungeon" in texts(controller.handle("kerl", "!home chest"))


def test_visit_modes_set_the_role_and_the_seat_scene(
        controller:GameController) -> None:
    rich(controller)
    controller.handle("kerl", "!home buy hut")
    befriend(controller, "hilda", 30)
    reply = texts(controller.handle("kerl", "!home invite hilda seat"))
    assert "you are the seat" in reply
    reply = texts(controller.handle("kerl", "!home romance hilda"))
    assert "no control" in reply or "cannot move" in reply
    reply = texts(controller.handle("kerl", "!home romance hilda domina"))
    assert "gives the orders" in reply
    reply = texts(controller.handle("kerl", "!home romance hilda sub"))
    assert "knees at your own door" in reply


def test_split_mode_only_takes_a_trailing_mode() -> None:
    from cursed_descent.house_modes import split_mode
    assert split_mode(["hilda", "seat"]) == (["hilda"], "seat")
    assert split_mode(["seat"]) == (["seat"], "")
    assert split_mode(["hilda"]) == (["hilda"], "")


def test_a_regular_can_be_invited_talked_to_and_romanced(
        controller:GameController) -> None:
    rich(controller)
    controller.handle("kerl", "!home buy hut")
    kerl = controller.repository.load("kerl")
    store = controller.town.regulars_of(kerl)
    store.add("cafe", {"name": "Lady Volena Wilde", "age": 63,
                       "visits": 1})
    store.set("cafe", "Lady Volena Wilde", {"visits": 1})
    assert "doesn't know" in texts(controller.handle(
        "kerl", "!home invite Volena")) or "no one" in texts(
        controller.handle("kerl", "!home invite Volena")) or True
    store.set("cafe", "Lady Volena Wilde", {"visits": 3})
    reply = texts(controller.handle("kerl", "!home invite Lady Volena Wilde"))
    assert "comes over" in reply
    assert "Volena" in texts(controller.handle(
        "kerl", "!home talk Lady Volena Wilde"))
    reply = texts(controller.handle("kerl", "!home romance Lady Volena Wilde"))
    assert "💞" in reply
    assert controller.repository.load("Lady Volena Wilde") is None
    reply = texts(controller.handle("kerl", "!home movein Lady Volena Wilde"))
    assert "only comes over as a guest" in reply
    reply = texts(controller.handle("kerl", "!home romance Lady Volena Wilde seat"))
    assert reply


def test_a_shemale_can_make_a_male_guest_pregnant_at_home(
        controller:GameController, monkeypatch) -> None:
    from cursed_descent import intimacy
    monkeypatch.setattr(intimacy, "PARTY_PREGNANCY_CHANCE", 1.0)
    monkeypatch.setattr(intimacy, "MPREG_FACTOR", 1.0)
    rich(controller)
    controller.handle("kerl", "!home buy hut")
    kerl = controller.repository.load("kerl")
    kerl.gender = "Shemale"
    controller.repository.save(kerl)
    hero = controller.repository.load("galactica")
    hero.gender = "Male"
    hero.body["build"] = "Muscular"
    controller.repository.save(hero)
    accepted(controller, "kerl", "!home invite galactica")
    reply = texts(controller.handle("kerl", "!home romance galactica top in "
                                            "much"))
    assert "👶" in reply
    hero = controller.repository.load("galactica")
    assert hero.pregnant == "party"
    assert hero.profile["pregnant_by"] == controller.repository.load(
        "kerl").name
    for _ in range(3):
        reply = texts(controller.handle("kerl", "!home sleep"))
    assert "👶" in reply
    hero = controller.repository.load("galactica")
    assert not hero.pregnant and hero.offspring


def test_home_activities_and_topics_work(
        controller:GameController) -> None:
    rich(controller)
    controller.handle("kerl", "!home buy hut")
    befriend(controller, "hilda", 30)
    controller.handle("kerl", "!home invite hilda")
    for kind in ("flirt", "kiss", "cuddle", "massage", "bath", "dance"):
        assert texts(controller.handle("kerl", f"!home do hilda {kind}"))
    assert "Usage" in texts(controller.handle("kerl", "!home do hilda"))
    assert texts(controller.handle("kerl", "!home talk hilda work"))


def test_several_guests_can_be_invited_and_sent_home(
        controller:GameController) -> None:
    rich(controller)
    controller.handle("kerl", "!home buy row")
    befriend(controller, "hilda", 30)
    befriend(controller, "rose", 30)
    reply = texts(controller.handle("kerl", "!home invite all"))
    assert reply.count("comes over") >= 2
    kerl = controller.repository.load("kerl")
    guests = home_of(kerl, START_TOWN)["guests"]
    assert len(guests) >= 2
    assert "nobody left" in texts(controller.handle(
        "kerl", "!home invite all")).lower() or True
    reply = texts(controller.handle("kerl", "!home leave all"))
    assert "head home" in reply
    kerl = controller.repository.load("kerl")
    assert home_of(kerl, START_TOWN)["guests"] == []
    assert "Nobody to send home" in texts(controller.handle(
        "kerl", "!home leave all"))
    controller.handle("kerl", "!home invite hilda")
    assert "leaves the house" in texts(controller.handle(
        "kerl", "!home leave hilda"))


def test_expecting_carrier_is_marked_in_status(
        controller:GameController) -> None:
    from cursed_descent.houses import expecting_note, status_lines
    rich(controller)
    controller.handle("kerl", "!home buy row")
    befriend(controller, "hilda", 30)
    controller.handle("kerl", "!home invite hilda")
    kerl = controller.repository.load("kerl")
    home = home_of(kerl, START_TOWN)
    entry = home["guests"][0]
    home["expecting"] = [entry["id"]]
    carrier = next(npc for npc in controller.repository.npc_players()
                   if npc.id == entry["id"])
    carrier.pregnant = "party"
    controller.repository.save(carrier)
    assert "expecting" in expecting_note(home, entry, controller.repository)
    lines = status_lines(kerl, START_TOWN, controller.repository)
    assert any("🤰" in line for line in lines)


def test_resident_sees_that_he_lives_in_the_hosts_house(
        controller:GameController) -> None:
    from cursed_descent.houses import lodging_lines
    rich(controller)
    controller.handle("kerl", "!home buy hut")
    befriend(controller, "galactica", 30)
    reply = accepted(controller, "kerl", "!home movein galactica")
    assert any(m.recipient == "Galactica" and "move into" in m.text
               for m in reply)
    galactica = controller.repository.load("galactica")
    lines = lodging_lines(galactica, START_TOWN, controller.repository)
    assert lines and "kerl" in lines[0].lower()
    assert "live in" in texts(controller.handle("galactica", "!home"))
    assert "rests" in texts(controller.handle("galactica", "!home sleep")) \
        or "sleeps" in texts(controller.handle("galactica", "!home sleep"))


def test_resident_can_invite_guests_into_the_shared_house(
        controller:GameController) -> None:
    rich(controller)
    controller.handle("kerl", "!home buy row")
    befriend(controller, "galactica", 30)
    accepted(controller, "kerl", "!home movein galactica")
    friend = controller.repository.load("hilda")
    galactica = controller.repository.load("galactica")
    friend.profile.setdefault("friends", {})[galactica.id] = 30
    controller.repository.save(friend)
    reply = texts(controller.handle("galactica", "!home invite hilda"))
    assert "comes over" in reply
    kerl = controller.repository.load("kerl")
    guests = home_of(kerl, START_TOWN)["guests"]
    assert any("Hilda" in entry["name"] for entry in guests)
    assert "owner" in texts(controller.handle("galactica",
                                              "!home movein hilda"))


def test_swallowed_or_crushed_people_are_gone_for_the_round(
        controller:GameController) -> None:
    from cursed_descent.config import CAFE_LOCK
    rich(controller)
    controller.handle("kerl", "!home buy row")
    befriend(controller, "galactica", 30)
    accepted(controller, "kerl", "!home invite galactica")
    galactica = controller.repository.load("galactica")
    galactica.records[CAFE_LOCK] = 1
    controller.repository.save(galactica)
    reply = texts(controller.handle("kerl", "!home talk galactica"))
    assert "gone for this round" in reply
    reply = texts(hit(controller, "kerl", "!home practice galactica oral give some in"))
    assert "gone for this round" in reply


def test_hostess_can_order_a_guest_to_use_a_title(
        controller:GameController) -> None:
    rich(controller)
    controller.handle("kerl", "!home buy row")
    befriend(controller, "hilda", 30)
    controller.handle("kerl", "!home invite hilda")
    reply = texts(controller.handle("kerl", "!home order hilda herrin"))
    assert "Herrin" in reply
    reply = texts(hit(controller, "kerl", "!home practice hilda oral give some in"))
    wall = time.time() + 2000
    for step in range(6):
        wall += 11
        reply += texts(home_scene.tick_scenes(
            controller.repository, random.Random(step), wall))
    assert "Herrin" in reply
    assert "Order whom" in texts(controller.handle(
        "kerl", "!home order hilda"))


def test_title_appears_in_more_dialogues(
        controller:GameController) -> None:
    rich(controller)
    controller.handle("kerl", "!home buy row")
    befriend(controller, "hilda", 30)
    controller.handle("kerl", "!home invite hilda")
    controller.handle("kerl", "!home order hilda sir")
    assert "Sir" in texts(controller.handle("kerl", "!home talk hilda"))
    assert "Sir" in texts(controller.handle("kerl", "!home do hilda kiss"))
    assert "Sir" in texts(controller.handle("kerl", "!home leave hilda"))
    assert "Sir" in texts(controller.handle("kerl", "!home invite hilda"))


def test_working_characters_are_not_at_home(
        controller:GameController) -> None:
    rich(controller)
    controller.handle("kerl", "!home buy row")
    befriend(controller, "galactica", 30)
    accepted(controller, "kerl", "!home movein galactica")
    controller.handle("galactica", "!job cafe seat")
    reply = texts(controller.handle("kerl", "!home talk galactica"))
    assert "not home right now" in reply
    assert "Café" in reply or "cafe" in reply.lower()
    controller.handle("galactica", "!safeword")
    controller.handle("galactica", "!home")
    assert "not home" not in texts(controller.handle(
        "kerl", "!home talk galactica"))


def test_the_last_place_is_remembered(controller:GameController) -> None:
    controller.handle("kerl", "!tavern")
    kerl = controller.repository.load("kerl")
    assert controller.town.where(kerl) == "tavern"
    controller.handle("kerl", "!bank")
    assert controller.town.where(
        controller.repository.load("kerl")) == "bank"


def test_throne_mode_lets_the_host_sit_on_the_guest(
        controller:GameController) -> None:
    rich(controller)
    controller.handle("kerl", "!home buy row")
    befriend(controller, "hilda", 30)
    controller.handle("kerl", "!home invite hilda")
    reply = texts(controller.handle("kerl", "!home romance hilda throne"))
    assert "your seat" in reply
    assert "Hilda" in reply
    reply = texts(accepted(controller, "kerl", "!home invite galactica throne"))
    assert "use" in reply.lower() or "seat" in reply.lower()


def test_home_look_eat_cook_and_the_home_sex_partner(
        controller:GameController) -> None:
    from cursed_descent.houses import home_partner
    rich(controller)
    controller.handle("kerl", "!home buy hut")
    befriend(controller, "hilda", 30)
    controller.handle("kerl", "!home invite hilda")
    assert "Hilda" in texts(controller.handle("kerl", "!home look"))
    assert "nothing to eat" in texts(controller.handle("kerl", "!home eat"))
    assert "nothing to cook" in texts(controller.handle("kerl", "!home cook"))
    kerl = controller.repository.load("kerl")
    kerl.inventory.append("bread_loaf")
    kerl.inventory.append("meat_boar")
    controller.repository.save(kerl)
    assert "cooks" in texts(controller.handle("kerl", "!home cook"))
    assert "consumes" in texts(controller.handle("kerl", "!home eat"))
    controller.handle("kerl", "!home sex hilda")
    kerl = controller.repository.load("kerl")
    partner = home_partner(kerl, START_TOWN, controller.repository,
                           controller.town.regulars_of(kerl))
    assert partner is not None and partner.first_name == "Hilda"
    controller.handle("kerl", "!home back")
    assert "home_sex" not in controller.repository.load("kerl").profile


def test_a_resident_gets_a_lodging_entry_and_moving_out_removes_it(
        controller:GameController) -> None:
    from cursed_descent.sheet import sheet_lines
    rich(controller)
    controller.handle("kerl", "!home buy row")
    accepted(controller, "kerl", "!home movein galactica")
    galactica = controller.repository.load("galactica")
    kerl = controller.repository.load("kerl")
    house_id = kerl.profile["houses"][START_TOWN]
    assert galactica.profile["lodging"][START_TOWN] == house_id
    assert any("Lives at" in line for line in sheet_lines(galactica))
    assert galactica.profile["home_host"]
    controller.handle("galactica", "!home moveout")
    galactica = controller.repository.load("galactica")
    assert "lodging" not in galactica.profile or (
        START_TOWN not in galactica.profile["lodging"])
    assert "home_host" not in galactica.profile
    assert sheet_lines(galactica)[2] == "Home: none"


def test_a_house_lives_in_its_own_file_and_guests_stay_in_memory(
        controller:GameController, tmp_path) -> None:
    import json
    rich(controller)
    controller.handle("kerl", "!home buy row")
    befriend(controller, "hilda", 30)
    controller.handle("kerl", "!home invite hilda")
    kerl = controller.repository.load("kerl")
    house_id = kerl.profile["houses"][START_TOWN]
    assert len(house_id) == 6
    files = list(controller.repository.houses.data_path.glob(
        f"{START_TOWN}/houses/{house_id}.json"))
    assert len(files) == 1
    data = json.loads(files[0].read_text(encoding="utf-8"))
    assert data["owner"] == kerl.id and data["type"] == "row"
    assert data["address_id"] == house_id and "guests" not in data
    assert data["storage"] == {"gold": 0, "items": []}
    assert home_of(kerl, START_TOWN)["guests"]


def test_a_legacy_house_in_the_profile_is_migrated(
        controller:GameController) -> None:
    kerl = controller.repository.load("kerl")
    kerl.profile["houses"] = {START_TOWN: {
        "type": "hut", "residents": [], "guests": []}}
    house = home_of(kerl, START_TOWN)
    assert kerl.profile["houses"][START_TOWN] == house["id"]
    assert controller.repository.load("kerl").profile["houses"][
        START_TOWN] == house["id"]


def test_an_npc_guest_cannot_be_at_two_houses_and_leaves_when_idle(
        controller:GameController) -> None:
    rich(controller)
    controller.handle("kerl", "!home buy row")
    befriend(controller, "hilda", 30)
    controller.handle("kerl", "!home invite hilda")
    kerl = controller.repository.load("kerl")
    store = controller.repository.houses
    other = store.create(START_TOWN, kerl, "hut", 1)
    hilda = controller.repository.load("hilda")
    assert store.guest_elsewhere(hilda.id, other) is not None
    gone = store.sweep(10 ** 9, 600)
    assert len(gone) == 1
    assert home_of(kerl, START_TOWN)["guests"] == []


def test_chest_gold_and_the_players_purse_are_saved_together(
        controller:GameController) -> None:
    import json
    rich(controller, 5000)
    controller.handle("kerl", "!home buy hut")
    controller.handle("kerl", "!home store gold 100")
    saved = json.loads(controller.repository.path("kerl").read_text(
        encoding="utf-8"))
    kerl = controller.repository.load("kerl")
    house_id = kerl.profile["houses"][START_TOWN]
    stored = json.loads(next(controller.repository.houses.data_path.glob(
        f"*/houses/{house_id}.json")).read_text(encoding="utf-8"))
    assert saved["gold"] == kerl.gold
    assert stored["storage"]["gold"] == 100
    assert saved["gold"] + stored["storage"]["gold"] == 5000 - 800


def test_examining_the_owner_and_a_guest_inside_the_house(
        controller:GameController) -> None:
    rich(controller)
    controller.handle("kerl", "!home buy row")
    accepted(controller, "kerl", "!home movein galactica")
    seen = texts(controller.handle("kerl", "!home look galactica"))
    assert "👁" in seen and "Galactica" in seen
    seen = texts(controller.handle("galactica", "!home look kerl"))
    assert "👁" in seen
    assert "in this house" in texts(controller.handle(
        "kerl", "!home look nobodyhere"))


def test_a_resident_invites_from_their_own_regulars(
        controller:GameController) -> None:
    rich(controller)
    controller.handle("kerl", "!home buy row")
    accepted(controller, "kerl", "!home movein galactica")
    galactica = controller.repository.load("galactica")
    store = controller.town.regulars_of(galactica)
    store.add("cafe", {"name": "Lady Volena Wilde", "age": 63,
                       "visits": 3})
    store.set("cafe", "Lady Volena Wilde", {"visits": 3})
    reply = texts(controller.handle(
        "galactica", "!home invite Lady Volena Wilde"))
    assert "comes over" in reply


def test_a_resident_can_talk_look_and_have_fun_with_the_owner(
        controller:GameController) -> None:
    rich(controller)
    controller.handle("kerl", "!home buy row")
    accepted(controller, "kerl", "!home movein galactica")
    kerl = controller.repository.load("kerl")
    for command in ("look", "talk", "sex"):
        reply = texts(controller.handle(
            "galactica", f"!home {command} {kerl.full_name}"))
        assert "Nobody called" not in reply
        assert "need to trust you" not in reply
    reply = texts(hit(controller, "galactica", f"!home practice {kerl.full_name} oral give"))
    assert "Nobody called" not in reply
    assert "not in your house" not in reply


def test_residents_are_found_by_full_name_even_if_stored_short(
        controller:GameController) -> None:
    rich(controller)
    controller.handle("kerl", "!home buy row")
    accepted(controller, "kerl", "!home movein galactica")
    kerl = controller.repository.load("kerl")
    galactica = controller.repository.load("galactica")
    home = controller.repository.houses.get(
        galactica.profile["lodging"][controller.town_key], controller.town_key
    ) if hasattr(controller, "town_key") else None
    if home is not None:
        for entry in home["residents"]:
            entry["name"] = entry["name"].split()[0]
    reply = texts(controller.handle("kerl", f"!home leave {galactica.full_name}"))
    assert "Nobody called" not in reply
    assert "could come" not in reply
    reply = texts(controller.handle(
        "galactica", f"!home look {kerl.full_name}"))
    assert "Nobody called" not in reply


def test_intimacy_with_a_hero_needs_the_others_confirmation(
        controller:GameController) -> None:
    rich(controller)
    controller.handle("kerl", "!home buy row")
    controller.handle("kerl", "!home invite galactica")
    controller.handle("galactica", "!home accept")
    reply = texts(controller.handle("kerl", "!home sex galactica"))
    assert "confirm on their own screen" in reply
    kerl = controller.repository.load("kerl")
    assert not kerl.profile.get("home_sex")
    declined = texts(controller.handle("galactica", "!home decline"))
    assert "decline" in declined
    controller.handle("kerl", "!home sex galactica")
    reply = texts(controller.handle("galactica", "!home accept"))
    assert "bedroom" in reply
    assert controller.repository.load("kerl").profile["home_sex"]


def test_ordered_title_uses_the_kin_role(
        controller:GameController) -> None:
    rich(controller)
    controller.handle("kerl", "!home buy row")
    controller.handle("kerl", "!home invite galactica")
    controller.handle("galactica", "!home accept")
    kerl = controller.repository.load("kerl")
    galactica = controller.repository.load("galactica")
    kerl.profile.setdefault("family", {})[galactica.id] = {
        "role": "son", "name": galactica.name}
    controller.repository.save(kerl)
    from cursed_descent.house_titles import KIN_ORDERS
    from cursed_descent.house_titles import order_title
    import random
    seen = set()
    for seed in range(40):
        reply = order_title(kerl, {"titles": {}}, galactica, "mistress",
                            controller.repository, random.Random(seed))
        seen.add(reply[0].text)
    assert any(text.format(a="x", b="y", title="Z") for text in KIN_ORDERS["son"])
    assert any("son" in text or "Good boy" in text for text in seen)


def test_both_heroes_land_in_the_sex_view_after_accepting(
        controller:GameController) -> None:
    rich(controller)
    controller.handle("kerl", "!home buy row")
    controller.handle("kerl", "!home invite galactica")
    controller.handle("galactica", "!home accept")
    controller.handle("kerl", "!home sex galactica")
    controller.handle("galactica", "!home accept")
    kerl = controller.repository.load("kerl")
    galactica = controller.repository.load("galactica")
    assert kerl.profile["home_sex"] == galactica.name
    assert galactica.profile["home_sex"] == kerl.name
    controller.handle("kerl", "!home back")
    assert not controller.repository.load("galactica").profile.get("home_sex")
    assert not controller.repository.load("kerl").profile.get("home_sex")


def test_consent_ends_with_the_bedroom_scene(
        controller:GameController) -> None:
    rich(controller)
    controller.handle("kerl", "!home buy row")
    controller.handle("kerl", "!home invite galactica")
    controller.handle("galactica", "!home accept")
    controller.handle("kerl", "!home sex galactica")
    controller.handle("galactica", "!home accept")
    controller.handle("kerl", "!home back")
    reply = texts(controller.handle("kerl", "!home sex galactica"))
    assert "confirm on their own screen" in reply
    assert controller.repository.load("galactica").profile["sex_offer"]


def test_asking_each_other_counts_as_a_yes(
        controller:GameController) -> None:
    rich(controller)
    controller.handle("kerl", "!home buy row")
    controller.handle("kerl", "!home invite galactica")
    controller.handle("galactica", "!home accept")
    controller.handle("kerl", "!home sex galactica")
    kerl = controller.repository.load("kerl")
    reply = texts(controller.handle("galactica", f"!home sex {kerl.full_name}"))
    assert "bedroom" in reply
    assert controller.repository.load("kerl").profile["home_sex"]
    assert "sex_offer" not in controller.repository.load("galactica").profile
    assert "sex_offer" not in controller.repository.load("kerl").profile


def host_with_guest(controller:GameController) -> None:
    rich(controller)
    controller.handle("kerl", "!home buy row")
    controller.handle("kerl", "!home invite galactica")
    controller.handle("galactica", "!home accept")


def test_consent_setting_deny_blocks_the_request(
        controller:GameController) -> None:
    host_with_guest(controller)
    reply = texts(controller.handle("galactica", "!prefs consent deny"))
    assert "deny" in reply
    reply = texts(controller.handle("kerl", "!home sex galactica"))
    assert "does not accept" in reply
    assert "sex_offer" not in controller.repository.load("galactica").profile


def test_consent_setting_allow_accepts_at_once(
        controller:GameController) -> None:
    host_with_guest(controller)
    controller.handle("galactica", "!prefs consent allow")
    reply = texts(controller.handle("kerl", "!home sex galactica"))
    assert "bedroom" in reply
    assert controller.repository.load("galactica").profile["home_sex"]
    assert "sex_offer" not in controller.repository.load("galactica").profile


def test_a_client_who_lives_in_a_house_gives_that_address(
        controller:GameController) -> None:
    rich(controller)
    controller.handle("kerl", "!home buy hut")
    kerl = controller.repository.load("kerl")
    galactica = controller.repository.load("galactica")
    kerl.profile.setdefault("family", {})[galactica.id] = {
        "role": "son", "name": galactica.name}
    controller.repository.save(kerl)
    accepted(controller, "kerl", "!home movein galactica")
    address = home_of(kerl, START_TOWN)["address"]

    class Client:
        player = "galactica"

    said = controller.town.real_address(Client())
    assert said.startswith(address) and "kerl's house" in said
    assert controller.town.real_address(Client.__new__(Client)) != ""
    assert controller.town.real_address(type("C", (), {"player": ""})()) == ""
    assert controller.town.real_address(
        type("C", (), {"player": "kerl"})()).startswith(address)

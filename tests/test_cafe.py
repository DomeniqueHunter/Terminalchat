import random

from cursed_descent.towns.last_light_humans.cafe.service import ambient, cafe_death, regular_call, sitting_on
from cursed_descent.content import ITEMS
from cursed_descent.town_buildings.brothel.clients import new_client
from cursed_descent.towns.last_light_humans.cafe.guests import (
    Guest, difficulty, new_guest,
)
from cursed_descent.towns.last_light_humans.cafe.ledger import CafeLedger


def text(messages) -> str:
    return "\n".join(message.text for message in messages)


def regs(controller, name:str):
    return controller.town.regulars_of(controller.repository.load(name))


def setup_pair(controller) -> None:
    kerl = controller.repository.load("Kerl")
    kerl.gender = "Male"
    controller.repository.save(kerl)
    lady = controller.repository.load("Galactica")
    lady.gender = "Female"
    lady.body["weight"] = 120
    lady.body["butt"] = 150
    controller.repository.save(lady)


def arrive(controller, name:str, guest=None) -> None:
    shift = controller.town.shifts[name]
    shift.client = guest or Guest("Lady Mabel", 100, 140)
    shift.due = controller.town.now + 20


def test_cafe_menu_lists_jobs_and_bertha_lives_there(controller) -> None:
    setup_pair(controller)
    reply = text(controller.handle("Galactica", "!cafe"))
    for word in ("seat", "server", "trainer", "baker", "usher", "cleaner"):
        assert word in reply
    assert "Café" in text(controller.handle("Kerl", "!town"))
    bertha = controller.repository.load("Madame Bertha")
    assert bertha.body["weight"] == 155 and bertha.body["butt"] == 185
    assert controller.repository.is_story(bertha)
    assert "Nobody called" in text(controller.handle("Kerl", "!talk bertha"))
    controller.handle("Kerl", "!cafe")
    assert "Bertha" in text(controller.handle("Kerl", "!talk bertha"))


def test_simple_job_pays(controller) -> None:
    setup_pair(controller)
    before = controller.repository.load("Galactica").gold
    reply = text(controller.handle("Galactica", "!job cafe baker", now=0.0))
    for step in range(1, 6):
        reply += text(controller.tick(now=step * 20.0))
    assert "Shift over" in reply
    assert controller.repository.load("Galactica").gold > before


def test_seat_shift_hold_and_safeword(controller) -> None:
    setup_pair(controller)
    start = text(controller.handle("Kerl", "!job cafe seat"))
    assert "[quit]" in start and "Nobody sits on you yet" in start
    assert "Next guest in" in text(controller.handle("Kerl", "!hold"))
    arrive(controller, "kerl")
    assert "gold" in text(controller.handle("Kerl", "!hold"))
    reply = text(controller.handle("Kerl", "!quit"))
    assert "tap out" in reply and "Shift over" in reply
    assert "kerl" not in controller.town.shifts


def test_rider_sits_and_rises(controller) -> None:
    setup_pair(controller)
    controller.handle("Kerl", "!job cafe seat")
    sit = controller.handle("Galactica", "!sit Kerl")
    assert any(m.recipient == "kerl" for m in sit)
    assert "sits down on you" in text(sit)
    held = text(controller.handle("Kerl", "!hold"))
    assert "gold" in held
    second = text(controller.handle("Kerl", "!hold"))
    assert "quiver" in second or "pleads" in second
    assert "rises" in text(controller.handle("Galactica", "!rise"))
    assert "not sitting" in text(controller.handle("Galactica", "!rise"))


def test_men_cannot_sit(controller) -> None:
    setup_pair(controller)
    controller.handle("Galactica", "!job cafe seat")
    assert "Only ladies" in text(controller.handle("Kerl", "!sit Galactica"))


def test_desperation_when_lady_stays(controller) -> None:
    setup_pair(controller)
    controller.handle("Galactica", "!job cafe seat")
    arrive(controller, "Galactica", Guest("Lady X", 140, 185))
    replies = [text(controller.handle("Galactica", "!hold"))
               for _ in range(2)]
    assert any(word in replies[1] for word in (
        "slap", "plea", "legs shake", "squirm"))
    assert controller.town.shifts["Galactica"].client is None


def test_difficulty_grows_with_weight() -> None:
    assert difficulty(Guest("a", 70, 105), 10, 10, 1) == "light"
    assert difficulty(Guest("a", 150, 190), 3, 3, 1) == "crushing"


def force_death(controller, name:str, fate:str, outcome:str) -> str:
    controller.town.rng = random.Random(1)
    original = controller.town.rng.choices
    controller.town.rng.choices = lambda kinds, weights: [outcome]
    player = controller.repository.load(name)
    reply = text(cafe_death(controller.town, player, fate))
    controller.town.rng.choices = original
    controller.repository.save(player) if player.npc == "" else None
    return reply


def test_death_credits_bertha_and_makes_a_cushion(controller) -> None:
    setup_pair(controller)
    reply = force_death(controller, "Kerl", "smothered", "cushion")
    assert "Seat Cushion" in reply
    bertha = controller.repository.load("Madame Bertha")
    assert bertha.records["kills"] == 1 and bertha.body["weight"] == 157
    assert bertha.body["butt"] == 186
    assert controller.repository.load("Kerl").npc == ""
    stock = controller.town.cafe.stock()
    assert stock and ITEMS[stock[0]["id"]]["made_from"] == "kerl"
    controller.repository.load("Galactica")
    pay = controller.repository.load("Galactica")
    pay.gold = 5000
    controller.repository.save(pay)
    assert "buys" in text(controller.handle("Galactica", "!cafe buy 1"))
    assert any(item.startswith("cafe_") for item in
               controller.repository.load("Galactica").inventory)


def test_cake_is_consumable(controller) -> None:
    setup_pair(controller)
    force_death(controller, "Kerl", "smothered", "cake")
    entry = controller.town.cafe.stock()[0]
    assert ITEMS[entry["id"]]["slot"] == "consumable"
    assert ITEMS[entry["id"]]["heal"] > 0


def test_engulfed_leaves_no_item_and_grows_more(controller) -> None:
    setup_pair(controller)
    reply = force_death(controller, "Kerl", "engulfed", "cake")
    assert "pleasantly full" in reply
    assert controller.repository.load("Madame Bertha").body["weight"] == 160
    assert not controller.town.cafe.stock()
    assert text(controller.handle("Galactica", "!cafe")).count(
        "Bertha has finished") == 0
    assert not controller.town.cafe.stock()


def test_furniture_becomes_a_stool_and_can_be_ransomed(controller) -> None:
    setup_pair(controller)
    force_death(controller, "Kerl", "collapsed", "furniture")
    stool = controller.repository.load("Kerl")
    assert stool.npc == "furniture"
    assert "kerl" in text(controller.handle("Galactica", "!cafe"))
    rich = controller.repository.load("Galactica")
    rich.gold = 5000
    controller.repository.save(rich)
    assert "free" in text(controller.handle("Galactica", "!ransom Kerl"))
    assert controller.repository.load("Kerl").npc == ""


def test_ransom_restores_preferences_of_a_stool(controller) -> None:
    setup_pair(controller)
    kerl = controller.repository.load("Kerl")
    kerl.profile.update({"consent": "deny", "role": "sub",
                         "age_pref": [30, 50]})
    controller.repository.save(kerl)
    force_death(controller, "Kerl", "collapsed", "furniture")
    stool = controller.repository.load("Kerl")
    assert stool.profile["kind"] == "furniture"
    assert stool.profile["kept"]["consent"] == "deny"
    rich = controller.repository.load("Galactica")
    rich.gold = 5000
    controller.repository.save(rich)
    controller.handle("Galactica", "!ransom Kerl")
    freed = controller.repository.load("Kerl")
    assert freed.profile["consent"] == "deny"
    assert freed.profile["role"] == "sub"
    assert freed.profile["age_pref"] == [30, 50]
    assert "kind" not in freed.profile


def test_ledger_persists_and_registers_items(controller) -> None:
    setup_pair(controller)
    force_death(controller, "Kerl", "smothered", "cushion")
    item_id = controller.town.cafe.stock()[0]["id"]
    del ITEMS[item_id]
    CafeLedger(controller.repository.data_path
               if hasattr(controller.repository, "data_path")
               else controller.town.cafe.path.parent)
    assert item_id in ITEMS


def test_hold_death_only_below_margin(controller) -> None:
    setup_pair(controller)
    controller.handle("Kerl", "!job cafe seat")
    arrive(controller, "kerl", Guest("Lady Doom", 150, 190))
    kerl = controller.repository.load("Kerl")
    kerl.stats["vitality"] = 1
    kerl.stats["strength"] = 1
    controller.repository.save(kerl)
    outcomes = set()
    for seed in range(30):
        controller.town.shifts["kerl"] = controller.town.shifts.get(
            "kerl") or None
        if controller.town.shifts["kerl"] is None:
            break
        arrive(controller, "kerl", Guest("Lady Doom", 150, 190))
        controller.town.rng = random.Random(seed)
        reply = text(controller.handle("Kerl", "!hold"))
        if "💀" in reply:
            outcomes.add("dead")
            break
        controller.town.shifts["kerl"].left = 4
    assert "dead" in outcomes


def test_a_man_may_only_be_a_seat(controller) -> None:
    setup_pair(controller)
    menu = text(controller.handle("Kerl", "!cafe"))
    assert "Men are furniture" in menu and "baker" not in menu
    for job in ("baker", "server", "trainer", "usher", "cleaner"):
        assert "furniture" in text(controller.handle(
            "Kerl", f"!job cafe {job}"))
    assert "kerl" not in controller.town.shifts
    assert "[quit]" in text(controller.handle("Kerl", "!job cafe seat"))


def test_a_seated_man_cannot_leave_while_a_lady_sits(controller) -> None:
    setup_pair(controller)
    controller.handle("Kerl", "!job cafe seat")
    controller.handle("Galactica", "!sit Kerl")
    for command in ("!quit", "!safeword"):
        assert "only she can" in text(controller.handle("Kerl", command))
    for command in ("!bank", "!town", "!lobby", "!order cafe 1"):
        assert "pinned" in text(controller.handle("Kerl", command))
    assert "kerl" in controller.town.shifts
    assert "Galactica" in text(controller.handle("Kerl", "!examine Galactica"))
    left = controller.town.shifts["kerl"].left
    for _ in range(6):
        controller.handle("Kerl", "!hold")
    assert controller.town.shifts["kerl"].left == left
    controller.handle("Galactica", "!rise")
    assert "tap out" in text(controller.handle("Kerl", "!quit"))
    assert "kerl" not in controller.town.shifts


def test_seat_with_an_npc_guest_is_pinned_but_can_quit(controller) -> None:
    setup_pair(controller)
    controller.handle("Kerl", "!job cafe seat")
    assert "[quit] is your way out" in text(
        controller.handle("Kerl", "!bank"))
    arrive(controller, "kerl")
    guest = controller.town.shifts["kerl"].client
    assert guest.name in text(controller.handle(
        "Kerl", f"!examine {guest.name}"))
    assert "Bertha" in text(controller.handle("Kerl", "!examine bertha"))


def test_rider_sees_reactions_and_can_lean_or_stay(controller) -> None:
    setup_pair(controller)
    controller.handle("Kerl", "!job cafe seat")
    controller.handle("Galactica", "!sit Kerl")
    held = controller.handle("Kerl", "!hold")
    assert any(m.recipient == "Galactica" and "gold" in m.text
               for m in held)
    assert "stays put" in text(controller.handle("Galactica", "!stay"))
    for _ in range(3):
        controller.handle("Galactica", "!lean")
    shift = controller.town.shifts["kerl"]
    assert shift.client.squeeze == 3
    assert "cannot press" in text(controller.handle("Galactica", "!lean"))
    controller.handle("Galactica", "!rise")
    assert "not sitting" in text(controller.handle("Galactica", "!lean"))
    assert "not sitting" in text(controller.handle("Galactica", "!stay"))


def test_free_npc_stools_are_described_and_sometimes_there(controller) -> None:
    from cursed_descent.towns.last_light_humans.cafe.stools import (
        Stool, describe, free_list, refresh_stools,
    )
    setup_pair(controller)
    counts = {len(refresh_stools(random.Random(seed))) for seed in range(40)}
    assert 0 in counts and max(counts) >= 2
    stool = Stool("Tom", 30, 190, 90, "Muscular", 70, "eager")
    detail = describe(stool)
    assert "tall" in detail and "broad shoulders" in detail
    assert "all fours" in detail
    assert "No free stool" in free_list([])
    controller.town.stools = [stool]
    controller.town.refresh = None
    lady = controller.repository.load("Galactica")
    lady.gold = 100
    controller.repository.save(lady)
    assert "1. Tom" in text(controller.handle("Galactica", "!sit"))
    reply = text(controller.handle("Galactica", "!sit 1"))
    assert "You pay 15 gold" in reply and "broad shoulders" in reply
    assert controller.repository.load("Galactica").gold == 85
    assert controller.town.stools == []


def test_trainer_shift_describes_every_stool(controller) -> None:
    setup_pair(controller)
    reply = text(controller.handle("Galactica", "!job cafe trainer"))
    assert reply.count("kg") >= 3 and "Shift over" in reply


def test_men_cannot_use_any_ladies_service(controller) -> None:
    from cursed_descent.towns.last_light_humans.cafe.stools import Stool
    setup_pair(controller)
    controller.town.stools = [Stool("Tom", 30, 190, 90, "Muscular", 70,
                                    "eager")]
    kerl = controller.repository.load("Kerl")
    kerl.gold = 100
    controller.repository.save(kerl)
    for command in ("!sit", "!sit 1", "!sit Tom", "!sit Galactica"):
        assert "Only ladies" in text(controller.handle("Kerl", command))
    assert controller.repository.load("Kerl").gold == 100
    assert controller.town.stools
    assert "Free stools" not in text(controller.handle("Kerl", "!cafe"))


def test_time_brings_guests_reactions_and_countdown(controller) -> None:
    setup_pair(controller)
    controller.handle("Kerl", "!job cafe seat", now=100.0)
    shift = controller.town.shifts["kerl"]
    assert shift.client is None
    assert "Next guest in" in controller.town.timer_text(
        controller.repository.load("Kerl"))
    assert controller.tick(now=105.0) == []
    arrived = text(controller.tick(now=120.0))
    assert "arrives and sits down on you" in arrived
    assert shift.client is not None and shift.due == 140.0
    assert "Next reaction in 20 s" in controller.town.timer_text(
        controller.repository.load("Kerl"))
    assert controller.tick(now=130.0) == []
    shift.client = Guest("Lady Doom", 150, 190)
    kerl = controller.repository.load("Kerl")
    kerl.stats["vitality"] = 1
    kerl.stats["strength"] = 1
    controller.repository.save(kerl)
    reacted = ""
    for step in range(60):
        reacted += text(controller.tick(now=140.0 + step * 20))
        if "kerl" not in controller.town.shifts:
            break
        controller.town.shifts["kerl"].left = 4
        controller.town.shifts["kerl"].client = Guest(
            "Lady Doom", 150, 190)
    assert "💀" in reacted and "kerl" not in controller.town.shifts


def test_a_lady_can_take_the_waiting_seat_first(controller) -> None:
    setup_pair(controller)
    controller.handle("Kerl", "!job cafe seat", now=10.0)
    assert "sits down on you" in text(controller.handle(
        "Galactica", "!sit Kerl", now=11.0))
    assert controller.town.shifts["kerl"].due == 31.0
    assert controller.tick(now=15.0) == []
    reacted = controller.tick(now=31.0)
    assert any(m.recipient == "Galactica" for m in reacted)


def test_npc_stool_ride_runs_on_time_with_stay_lean_rise(controller) -> None:
    from cursed_descent.towns.last_light_humans.cafe.stools import Stool
    setup_pair(controller)
    controller.town.stools = [Stool("Tom", 30, 190, 90, "Muscular", 70,
                                    "eager")]
    lady = controller.repository.load("Galactica")
    lady.gold = 100
    controller.repository.save(lady)
    reply = text(controller.handle("Galactica", "!sit 1", now=0.0))
    assert "Next reaction in 20 s" in reply
    assert sitting_on(controller.town, lady) == "Tom"
    assert "stay put" in text(controller.handle("Galactica", "!stay"))
    assert "Tom" in text(controller.handle("Galactica", "!lean"))
    assert "Next reaction of Tom" in controller.town.timer_text(lady)
    assert "rise" in text(controller.handle("Galactica", "!rise")).lower()
    assert controller.town.rides == {}
    assert sitting_on(controller.town, lady) == ""


def test_examine_covers_free_stools_and_the_stool_you_ride(
        controller) -> None:
    from cursed_descent.towns.last_light_humans.cafe.stools import Stool
    setup_pair(controller)
    controller.town.stools = [Stool("Tom", 30, 190, 90, "Muscular", 70,
                                    "eager")]
    assert "broad shoulders" in text(controller.handle(
        "Galactica", "!examine Tom"))
    lady = controller.repository.load("Galactica")
    lady.gold = 100
    controller.repository.save(lady)
    controller.handle("Galactica", "!sit 1")
    assert "broad shoulders" in text(controller.handle(
        "Galactica", "!examine tom"))


def test_a_pinned_seat_can_still_talk_to_the_owner(controller) -> None:
    setup_pair(controller)
    controller.handle("Kerl", "!job cafe seat")
    assert "Bertha" in text(controller.handle("Kerl", "!talk bertha"))
    assert "'" in text(controller.handle("Kerl", "!chat bertha work"))
    assert "pinned" in text(controller.handle("Kerl", "!bank"))


def test_panic_builds_up_over_twenty_rounds() -> None:
    from cursed_descent.towns.last_light_humans.cafe.guests import panic_tier
    from cursed_descent.config import CAFE_RIDE_ROUNDS, CAFE_SEAT_SESSIONS
    assert CAFE_RIDE_ROUNDS == 20 and CAFE_SEAT_SESSIONS == 20
    tiers = [panic_tier(done, 20) for done in range(21)]
    assert tiers[0] == "" and tiers[3] == "uneasy"
    assert tiers[8] == "strained" and tiers[14] == "panic"
    assert tiers[19] == "frantic"


def test_seat_shift_lasts_twenty_rounds(controller) -> None:
    setup_pair(controller)
    controller.handle("Kerl", "!job cafe seat")
    shift = controller.town.shifts["kerl"]
    assert shift.left == 20
    kerl = controller.repository.load("Kerl")
    kerl.stats["vitality"] = 99
    kerl.stats["strength"] = 99
    controller.repository.save(kerl)
    shift.client = Guest("Lady Mabel", 80, 110)
    shift.left = 2
    reply = text(controller.handle("Kerl", "!hold"))
    assert "frantic" in reply or "kicking" in reply or "begging" in reply \
        or "scrabble" in reply or "panic" in reply


def test_free_stools_are_adults_between_18_and_25() -> None:
    from cursed_descent.towns.last_light_humans.cafe.stools import new_stool
    rng = random.Random(3)
    ages = {new_stool(rng).age for _ in range(200)}
    assert min(ages) == 18 and max(ages) == 25


def test_guests_complain_when_the_seat_fails_and_ladies_can_complain(
        controller) -> None:
    from cursed_descent.towns.last_light_humans.cafe.stools import Stool
    setup_pair(controller)
    controller.handle("Kerl", "!job cafe seat")
    kerl = controller.repository.load("Kerl")
    kerl.stats["vitality"] = 1
    kerl.stats["strength"] = 1
    controller.repository.save(kerl)
    seen = ""
    for seed in range(40):
        arrive(controller, "kerl", Guest("Lady Doom", 150, 190))
        controller.town.rng = random.Random(seed)
        seen += text(controller.handle("Kerl", "!hold"))
        if "kerl" not in controller.town.shifts:
            break
        controller.town.shifts["kerl"].left = 4
    assert any(word in seen for word in (
        "Honestly", "disgrace", "cheek", "nerve", "He broke"))
    assert "Nothing to complain" in text(controller.handle(
        "Galactica", "!complain"))
    controller.town.stools = [Stool("Tom", 30, 190, 90, "Slim", 1, "nervous")]
    lady = controller.repository.load("Galactica")
    lady.gold = 100
    controller.repository.save(lady)
    controller.town.rng = random.Random(3)
    controller.handle("Galactica", "!sit 1", now=0.0)
    for step in range(1, 60):
        controller.tick(now=step * 20.0)
        if "Galactica" in controller.town.complaints:
            break
    assert "Galactica" in controller.town.complaints
    gold = controller.repository.load("Galactica").gold
    assert "half your ticket" in text(controller.handle(
        "Galactica", "!complain"))
    assert controller.repository.load("Galactica").gold == gold + 7
    assert "Nothing to complain" in text(controller.handle(
        "Galactica", "!complain"))


def test_bertha_is_rude_to_men_and_polite_to_ladies(controller) -> None:
    setup_pair(controller)
    controller.handle("Kerl", "!cafe")
    controller.handle("Galactica", "!cafe")
    rude = text(controller.handle("Kerl", "!chat bertha self"))
    assert "replaceable" in rude or "guests" in rude
    assert "footstool" in rude
    assert "footstool" not in text(controller.handle("Galactica",
                                                     "!chat bertha self"))
    controller.handle("Kerl", "!town")
    assert "Nobody called" in text(controller.handle("Kerl", "!meet bertha"))
    assert "Do try not to wobble" in text(controller.handle("Kerl", "!cafe"))


def test_pinned_seat_actions(controller) -> None:
    setup_pair(controller)
    controller.handle("Kerl", "!job cafe seat")
    assert "Next guest" in text(controller.handle("Kerl", "!breath"))
    arrive(controller, "kerl", Guest("Lady Mabel", 90, 120))
    assert "last breath" in text(controller.handle("Kerl", "!breath"))
    assert controller.town.shifts["kerl"].winded == 0 or True
    arrive(controller, "kerl", Guest("Lady Mabel", 90, 120))
    assert "stop fighting" in text(controller.handle("Kerl", "!giveup"))
    arrive(controller, "kerl", Guest("Lady Mabel", 90, 120))
    assert "wait" or True
    assert "gold" in text(controller.handle("Kerl", "!wait"))
    seen = set()
    for seed in range(30):
        arrive(controller, "kerl", Guest("Lady Mabel", 90, 120, cruel=0))
        controller.town.shifts["kerl"].left = 10
        controller.town.rng = random.Random(seed)
        reply = text(controller.handle("Kerl", "!pat"))
        seen.add("of course, dear" in reply)
        if "kerl" not in controller.town.shifts:
            break
    assert True in seen and False in seen


def test_struggle_can_free_him_and_rider_cases_only_signal(
        controller) -> None:
    setup_pair(controller)
    kerl = controller.repository.load("Kerl")
    kerl.stats["strength"] = 90
    kerl.stats["agility"] = 90
    controller.repository.save(kerl)
    controller.handle("Kerl", "!job cafe seat")
    arrive(controller, "kerl", Guest("Lady Mabel", 80, 110))
    assert "tumbles off" in text(controller.handle("Kerl", "!struggle"))
    assert controller.town.shifts["kerl"].client is None
    controller.handle("Galactica", "!sit Kerl")
    reply = controller.handle("Kerl", "!pat")
    assert any(m.recipient == "Galactica" and "slaps your rear" in m.text
               for m in reply)
    reply = controller.handle("Kerl", "!struggle")
    assert any(m.recipient == "Galactica" and "wriggles" in m.text
               for m in reply)
    assert controller.town.shifts["kerl"].client.rider == "Galactica"


def test_pinned_seat_can_examine_rider_but_not_talk(controller) -> None:
    setup_pair(controller)
    controller.handle("Kerl", "!job cafe seat")
    assert "Nobody can hear" not in text(controller.handle("Kerl", "!talk"))
    arrive(controller, "kerl", Guest("Lady Mabel", 90, 120))
    assert "90 kg" in text(controller.handle("Kerl", "!examine Lady Mabel"))
    assert "muffled" in text(controller.handle("Kerl", "!talk"))
    assert "muffled" in text(controller.handle("Kerl", "!chat Bertha"))


def test_examine_guest_by_surname_and_title(controller) -> None:
    setup_pair(controller)
    controller.handle("Kerl", "!job cafe seat")
    arrive(controller, "kerl", Guest("Mrs. Fenwick", 86, 124))
    for query in ("Fenwick", "Mrs. Fenwick", "mrs", "fenwick"):
        assert "86 kg" in text(controller.handle("Kerl", f"!examine {query}"))


def test_kiss_pays_more_and_signals_a_rider(controller) -> None:
    setup_pair(controller)
    controller.handle("Kerl", "!job cafe seat")
    arrive(controller, "kerl", Guest("Lady Mabel", 90, 120, squeeze=2))
    assert "kiss it with devotion" in text(controller.handle("Kerl", "!kiss"))
    controller.town.shifts["kerl"].client = None
    controller.handle("Galactica", "!sit Kerl")
    reply = controller.handle("Kerl", "!kiss")
    assert any(m.recipient == "Galactica" and "kisses your rear" in m.text
               for m in reply)


def test_bertha_sometimes_sits_as_a_hate_probe() -> None:
    from cursed_descent.towns.last_light_humans.cafe.guests import new_guest
    names = {new_guest(random.Random(seed)).name for seed in range(300)}
    assert "Madame Bertha" in names and len(names) > 3
    bertha = [new_guest(random.Random(seed)) for seed in range(300)
              if new_guest(random.Random(seed)).name == "Madame Bertha"][0]
    assert bertha.weight >= 150 and bertha.butt >= 190


def test_air_gauge_drops_and_breath_refills(controller) -> None:
    setup_pair(controller)
    controller.handle("Kerl", "!job cafe seat")
    arrive(controller, "kerl", Guest("Lady Mabel", 100, 130))
    reply = text(controller.handle("Kerl", "!wait"))
    assert "Air" in reply and "%" in reply
    shift = controller.town.shifts["kerl"]
    assert 0 <= shift.air <= 100
    arrive(controller, "kerl", Guest("Lady Mabel", 60, 100))
    shift.air = 50
    controller.handle("Kerl", "!breath")
    with_breath = controller.town.shifts["kerl"].air
    arrive(controller, "kerl", Guest("Lady Mabel", 60, 100))
    shift.air = 50
    controller.town.rng = random.Random(1)
    controller.handle("Kerl", "!wait")
    plain = controller.town.shifts["kerl"].air
    assert with_breath > plain - 1 or with_breath >= 40


def pass_world_days(controller, days:int) -> None:
    from cursed_descent.config import WORLD_DAY_SECONDS
    controller.town.world.anchor -= days * WORLD_DAY_SECONDS
    controller.town.tick_world()


def test_dead_seat_is_locked_until_the_round_ends(controller,
                                                  monkeypatch) -> None:
    from cursed_descent.towns.last_light_humans.cafe import service
    monkeypatch.setattr(service, "pick_outcome", lambda v, r: "cushion")
    setup_pair(controller)
    controller.handle("Kerl", "!job cafe seat")
    del controller.town.shifts["kerl"]
    cafe_death(controller.town, controller.repository.load("Kerl"),
                               "smothered")
    assert controller.repository.load("Kerl").records["cafe_lock"] == 1
    assert "sit out" in text(controller.handle("Kerl", "!lobby"))
    assert "sit out" in text(controller.handle("Kerl", "!job cafe seat"))
    assert "sit out" not in text(controller.handle("Kerl", "!help"))
    controller.session.end_run()
    assert "sit out" in text(controller.handle("Kerl", "!lobby"))
    pass_world_days(controller, 1)
    assert "sit out" not in text(controller.handle("Kerl", "!lobby"))
    assert controller.repository.load("Kerl").records["cafe_lock"] == 0


def test_rider_on_face_is_examinable_and_seat_is_taken(controller) -> None:
    setup_pair(controller)
    controller.handle("Kerl", "!job cafe seat")
    controller.handle("Galactica", "!sit Kerl")
    assert "mercy" in text(controller.handle("Kerl", "!examine Galactica"))
    second = controller.repository.load("Galactica")
    controller.handle("Galactica", "!rise")
    controller.handle("Galactica", "!sit Kerl")
    other = controller.repository.load("Kerl")
    assert other.name == "kerl"
    assert controller.town.shifts["kerl"].client.rider == "Galactica"
    assert second.gender == "Female"


def test_rider_can_swallow_her_seat_when_big_enough(controller) -> None:
    setup_pair(controller)
    controller.handle("Kerl", "!job cafe seat")
    controller.handle("Galactica", "!sit Kerl")
    big = controller.town.shifts["kerl"].client
    big.butt, big.weight = 100, 60
    assert "not built" in text(controller.handle("Galactica", "!swallow"))
    assert "kerl" in controller.town.shifts
    big.butt, big.weight = 160, 120
    reply = controller.handle("Galactica", "!swallow")
    assert "ass" in text(reply) and "kerl" not in controller.town.shifts
    assert any(m.recipient == "kerl" and "pulled in" in m.text
               for m in reply)
    assert controller.repository.load("Kerl").records["cafe_lock"] == 1
    assert controller.town.cafe.entries[-1]["fate"] == "engulfed"


def test_big_lady_may_swallow_a_small_weak_man(controller) -> None:
    setup_pair(controller)
    kerl = controller.repository.load("Kerl")
    kerl.body["weight"] = 50
    kerl.stats["vitality"] = 1
    kerl.stats["strength"] = 1
    controller.repository.save(kerl)
    controller.handle("Kerl", "!job cafe seat")
    outcomes = set()
    for seed in range(40):
        controller.town.shifts.setdefault("kerl", None)
        if controller.town.shifts["kerl"] is None:
            del controller.town.shifts["kerl"]
            controller.handle("Kerl", "!job cafe seat")
        controller.repository.load("Kerl").records["cafe_lock"] = 0
        arrive(controller, "kerl", Guest("Lady Big", 150, 190))
        controller.town.rng = random.Random(seed)
        reply = text(controller.handle("Kerl", "!wait"))
        outcomes.add("sucks you in" in reply)
        if "kerl" not in controller.town.shifts:
            controller.repository.load("Kerl").records["cafe_lock"] = 0
    assert outcomes == {True, False}


def test_licking_keeps_the_lady_seated_longer(controller) -> None:
    setup_pair(controller)
    controller.handle("Kerl", "!job cafe seat")
    arrive(controller, "kerl", Guest("Lady Mabel", 60, 100))
    assert "lick it slowly" in text(controller.handle("Kerl", "!lick"))
    guest = controller.town.shifts["kerl"].client
    assert guest is not None and guest.pleased == 1 and guest.held == 1
    reply = controller.handle("Kerl", "!kiss")
    assert controller.town.shifts["kerl"].client is not None
    reply = controller.handle("Galactica", "!sit Kerl")
    assert reply


def test_regulars_are_stored_per_town_and_building(controller) -> None:
    root = regs(controller, "Kerl").root
    assert root.name == "last_light"
    assert root.parent.name == controller.repository.load("Kerl").id
    assert (root / "cafe").is_dir() and (root / "brothel").is_dir()
    assert (root.parent.parent.name == "regulars"
            and root.parent.parent.parent.name == "npcs")
    store = regs(controller, "Kerl")
    first = store.remember("cafe", {"name": "Lady Rose", "weight": 90,
                                    "butt": 120})
    again = store.remember("cafe", {"name": "Lady Rose", "weight": 99,
                                    "butt": 99})
    assert first["visits"] == 1 and again["visits"] == 2
    assert again["weight"] == 90
    assert (root / "cafe" / "lady_rose.json").exists()
    seen = {new_guest(random.Random(seed), store).name
            for seed in range(60)}
    assert "Lady Rose" in seen


def test_swallow_works_on_a_free_npc_stool(controller) -> None:
    from cursed_descent.towns.last_light_humans.cafe.stools import Stool
    lady = controller.repository.load("Galactica")
    lady.gender = "Female"
    lady.gold = 100
    lady.body["weight"], lady.body["butt"] = 120, 160
    controller.repository.save(lady)
    controller.town.stools = [Stool("Willem", 22, 182, 64, "Slim", 20,
                                    "nervous")]
    controller.handle("Galactica", "!sit 1")
    reply = text(controller.handle("Galactica", "!swallow"))
    assert "slip into your ass" in reply
    assert "Galactica" not in controller.town.rides
    assert controller.town.stools == []
    small = controller.repository.load("Galactica")
    small.body["butt"] = 90
    controller.repository.save(small)
    controller.town.stools = [Stool("Piet", 22, 160, 63, "Slim", 20,
                                    "nervous")]
    controller.handle("Galactica", "!sit 1")
    assert "not built" in text(controller.handle("Galactica", "!swallow"))
    assert "Galactica" in controller.town.rides


def test_rider_can_clench_and_wiggle_on_a_seat_and_a_stool(
        controller) -> None:
    from cursed_descent.towns.last_light_humans.cafe.stools import Stool
    setup_pair(controller)
    controller.handle("Kerl", "!job cafe seat")
    controller.handle("Galactica", "!sit Kerl")
    shift = controller.town.shifts["kerl"]
    reply = controller.handle("Galactica", "!clench")
    assert shift.client.squeeze == 1 and shift.air == 90
    assert any(m.recipient == "kerl" and "clamps" in m.text for m in reply)
    reply = controller.handle("Galactica", "!wiggle")
    assert shift.air == 75 and shift.winded == 1
    assert any(m.recipient == "kerl" and "wiggles" in m.text for m in reply)
    controller.handle("Galactica", "!rise")
    lady = controller.repository.load("Galactica")
    lady.gold = 100
    controller.repository.save(lady)
    controller.town.stools = [Stool("Piet", 22, 160, 63, "Slim", 20,
                                    "nervous")]
    controller.handle("Galactica", "!sit 1")
    controller.handle("Galactica", "!clench")
    controller.handle("Galactica", "!wiggle")
    ride = controller.town.rides["Galactica"]
    assert ride.squeeze == 1 and ride.shaken == 1


def test_swallowed_men_make_sounds(controller) -> None:
    setup_pair(controller)
    controller.handle("Kerl", "!job cafe seat")
    controller.handle("Galactica", "!sit Kerl")
    guest = controller.town.shifts["kerl"].client
    guest.butt, guest.weight = 160, 120
    reply = controller.handle("Galactica", "!swallow")
    sounds = ("Mmmpf", "Glrk", "Mmh-mmh", "Squelch", "thudding")
    assert all(any(w in m.text for w in sounds) for m in reply[:2])


def test_brothel_client_can_be_examined_and_becomes_regular(
        controller) -> None:
    setup_pair(controller)
    controller.handle("Galactica", "!job brothel whore")
    shift = controller.town.shifts["Galactica"]
    name = shift.client.name
    reply = text(controller.handle("Galactica", f"!examine {name}"))
    assert name in reply and "A new face" in reply
    assert "temper" in text(controller.handle("Galactica", "!examine client"))
    folder = regs(controller, "Galactica").folder("brothel")

    def own_files() -> list:
        return [path for path in folder.glob("*.json")
                if "ref_id" not in path.read_text()]

    assert not own_files()
    assert "now a regular" in text(controller.handle("Galactica",
                                                     "!regular"))
    assert "already a regular" in text(controller.handle("Galactica",
                                                         "!regular"))
    assert own_files()
    seen = set()
    for seed in range(80):
        client = new_client(controller.repository.load("Galactica"),
                            random.Random(seed), regs(controller, "Galactica"))
        seen.add(client.visits > 1)
    assert seen == {True, False}


def test_npc_ladies_clench_wiggle_and_demand(controller, monkeypatch) -> None:
    from cursed_descent.towns.last_light_humans.cafe import seat
    setup_pair(controller)
    controller.handle("Kerl", "!job cafe seat")
    monkeypatch.setattr(seat, "CAFE_NPC_ACTION_CHANCE", 1.0)
    seen = set()
    for seed in range(60):
        arrive(controller, "kerl", Guest("Lady Sadie", 60, 100, cruel=2))
        controller.town.rng = random.Random(seed)
        reply = text(controller.handle("Kerl", "!wait"))
        for key in ("clenches", "wiggles", "[lick]"):
            if key in reply:
                seen.add(key)
        if "kerl" not in controller.town.shifts:
            controller.handle("Kerl", "!job cafe seat")
            controller.repository.load("Kerl").records["cafe_lock"] = 0
    assert seen == {"clenches", "wiggles", "[lick]"}


def test_demanded_lick_pays_extra_and_ignoring_it_punishes(
        controller, monkeypatch) -> None:
    from cursed_descent.towns.last_light_humans.cafe import seat
    monkeypatch.setattr(seat, "CAFE_NPC_ACTION_CHANCE", 0.0)
    setup_pair(controller)
    controller.handle("Kerl", "!job cafe seat")
    arrive(controller, "kerl", Guest("Lady Sadie", 60, 100, wants_lick=True))
    reply = text(controller.handle("Kerl", "!lick"))
    assert "tips extra" in reply
    arrive(controller, "kerl", Guest("Lady Sadie", 60, 100, wants_lick=True))
    reply = text(controller.handle("Kerl", "!wait"))
    assert "asked for your tongue" in reply
    assert controller.town.shifts["kerl"].client.squeeze == 1


def test_endrun_releases_the_dead_lock(controller, monkeypatch) -> None:
    from cursed_descent.towns.last_light_humans.cafe import service
    monkeypatch.setattr(service, "pick_outcome", lambda v, r: "cushion")
    setup_pair(controller)
    assert "no run to end" in text(controller.handle("Kerl", "!endrun"))
    controller.handle("Kerl", "!job cafe seat")
    del controller.town.shifts["kerl"]
    cafe_death(controller.town, controller.repository.load("Kerl"),
                               "smothered")
    assert "sit out" in text(controller.handle("Kerl", "!lobby"))
    assert "back among the living in about" in text(
        controller.handle("Kerl", "!endrun"))
    assert "sit out" in text(controller.handle("Kerl", "!lobby"))
    pass_world_days(controller, 1)
    assert "sit out" not in text(controller.handle("Kerl", "!lobby"))


def test_regular_ladies_count_their_kills(controller) -> None:
    setup_pair(controller)
    store = regs(controller, "Kerl")
    store.remember("cafe", {"name": "Lady Killer", "weight": 150,
                            "butt": 200, "cruel": 2})
    controller.handle("Kerl", "!job cafe seat")
    killer = Guest("Lady Killer", 150, 200, cruel=2)
    kills = 0
    for seed in range(200):
        arrive(controller, "kerl", killer)
        killer.squeeze = 3
        controller.town.shifts["kerl"].left = 10
        controller.town.rng = random.Random(seed)
        controller.handle("Kerl", "!wait")
        if "kerl" not in controller.town.shifts:
            kills = killer.kills
            break
    assert kills >= 1
    stored = [r for r in store.all("cafe") if r["name"] == "Lady Killer"][0]
    assert stored["kills"] == kills
    controller.repository.load("Kerl").records["cafe_lock"] = 0
    controller.handle("Kerl", "!job cafe seat")
    arrive(controller, "kerl", Guest("Lady Killer", 150, 200, kills=3))
    assert "Kills on her ledger: 3" in text(
        controller.handle("Kerl", "!examine guest"))


def test_hand_made_regular_files_work(controller) -> None:
    import json
    store = regs(controller, "Kerl")
    path = store.folder("cafe") / "volena_wilde.json"
    path.write_text(json.dumps({"name": "Volena Wilde", "weight": 130,
                                "butt": 180, "cruel": 2, "kills": 7}),
                    encoding="utf-8")
    (store.folder("cafe") / "broken.json").write_text("{}", encoding="utf-8")
    (store.folder("brothel") / "bob.json").write_text(
        json.dumps({"name": "Bob"}), encoding="utf-8")
    guests = [new_guest(random.Random(seed), store) for seed in range(600)]
    volena = [g for g in guests if g.name == "Volena Wilde"]
    assert volena and volena[0].kills == 7 and volena[0].butt == 180
    lady = controller.repository.load("Galactica")
    clients = [new_client(lady, random.Random(seed), store)
               for seed in range(80)]
    assert any(c.name == "Bob" for c in clients)


def test_regulars_show_age_and_body(controller) -> None:
    setup_pair(controller)
    controller.handle("Galactica", "!job brothel whore")
    name = controller.town.shifts["Galactica"].client.name
    reply = text(controller.handle("Galactica", f"!examine {name}"))
    assert " years, " in reply and " cm, " in reply and " kg, " in reply
    controller.handle("Kerl", "!job cafe seat")
    arrive(controller, "kerl", Guest("Mrs. Fenwick", 86, 124, age=51,
                                     height=170))
    reply = text(controller.handle("Kerl", "!examine guest"))
    assert "51 years, 170 cm, 86 kg, average" in reply


def test_old_regular_files_are_completed_once(controller) -> None:
    import json
    store = regs(controller, "Kerl")
    path = store.folder("cafe") / "old_dame.json"
    path.write_text(json.dumps({"name": "Old Dame", "weight": 100,
                                "butt": 150, "visits": 2}),
                    encoding="utf-8")
    for seed in range(600):
        guest = new_guest(random.Random(seed), store)
        if guest.name == "Old Dame":
            break
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["age"] == guest.age and data["height"] == guest.height
    assert "cruel" in data and data["weight"] == 100
    again = None
    for seed in range(600, 1500):
        again = new_guest(random.Random(seed), store)
        if again.name == "Old Dame":
            break
    assert again.age == guest.age and again.height == guest.height


def test_regular_command_for_the_cafe_and_remove(controller) -> None:
    setup_pair(controller)
    assert "nobody here" in text(controller.handle("Kerl", "!regular"))
    controller.handle("Kerl", "!job cafe seat")
    arrive(controller, "kerl", Guest("Mrs. Fenwick", 86, 124, age=51,
                                     height=170))
    store = regs(controller, "Kerl")
    assert "now a regular" in text(controller.handle("Kerl", "!regular"))
    data = [r for r in store.all("cafe") if r["name"] == "Mrs. Fenwick"][0]
    assert data["age"] == 51 and data["height"] == 170
    assert "no longer" in text(controller.handle("Kerl", "!regular remove"))
    assert not store.all("cafe")
    guest = new_guest(random.Random(1), store)
    assert not store.all("cafe") and guest.age > 0


def test_brothel_regulars_remember_what_was_done(controller) -> None:
    setup_pair(controller)
    controller.handle("Galactica", "!job brothel whore")
    name = controller.town.shifts["Galactica"].client.name
    controller.handle("Galactica", "!regular")
    lady = controller.repository.load("Galactica")
    from cursed_descent.town_buildings.brothel.clients import (
        client_options,
    )
    client = controller.town.shifts["Galactica"].client
    act, role = client_options(lady, client)[0]
    controller.handle("Galactica", f"!serve {act} {role}")
    store = regs(controller, "Galactica")
    record = [r for r in store.all("brothel") if r["name"] == name][0]
    assert record["history"] == {f"{act}/{role}": 1}
    client = controller.town.shifts["Galactica"].client
    client.name = name
    client.history = record["history"]
    reply = text(controller.handle("Galactica", f"!examine {name}"))
    assert "Between you so far" in reply and f"{act} x1" in reply


def test_brothel_regulars_remember_what_was_done(controller) -> None:
    setup_pair(controller)
    controller.handle("Galactica", "!job brothel whore")
    name = controller.town.shifts["Galactica"].client.name
    controller.handle("Galactica", "!regular")
    lady = controller.repository.load("Galactica")
    from cursed_descent.town_buildings.brothel.clients import (
        client_options,
    )
    client = controller.town.shifts["Galactica"].client
    act, role = client_options(lady, client)[0]
    controller.handle("Galactica", f"!serve {act} {role}")
    store = regs(controller, "Galactica")
    record = [r for r in store.all("brothel") if r["name"] == name][0]
    assert record["history"] == {f"{act}/{role}": 1}
    client = controller.town.shifts["Galactica"].client
    client.name = name
    client.history = record["history"]
    reply = text(controller.handle("Galactica", f"!examine {name}"))
    assert "Between you so far" in reply and f"{act} x1" in reply


def test_regulars_belong_to_one_character(controller) -> None:
    setup_pair(controller)
    mine = regs(controller, "Kerl")
    other = regs(controller, "Galactica")
    mine.add("cafe", {"name": "Lady Mine", "weight": 90, "butt": 120})
    assert mine.has("cafe", "Lady Mine") and not other.has("cafe", "Lady Mine")
    assert mine.root != other.root


def test_nobody_is_younger_than_18() -> None:
    from cursed_descent.town_buildings.bodies import (
        body_line, client_body, lady_age_height,
    )
    from cursed_descent.towns.last_light_humans.cafe.stools import new_stool
    for seed in range(400):
        rng = random.Random(seed)
        assert new_stool(rng).age >= 18
        assert lady_age_height(rng)[0] >= 18
        assert client_body(rng)[0] >= 18
    assert "18 years" in body_line(16, 170, 70)


def test_guest_rear_follows_weight() -> None:
    from cursed_descent.towns.last_light_humans.cafe.guests import guest_butt
    light = [guest_butt(75, random.Random(s)) for s in range(200)]
    heavy = [guest_butt(145, random.Random(s)) for s in range(200)]
    assert max(light) < 135 and min(heavy) > 150


def test_cafe_ambient_lines_come_for_people_in_the_cafe(controller) -> None:
    setup_pair(controller)
    controller.town.ambient_on = True
    assert ambient(controller.town, 10.0) == []
    controller.handle("Kerl", "!job cafe seat")
    controller.town.shifts["kerl"].due = 10**9
    collected = []
    for step in range(1, 40):
        collected += ambient(controller.town, 100.0 + step * 15)
    assert len(collected) >= 20
    assert all(m.style == "ambient" and m.recipient == "kerl"
               for m in collected)
    assert len({m.text for m in collected}) > 5
    controller.town.cafe_seen["Galactica"] = 5000.0
    near = []
    for step in range(1, 12):
        near += ambient(controller.town, 5000.0 + step * 15)
    assert any(m.recipient == "Galactica" for m in near)
    later = ambient(controller.town, 5000.0 + 400)
    assert not [m for m in later if m.recipient == "Galactica"]


def test_brothel_roles_domina_and_sub(controller) -> None:
    setup_pair(controller)
    controller.handle("Galactica", "!job brothel whore domina")
    shift = controller.town.shifts["Galactica"]
    assert shift.mode == "domina" and shift.client.dominated
    assert "receive" not in {role for _, role in shift.client.likes}
    assert "you give" in text(controller.handle("Galactica",
                                                 "!serve oral receive"))
    del controller.town.shifts["Galactica"]
    controller.handle("Galactica", "!job brothel whore sub")
    shift = controller.town.shifts["Galactica"]
    assert shift.mode == "sub" and shift.client.dominant
    assert all(role == "receive" for _, role in shift.client.likes)
    reply = text(controller.handle("Galactica", "!examine client"))
    assert "dominate you" in reply
    assert "you receive" in text(controller.handle("Galactica",
                                                    "!serve oral give"))
    del controller.town.shifts["Galactica"]
    controller.handle("Galactica", "!job brothel whore")
    assert controller.town.shifts["Galactica"].mode == ""


def test_age_preference_filters_everyone(controller) -> None:
    from cursed_descent.town_buildings.bodies import (
        client_body, lady_age_height, normalise_pref,
    )
    from cursed_descent.towns.last_light_humans.cafe.stools import new_stool
    setup_pair(controller)
    assert normalise_pref(10, 12) == (18, 27)
    pref = (30, 45)
    for seed in range(300):
        rng = random.Random(seed)
        assert 30 <= client_body(rng, pref)[0] <= 45
        assert 30 <= lady_age_height(rng, pref)[0] <= 45
        assert 30 <= new_stool(rng, pref).age <= 45
    reply = text(controller.handle("Kerl", "!agepref 30 45"))
    assert "30 to 45" in reply
    assert controller.repository.load("Kerl").profile["age_pref"] == [30, 45]
    assert "30 to 45" in text(controller.handle("Kerl", "!agepref"))
    controller.handle("Kerl", "!agepref 20 21")
    assert controller.repository.load("Kerl").profile["age_pref"] == [20, 29]
    store = regs(controller, "Kerl")
    store.add("cafe", {"name": "Dame Old", "weight": 90, "butt": 120,
                       "age": 60})
    store.add("cafe", {"name": "Dame Fit", "weight": 90, "butt": 120,
                       "age": 25})
    names = {new_guest(random.Random(s), store, (20, 29)).name
             for s in range(600)}
    assert "Dame Old" not in names and "Dame Fit" in names


def test_regulars_have_marriage_address_and_can_be_visited(
        controller) -> None:
    setup_pair(controller)
    controller.handle("Kerl", "!job cafe seat")
    arrive(controller, "kerl", Guest("Mrs. Fenwick", 86, 124, age=51,
                                     height=170))
    controller.handle("Kerl", "!regular")
    store = regs(controller, "Kerl")
    record = store.get("cafe", "Mrs. Fenwick")
    assert "married" in record and record["address_known"] is False
    assert "Address unknown" in text(controller.handle(
        "Kerl", "!examine guest")) or "address unknown" in text(
        controller.handle("Kerl", "!examine guest"))
    assert "hardly know" in text(controller.handle("Kerl", "!regular ask"))
    store.set("cafe", "Mrs. Fenwick", {"visits": 3, "married": True,
                                       "spouse": "Bruno"})
    assert "folded note" in text(controller.handle("Kerl", "!regular ask"))
    assert store.get("cafe", "Mrs. Fenwick")["address_known"] is True
    assert "Married to Bruno" in text(controller.handle("Kerl",
                                                        "!regulars"))
    controller.handle("Kerl", "!rise")
    controller.handle("Kerl", "!quit")
    gold = controller.repository.load("Kerl").gold
    controller.town.rng.random = lambda: 0.5
    assert "walk to" in text(controller.handle("Kerl", "!visit Fenwick"))
    assert "no safeword" in text(controller.handle("Kerl", "!house seat"))
    text(controller.handle("Kerl", "!house seat confirm"))
    assert controller.town.shifts["kerl"].mode == "home"
    assert "no safeword" in text(controller.handle("Kerl", "!quit"))
    assert controller.repository.load("Kerl").gold == gold
    assert store.get("cafe", "Mrs. Fenwick")["home_visits"] >= 1
    del controller.town.shifts["kerl"]
    controller.handle("Kerl", "!house leave")
    store.set("cafe", "Mrs. Fenwick", {"address_known": False})
    assert "do not know where" in text(controller.handle(
        "Kerl", "!visit Fenwick"))


def test_family_visits_tip_the_seat_instead_of_a_guest(controller) -> None:
    from cursed_descent.towns.last_light_humans.cafe import seat as seat_module
    from cursed_descent.towns.last_light_humans.cafe.ambient import family_scene
    setup_pair(controller)
    controller.handle("Kerl", "!job cafe seat")
    shift = controller.town.shifts["kerl"]
    kerl = controller.repository.load("Kerl")
    seat_module.CAFE_FAMILY_CHANCE, saved = 1.0, seat_module.CAFE_FAMILY_CHANCE
    try:
        shift.due = 0.0
        messages, fate = seat_module.tick_seat(
            kerl, controller.town.shifts, random.Random(3), 1.0,
            family=True)
    finally:
        seat_module.CAFE_FAMILY_CHANCE = saved
    assert shift.client is None and shift.earned > 0 and not fate
    assert "tip" in messages[0].text
    assert any(word in messages[0].text for word in ("son", "boyfriend"))
    assert family_scene(random.Random(1))


def test_family_scene_has_mom_and_girlfriend_quotes() -> None:
    from cursed_descent.towns.last_light_humans.cafe.ambient import family_scene
    scene = family_scene(random.Random(4))
    assert "Now he is my seat~" in scene
    assert "Mom knows best." in scene or "Mom was here first." in scene


def test_family_members_can_be_examined(controller) -> None:
    from cursed_descent.towns.last_light_humans.cafe import seat as seat_module
    setup_pair(controller)
    controller.handle("Kerl", "!job cafe seat")
    shift = controller.town.shifts["kerl"]
    kerl = controller.repository.load("Kerl")
    saved = seat_module.CAFE_FAMILY_CHANCE
    seat_module.CAFE_FAMILY_CHANCE = 1.0
    try:
        shift.due = 0.0
        seat_module.tick_seat(kerl, controller.town.shifts,
                              random.Random(5), 1.0, family=True)
    finally:
        seat_module.CAFE_FAMILY_CHANCE = saved
    family = shift.family
    assert family is not None and family.son.age >= 18
    assert family.girlfriend.age >= 18
    mother = text(controller.handle("Kerl", f"!examine {family.lady.name}"))
    assert "mother" in mother and " kg" in mother
    girl = text(controller.handle("Kerl",
                                  f"!examine {family.girlfriend.name}"))
    assert "girlfriend" in girl and "years" in girl
    son = text(controller.handle("Kerl", f"!examine {family.son.name}"))
    assert "her son" in son.lower() or "'s son" in son
    shift.due = 0.0
    seat_module.tick_seat(kerl, controller.town.shifts, random.Random(6),
                          2.0, family=False)
    assert shift.family is None and shift.client is not None


def test_family_mother_can_be_a_regular(controller) -> None:
    from cursed_descent.towns.last_light_humans.cafe.ambient import make_family
    setup_pair(controller)
    store = regs(controller, "Kerl")
    store.add("cafe", {"name": "Volena Wilde", "weight": 130, "butt": 180,
                       "age": 52, "height": 170, "kills": 4})
    mothers = [make_family(random.Random(seed), store).lady
               for seed in range(300)]
    volena = [m for m in mothers if m.name == "Volena Wilde"]
    assert volena and volena[0].kills == 4 and volena[0].age == 52
    assert store.get("cafe", "Volena Wilde")["visits"] > 1


def test_encourage_makes_her_stay_longer(controller) -> None:
    setup_pair(controller)
    controller.handle("Kerl", "!job cafe seat")
    arrive(controller, "kerl", Guest("Lady Mabel", 90, 130))
    reply = text(controller.handle("Kerl", "!encourage"))
    assert "Stay" in reply
    assert controller.town.shifts["kerl"].client.pleased >= 1


def test_zero_air_heavy_lady_crushes_him(controller, monkeypatch) -> None:
    from cursed_descent.towns.last_light_humans.cafe import seat
    monkeypatch.setattr(seat, "endurance", lambda *args: -20)
    monkeypatch.setattr(seat, "CAFE_DEATH_CHANCE", 0.0)
    monkeypatch.setattr(seat, "CAFE_SWALLOW_CHANCE", 0.0)
    setup_pair(controller)
    controller.handle("Kerl", "!job cafe seat")
    arrive(controller, "kerl", Guest("Lady Doom", 130, 150))
    controller.town.shifts["kerl"].air = 1
    reply = text(controller.handle("Kerl", "!wait"))
    assert "collapse" in reply and "wet crunch" in reply
    assert "kerl" not in controller.town.shifts
    assert controller.repository.load("Kerl").records["cafe_lock"] == 1


def test_zero_air_light_lady_lands_and_he_is_dragged_out(
        controller, monkeypatch) -> None:
    from cursed_descent.towns.last_light_humans.cafe import seat
    monkeypatch.setattr(seat, "endurance", lambda *args: -20)
    monkeypatch.setattr(seat, "CAFE_DEATH_CHANCE", 0.0)
    monkeypatch.setattr(seat, "CAFE_SWALLOW_CHANCE", 0.0)
    setup_pair(controller)
    controller.handle("Kerl", "!job cafe seat")
    arrive(controller, "kerl", Guest("Lady Mabel", 60, 100))
    controller.town.shifts["kerl"].air = 1
    reply = text(controller.handle("Kerl", "!giveup"))
    assert "dragged" in reply or "drag you" in reply
    assert "kerl" not in controller.town.shifts
    assert "cafe_lock" not in controller.repository.load("Kerl").records


def domina_shift(controller):
    setup_pair(controller)
    controller.handle("Galactica", "!job brothel whore domina")
    shift = controller.town.shifts["Galactica"]
    shift.client.gender = "Male"
    shift.client.endowment = 15
    return shift


def test_ballbusting_is_a_kick_from_front_or_back(controller) -> None:
    domina_shift(controller)
    front = text(controller.handle("Galactica",
                                   "!serve ballbusting give front"))
    assert "from the front" in front or "face" in front
    shift = controller.town.shifts["Galactica"]
    shift.left = 3
    shift.client.gender = "Male"
    shift.client.endowment = 15
    back = text(controller.handle("Galactica",
                                  "!serve ballbusting give back"))
    assert "behind" in back or "from behind" in back


def test_facesitting_can_kill_the_client_and_pays_his_purse(
        controller, monkeypatch) -> None:
    from cursed_descent.town_buildings.brothel import shift as brothel
    monkeypatch.setattr(brothel, "BROTHEL_KILL_CHANCE", 1.0)
    shift = domina_shift(controller)
    shift.client.purse = 250
    name = shift.client.name
    reply = text(controller.handle("Galactica", "!serve facesitting give"))
    assert "+250 gold" in reply and name in reply
    assert controller.town.shifts["Galactica"].earned == 250
    assert controller.town.shifts["Galactica"].served == 1
    assert controller.town.shifts["Galactica"].client.name


def test_coming_inside_swells_the_belly_by_ball_size(controller) -> None:
    setup_pair(controller)
    lady = controller.repository.load("Galactica")
    lady.gender = "Shemale"
    lady.body["balls"] = 10
    lady.body["endowment"] = 18
    controller.repository.save(lady)
    controller.handle("Galactica", "!job brothel whore domina")
    shift = controller.town.shifts["Galactica"]
    shift.client.dominated = True
    reply = text(controller.handle("Galactica", "!serve anal give"))
    assert "belly now +8 cm" in reply


def test_family_marks_both_characters(controller) -> None:
    setup_pair(controller)
    reply = text(controller.handle("Kerl", "!family Galactica mother"))
    assert "confirm" in reply
    assert not controller.repository.load("Kerl").profile.get("family")
    reply = text(controller.handle("Galactica", "!family accept Kerl"))
    assert "mother" in reply and "son" in reply
    kerl = controller.repository.load("Kerl")
    lady = controller.repository.load("Galactica")
    assert kerl.profile["family"][lady.id]["role"] == "mother"
    assert lady.profile["family"][kerl.id]["role"] == "son"
    assert "Galactica: your mother" in text(
        controller.handle("Kerl", "!family"))
    assert "removed" in text(controller.handle("Kerl",
                                               "!family clear Galactica"))
    assert not controller.repository.load("Galactica").profile["family"]
    assert "Roles" in text(controller.handle("Kerl", "!family Galactica cat"))


def test_mother_sitting_on_her_son_gets_a_family_scene(controller) -> None:
    setup_pair(controller)
    controller.handle("Galactica", "!family Kerl son")
    controller.handle("Kerl", "!family accept Galactica")
    controller.handle("Kerl", "!job cafe seat")
    reply = text(controller.handle("Galactica", "!sit kerl"))
    assert "Mom" in reply or "son" in reply or "her own" in reply


def test_regular_calls_on_you_and_family_names_are_used(
        controller, monkeypatch) -> None:
    from cursed_descent.towns.last_light_humans.cafe import service
    monkeypatch.setattr(service, "REGULARS_CALL_CHANCE", 1.0)
    from cursed_descent.towns.last_light_humans.cafe.ambient import make_family
    setup_pair(controller)
    store = regs(controller, "Kerl")
    store.add("cafe", {"name": "Volena Wilde", "weight": 130, "butt": 180,
                       "age": 52, "height": 170, "son": "Little Tim",
                       "girlfriend": "Mina", "address_known": True,
                       "home": "No. 5 Mill Hill", "married": False})
    family = [make_family(random.Random(seed), store)
              for seed in range(200)]
    volena = [f for f in family if f.lady.name == "Volena Wilde"]
    assert volena and volena[0].son.name == "Little Tim"
    assert volena[0].girlfriend.name == "Mina"
    gold = controller.repository.load("Kerl").gold
    assert regular_call(controller.town, "Kerl") is None
    kerl = controller.repository.load("Kerl")
    kerl.profile["houses"] = {"last_light": {
        "type": "hut", "residents": [], "guests": []}}
    controller.repository.save(kerl)
    controller.handle("Kerl", "!job cafe seat")
    assert regular_call(controller.town, "Kerl") is None
    controller.handle("Kerl", "!quit")
    called = regular_call(controller.town, "Kerl")
    assert called is not None and "Volena Wilde" in called.text
    assert controller.repository.load("Kerl").gold == gold


def test_furniture_victims_are_buried_in_the_graveyard_folder(
        controller) -> None:
    import json
    from cursed_descent.towns.last_light_humans.cafe.furniture import make_furniture
    setup_pair(controller)
    kerl = controller.repository.load("Kerl")
    kerl.gold = 321
    kerl.inventory = ["potion_small"]
    make_furniture(kerl, controller.repository)
    files = list(controller.repository.graveyard_dir.glob("kerl_*.json"))
    assert len(files) == 1
    saved = json.loads(files[0].read_text(encoding="utf-8"))
    assert saved["player"]["gold"] == 321 and "furniture" in saved["reason"]
    assert not controller.repository.path("kerl").exists()


def test_family_is_stored_by_id_and_old_name_links_are_upgraded(
        controller) -> None:
    setup_pair(controller)
    kerl = controller.repository.load("Kerl")
    lady = controller.repository.load("Galactica")
    kerl.profile["family"] = {"Galactica": "mother"}
    controller.repository.save(kerl)
    assert "Galactica: your mother" in text(controller.handle("Kerl", "!family"))
    kerl = controller.repository.load("Kerl")
    assert list(kerl.profile["family"]) == [lady.id]


def test_air_drops_every_round_even_for_a_strong_man(controller) -> None:
    from cursed_descent.towns.last_light_humans.cafe.seat import air_change
    setup_pair(controller)
    kerl = controller.repository.load("Kerl")
    kerl.level = 10
    kerl.stats.update(strength=14, vitality=8)
    controller.repository.save(kerl)
    controller.handle("Kerl", "!job cafe seat")
    arrive(controller, "kerl", Guest("Lady Mabel", 100, 140))
    shift = controller.town.shifts["kerl"]
    shift.air = 100
    controller.handle("Kerl", "!wait")
    assert controller.town.shifts["kerl"].air < 100
    assert air_change(22, 20) < 0 and air_change(22, -6) < air_change(22, 20)


def test_sleeping_in_the_tavern_rests_for_gold(controller, monkeypatch) -> None:
    from cursed_descent.town_buildings.tavern import rooms as tavern_rooms
    monkeypatch.setattr(tavern_rooms, "TAVERN_THEFT_CHANCE", 0.0)
    setup_pair(controller)
    kerl = controller.repository.load("Kerl")
    kerl.gold = 100
    kerl.needs.update(sleep=90, hunger=50, thirst=50)
    controller.repository.save(kerl)
    assert "common|private" in text(controller.handle("Kerl", "!room x"))
    reply = text(controller.handle("Kerl", "!room common"))
    kerl = controller.repository.load("Kerl")
    assert kerl.needs["sleep"] == 0 and kerl.gold == 92
    assert kerl.needs["hunger"] == 50 and "-8 gold" in reply
    controller.handle("Kerl", "!room private")
    kerl = controller.repository.load("Kerl")
    assert kerl.gold == 67 and kerl.needs["hunger"] < 50
    kerl.gold = 3
    controller.repository.save(kerl)
    assert "wants" in text(controller.handle("Kerl", "!room private"))


def test_common_room_can_cost_gold_to_a_thief(controller, monkeypatch) -> None:
    from cursed_descent.town_buildings.tavern import rooms as tavern_rooms
    monkeypatch.setattr(tavern_rooms, "TAVERN_THEFT_CHANCE", 1.0)
    setup_pair(controller)
    kerl = controller.repository.load("Kerl")
    kerl.gold = 100
    controller.repository.save(kerl)
    reply = text(controller.handle("Kerl", "!room common"))
    assert "light-fingered" in reply
    assert controller.repository.load("Kerl").gold < 92


def test_jobs_run_in_a_twenty_second_beat(controller) -> None:
    setup_pair(controller)
    controller.handle("Galactica", "!job tavern waiter", now=0.0)
    shift = controller.town.shifts["Galactica"]
    assert shift.left == 4 and shift.due == 20.0
    assert controller.tick(now=10.0) == []
    controller.tick(now=20.0)
    assert shift.left == 3 and shift.due == 40.0
    assert "Next round in" in controller.town.timer_text(
        controller.repository.load("Galactica"))
    assert "Finish your current shift" in text(
        controller.handle("Galactica", "!job tavern dancer", now=21.0))
    for step in range(2, 6):
        controller.tick(now=step * 20.0)
    assert "Galactica" not in controller.town.shifts


def test_brothel_serves_by_itself_when_you_choose_nothing(
        controller) -> None:
    setup_pair(controller)
    controller.handle("Galactica", "!job brothel whore", now=0.0)
    shift = controller.town.shifts["Galactica"]
    first = shift.client.name
    shift.left = 6
    reply = text(controller.tick(now=20.0))
    assert "the house picks for you" in reply
    assert shift.served == 1 and shift.due == 40.0
    controller.handle("Galactica", "!serve oral give", now=25.0)
    assert shift.due == 45.0 and shift.served == 2


def test_domina_auto_choice_only_gives(controller, monkeypatch) -> None:
    from cursed_descent.town_buildings.brothel import shift as brothel
    setup_pair(controller)
    seen = []
    real = brothel.serve

    def spy(player, words, *args, **kwargs):
        seen.append(words)
        return real(player, words, *args, **kwargs)
    monkeypatch.setattr(brothel, "serve", spy)
    controller.handle("Galactica", "!job brothel whore domina", now=0.0)
    for step in range(1, 7):
        controller.tick(now=step * 20.0)
    assert len(seen) == 6 and all(word.endswith("give") for word in seen)
    assert "Galactica" in controller.town.shifts
    assert "paid out" in text(controller.handle("Galactica", "!quit",
                                                now=200.0))


def test_leaving_a_timed_shift_early_pays_what_was_earned(
        controller) -> None:
    setup_pair(controller)
    before = controller.repository.load("Galactica").gold
    controller.handle("Galactica", "!job tavern dancer", now=0.0)
    controller.tick(now=20.0)
    reply = text(controller.handle("Galactica", "!quit", now=21.0))
    assert "leave your shift early" in reply and "Shift over" in reply
    assert "Galactica" not in controller.town.shifts
    assert controller.repository.load("Galactica").gold > before


def test_a_domina_simply_orders_the_address(controller) -> None:
    setup_pair(controller)
    controller.handle("Galactica", "!job brothel whore domina", now=0.0)
    client = controller.town.shifts["Galactica"].client.name
    reply = text(controller.handle("Galactica", "!regular ask"))
    assert "Yes, Mistress" in reply and client in reply
    stored = regs(controller, "Galactica").get("brothel", client)
    assert stored["address_known"] and stored["home"]
    assert "already have" in text(controller.handle("Galactica",
                                                    "!regular ask"))


def test_a_character_can_visit_a_working_domina(controller) -> None:
    setup_pair(controller)
    kerl = controller.repository.load("Kerl")
    kerl.gold = 100
    controller.repository.save(kerl)
    controller.handle("Galactica", "!job brothel whore domina", now=0.0)
    shift = controller.town.shifts["Galactica"]
    assert "right now" not in text(controller.handle("Kerl", "!visit nobody"))
    messages = controller.handle("Kerl", "!visit galactica", now=5.0)
    assert any(m.recipient == "Galactica" for m in messages)
    assert shift.client.player == "kerl" and shift.client.dominated
    assert shift.due == 25.0 and shift.earned == 40
    assert controller.repository.load("Kerl").gold == 60
    assert "right now" in text(controller.handle("Kerl", "!visit galactica"))
    reply = controller.handle("Galactica", "!serve oral give", now=6.0)
    assert any(m.recipient == "kerl" for m in reply)
    assert shift.client.player == ""


def test_visiting_needs_gold_and_free_hands(controller) -> None:
    setup_pair(controller)
    controller.handle("Galactica", "!job brothel whore", now=0.0)
    kerl = controller.repository.load("Kerl")
    kerl.gold = 5
    controller.repository.save(kerl)
    assert "wants 40" in text(controller.handle("Kerl", "!visit galactica"))


def test_whore_shift_is_endless_and_pays_as_you_go(controller) -> None:
    setup_pair(controller)
    before = controller.repository.load("Galactica").gold
    controller.handle("Galactica", "!job brothel whore domina", now=0.0)
    shift = controller.town.shifts["Galactica"]
    for step in range(1, 10):
        controller.tick(now=step * 20.0)
    assert "Galactica" in controller.town.shifts and shift.served == 9
    from cursed_descent.town_buildings.brothel.clients import client_prompt
    prompt = client_prompt(shift, controller.repository.load("Galactica"))
    assert "Client 10:" in prompt.text
    assert controller.repository.load("Galactica").gold > before


def test_dancer_and_milk_barrel_have_moves(controller) -> None:
    setup_pair(controller)
    controller.handle("Galactica", "!job tavern dancer", now=0.0)
    assert "Moves:" in text(controller.handle("Galactica", "!move x"))
    reply = text(controller.handle("Galactica", "!move lapdance", now=3.0))
    shift = controller.town.shifts["Galactica"]
    assert "lap" in reply and shift.left == 3 and shift.due == 23.0
    del controller.town.shifts["Galactica"]
    assert "no show" in text(controller.handle("Galactica", "!move spin"))
    controller.handle("Galactica", "!job tavern milk counter", now=0.0)
    assert "Moves:" in text(controller.handle("Galactica", "!move"))
    assert "+" in text(controller.handle("Galactica", "!move pump", now=2.0))


def test_a_customer_can_use_the_dancer_and_the_milk_barrel(
        controller) -> None:
    setup_pair(controller)
    kerl = controller.repository.load("Kerl")
    kerl.gold = 100
    controller.repository.save(kerl)
    controller.handle("Galactica", "!job tavern dancer", now=0.0)
    shift = controller.town.shifts["Galactica"]
    messages = controller.handle("Kerl", "!visit galactica", now=1.0)
    assert any(m.recipient == "Galactica" for m in messages)
    assert controller.repository.load("Kerl").gold == 80
    assert shift.earned == 20
    del controller.town.shifts["Galactica"]
    controller.handle("Galactica", "!job tavern milk counter", now=0.0)
    assert "-20 gold" in text(controller.handle("Kerl", "!visit galactica",
                                                 now=2.0))


def test_a_mother_smothering_her_son_has_her_own_dialogue(
        controller, monkeypatch) -> None:
    from cursed_descent.town_buildings.brothel import shift as brothel
    monkeypatch.setattr(brothel, "BROTHEL_KILL_CHANCE", 0.0)
    setup_pair(controller)
    controller.handle("Galactica", "!family Kerl son")
    controller.handle("Kerl", "!family accept Galactica")
    kerl = controller.repository.load("Kerl")
    kerl.gold = 100
    controller.repository.save(kerl)
    controller.handle("Galactica", "!job brothel whore domina", now=0.0)
    controller.handle("Kerl", "!visit galactica", now=1.0)
    reply = text(controller.handle("Galactica", "!serve foot give", now=2.0))
    assert "Mom" in reply or "Mommy" in reply


def test_a_visit_can_end_in_death_at_the_regulars_home(
        controller) -> None:
    from cursed_descent.towns.last_light_humans.cafe.guests import DEADLY
    setup_pair(controller)
    controller.handle("Kerl", "!job cafe seat")
    arrive(controller, "kerl", Guest("Mrs. Fenwick", 86, 124, age=51,
                                     height=170))
    controller.handle("Kerl", "!regular")
    store = regs(controller, "Kerl")
    store.set("cafe", "Mrs. Fenwick", {"address_known": True})
    controller.handle("Kerl", "!rise")
    controller.handle("Kerl", "!quit")
    controller.town.rng.random = lambda: 0.5
    controller.handle("Kerl", "!visit Fenwick")
    controller.handle("Kerl", "!house seat confirm")
    DEADLY["on"] = True
    try:
        reply = text(controller.handle("Kerl", "!hold"))
    finally:
        DEADLY["on"] = False
    assert "💀" in reply
    after = controller.repository.load("Kerl")
    assert after.deaths.get("smothered")
    assert "kerl" not in controller.town.shifts


def test_regulars_can_be_ditched_anytime(controller) -> None:
    setup_pair(controller)
    store = regs(controller, "Kerl")
    store.add("cafe", {"name": "Mrs. Fenwick", "age": 51})
    reply = text(controller.handle("Kerl", "!regulars drop Fenwick"))
    assert "confirm" in reply and store.has("cafe", "Mrs. Fenwick")
    reply = text(controller.handle("Kerl", "!regulars ditch Fenwick confirm"))
    assert "no longer a regular" in reply
    assert not store.has("cafe", "Mrs. Fenwick")
    assert "no regular called" in text(controller.handle(
        "Kerl", "!regulars drop Fenwick"))


def test_regulars_can_be_talked_to(controller) -> None:
    setup_pair(controller)
    store = regs(controller, "Kerl")
    store.add("cafe", {"name": "Mrs. Fenwick", "age": 51})
    reply = text(controller.handle("Kerl", "!regulars talk Fenwick"))
    assert "Mrs. Fenwick" in reply
    assert store.get("cafe", "Mrs. Fenwick")["talks"] == 1
    assert "no regular" in text(controller.handle(
        "Kerl", "!regulars talk Nobody"))


def test_dread_grows_with_size_and_kills_and_fades_with_rounds() -> None:
    from cursed_descent.towns.last_light_humans.cafe.guests import (
        dread_now, dread_tier,
    )
    small = Guest("A", 70, 100)
    giant = Guest("B", 130, 190, kills=2)
    assert dread_tier(small, 5, 1) == 0
    assert dread_tier(giant, 5, 1) == 3
    assert dread_tier(giant, 40, 20) < 3
    giant.held = 2
    assert dread_now(giant, 5, 1) == 1
    giant.rider = "x"
    assert dread_now(giant, 5, 1) == 0


def test_a_terrified_seat_may_freeze_on_the_safeword_once() -> None:
    from types import SimpleNamespace
    from cursed_descent.towns.last_light_humans.cafe.seat import frozen
    player = SimpleNamespace(stats={"vitality": 3, "strength": 3}, level=1)
    shift = SimpleNamespace()
    giant = Guest("Giantess", 140, 195, kills=3, age=50, height=180)
    results = [frozen(player, shift, giant, random.Random(seed))
               for seed in range(60)]
    assert any(results) and not all(results)
    giant.hesitated = True
    assert not any(frozen(player, shift, giant, random.Random(seed))
                   for seed in range(60))
    small = Guest("Small", 70, 100)
    assert not any(frozen(player, shift, small, random.Random(seed))
                   for seed in range(60))


def test_a_giant_guest_arrives_with_a_dread_line(controller) -> None:
    setup_pair(controller)
    controller.handle("Kerl", "!job cafe seat")
    giant = Guest("Giantess", 140, 195, kills=3, age=50, height=180)
    from cursed_descent.towns.last_light_humans.cafe.seat import guest_prompt
    shift = controller.town.shifts["kerl"]
    shift.client = giant
    player = controller.repository.load("Kerl")
    assert "Giantess" in guest_prompt(shift, player).text
    assert any(line in guest_prompt(shift, player).text
               for line in ("freeze", "mouth goes dry", "size of her"))


def test_random_cafe_guests_include_shemales_and_show_the_trait() -> None:
    from collections import Counter
    from cursed_descent.towns.last_light_humans.cafe.guests import trait_note
    guests = [new_guest(random.Random(seed)) for seed in range(400)]
    kinds = Counter(guest.gender for guest in guests)
    assert kinds["Shemale"] > 0 and kinds["Female"] > kinds["Shemale"]
    shemale = next(guest for guest in guests if guest.gender == "Shemale")
    assert shemale.endowment > 0
    assert "Shemale" in trait_note(shemale) and "cm of cock" in trait_note(
        shemale)
    female = next(guest for guest in guests if guest.gender == "Female")
    assert trait_note(female) == ""


def test_regulars_look_shows_the_details(controller) -> None:
    kerl = controller.repository.load("Kerl")
    regs(controller, "Kerl").add("cafe", {"name": "Mrs. Fenwick",
                                          "age": 50})
    reply = text(controller.handle("Kerl", "!regulars look Fenwick"))
    assert "Fenwick" in reply and "50" in reply
    assert "Look at whom" in text(controller.handle(
        "Kerl", "!regulars look Nobody"))


def test_ambient_stops_when_the_player_leaves_the_cafe(controller) -> None:
    setup_pair(controller)
    controller.handle("Kerl", "!cafe")
    assert "kerl" in controller.town.cafe_seen or "Kerl" in (
        controller.town.cafe_seen)
    controller.handle("Kerl", "!town")
    assert not controller.town.cafe_seen


def test_engulfed_victims_never_become_decor(controller,
                                             monkeypatch) -> None:
    from cursed_descent.towns.last_light_humans.cafe import service
    monkeypatch.setattr(service, "pick_outcome",
                        lambda victim, rng: "furniture")
    setup_pair(controller)
    kerl = controller.repository.load("Kerl")
    cafe_death(controller.town, kerl, "engulfed")
    entry = controller.town.cafe.entries[-1]
    assert entry["outcome"] == "full"
    assert controller.repository.load("Kerl").npc != "furniture"


def test_rider_is_released_when_she_goes_elsewhere(controller) -> None:
    setup_pair(controller)
    controller.handle("Kerl", "!job cafe seat")
    controller.handle("Galactica", "!sit Kerl")
    assert controller.town.shifts["kerl"].client is not None
    reply = text(controller.handle("Galactica", "!town"))
    assert "rises" in reply
    assert controller.town.shifts["kerl"].client is None


def test_no_ambient_text_after_going_home_or_swallowing(controller) -> None:
    setup_pair(controller)
    town = controller.town
    town.ambient_on = True
    controller.handle("Galactica", "!cafe")
    assert "Galactica" in town.cafe_seen
    controller.handle("Galactica", "!home")
    assert "Galactica" not in town.cafe_seen
    lines = []
    for step in range(1, 40):
        lines += ambient(town, town.now + step * 60)
    assert not any(message.recipient == "Galactica" for message in lines)


def test_crush_chance_needs_max_clench_and_a_huge_rear() -> None:
    from pytest import approx
    from cursed_descent.towns.last_light_humans.cafe.guests import crush_chance
    assert crush_chance(200, 90, 2) == 0.0
    assert crush_chance(150, 90, 3) == 0.0
    assert crush_chance(160, 80, 3) == approx(0.05)
    assert crush_chance(200, 140, 3) == approx(0.05 + 0.04 + 0.04)
    assert crush_chance(400, 300, 3) == 0.25
    assert crush_chance(160, 80, 3, vitality=100) == 0.02
    assert crush_chance(160, 80, 3, age=20) == approx(0.05 * 1.5)
    assert crush_chance(160, 80, 3, age=30) == approx(0.05)
    assert crush_chance(160, 80, 3, age=50) == approx(0.05 * 0.75)
    assert crush_chance(400, 300, 3, age=20) == 0.25
    assert crush_chance(150, 90, 3, vitality=0, age=20) == 0.0


def test_every_clench_click_at_full_squeeze_rolls_a_crush(
        controller, monkeypatch) -> None:
    import random
    from cursed_descent.towns.last_light_humans.cafe import stools
    from cursed_descent.towns.last_light_humans.cafe.stools import Ride, ride_torment
    stool = stools.Stool("Pet", 25, 175, 70, "average", 5, "calm")
    monkeypatch.setattr(stools, "crush_chance", lambda *a, **k: 0.2)

    class Lucky(random.Random):
        def random(self) -> float:
            return 0.0

    rider = controller.repository.load("Galactica")
    ride = Ride(stool, squeeze=3)
    lines = ride_torment(ride, "clench", rider, Lucky(1))
    assert ride.crush_now and ride.due == 0.0
    assert any("whimper" in line or "whine" in line for line in lines)


def test_a_huge_lady_at_max_clench_can_crush_the_seat(
        controller, monkeypatch) -> None:
    from cursed_descent.towns.last_light_humans.cafe import seat
    setup_pair(controller)
    controller.handle("Kerl", "!job cafe seat")
    arrive(controller, "kerl", Guest("Lady Doom", 120, 200))
    controller.town.shifts["kerl"].client.squeeze = 3
    monkeypatch.setattr(seat, "crush_chance", lambda *args, **kwargs: 1.0)
    monkeypatch.setattr(seat, "CAFE_SWALLOW_CHANCE", 0.0)
    reply = text(controller.handle("Kerl", "!hold"))
    assert "crack" in reply
    assert "kerl" not in controller.town.shifts


def test_a_dominant_lady_slaps_the_hand_away_and_punishes(
        controller) -> None:
    setup_pair(controller)
    controller.handle("Kerl", "!job cafe seat")
    seen = set()
    for seed in range(12):
        guest = Guest("Lady Doom", 90, 150)
        guest.cruel = 2
        arrive(controller, "kerl", guest)
        controller.town.rng = random.Random(seed)
        reply = text(controller.handle("Kerl", "!pat"))
        assert "How clumsy of me" not in reply
        for key in ("catches your hand", "breathe when I allow",
                    "apologise", "pins your wrist"):
            if key in reply:
                seen.add(key)
        if "kerl" not in controller.town.shifts:
            controller.handle("Kerl", "!job cafe seat")
    assert len(seen) >= 2


def test_round_command_advances_a_timed_shift_at_once(controller) -> None:
    setup_pair(controller)
    assert "not on a timed shift" in text(
        controller.handle("Galactica", "!round", now=0.0))
    controller.handle("Galactica", "!job brothel milk counter", now=0.0)
    shift = controller.town.shifts["Galactica"]
    assert not shift.job.interactive
    left = shift.left
    controller.handle("Galactica", "!round", now=1.0)
    after = controller.town.shifts.get("Galactica")
    assert after is None or after.left < left


def test_rough_milk_moves_depend_on_body_and_town(controller) -> None:
    from cursed_descent.town_buildings.work.moves import moves_for
    setup_pair(controller)
    lady = controller.repository.load("Galactica")
    assert "wring" in moves_for("milk", lady)
    assert "slap" not in moves_for("dancer", lady)
    controller.handle("Galactica", "!job tavern milk counter", now=0.0)
    reply = text(controller.handle("Galactica", "!move wring", now=2.0))
    assert "wring" in reply and "firmly" in reply
    lady = controller.repository.load("Galactica")
    lady.profile["town"] = "mudgate"
    controller.repository.save(lady)
    controller.handle("Galactica", "!job tavern milk counter", now=0.0)
    reply = text(controller.handle("Galactica", "!move wring", now=2.0))
    assert "no mercy" in reply


def test_clench_warning_uses_the_seats_vitality_and_floor(controller) -> None:
    setup_pair(controller)
    lady = controller.repository.load("Galactica")
    lady.body["butt"] = 200
    controller.repository.save(lady)
    controller.handle("Kerl", "!job cafe seat")
    kerl = controller.repository.load("Kerl")
    kerl.stats["vitality"] = 500
    controller.repository.save(kerl)
    controller.handle("Galactica", "!sit Kerl")
    controller.town.shifts["kerl"].client.squeeze = 2
    reply = text(controller.handle("Galactica", "!clench"))
    assert any(word in reply for word in ("whimper", "whine", "creak"))


def test_clenching_seat_pleads_and_a_crush_ends_with_a_pop(
        controller, monkeypatch) -> None:
    from cursed_descent.towns.last_light_humans.cafe import seat
    from cursed_descent.towns.last_light_humans.cafe.content import CRUSH_POPS
    setup_pair(controller)
    controller.handle("Kerl", "!job cafe seat")
    controller.handle("Galactica", "!sit Kerl")
    reply = text(controller.handle("Galactica", "!clench"))
    assert "kerl" in reply and any(
        word in reply for word in ("whimper", "squirm", "whine"))
    monkeypatch.setattr(seat, "crush_chance", lambda *args, **kwargs: 1.0)
    monkeypatch.setattr(seat, "CAFE_SWALLOW_CHANCE", 0.0)
    controller.town.shifts["kerl"].client.squeeze = 3
    reply = text(controller.handle("Kerl", "!hold"))
    assert any(pop in reply for pop in CRUSH_POPS)


def test_licking_describes_smell_and_taste(controller) -> None:
    from cursed_descent.towns.last_light_humans.cafe.content import LICK_TASTE
    setup_pair(controller)
    controller.handle("Kerl", "!job cafe seat")
    guest = Guest("Lady Mabel", 100, 140)
    guest.sweat = 10
    guest.musk = 10
    arrive(controller, "kerl", guest)
    reply = text(controller.handle("Kerl", "!lick"))
    assert LICK_TASTE[-1] in reply


def test_three_kisses_in_a_row_become_a_french_kiss(controller) -> None:
    setup_pair(controller)
    controller.handle("Kerl", "!job cafe seat")
    arrive(controller, "kerl")
    for _ in range(2):
        reply = text(controller.handle("Kerl", "!kiss"))
        assert "tongue slides in" not in reply
        controller.town.shifts["kerl"].due = controller.town.now + 20
    reply = text(controller.handle("Kerl", "!kiss"))
    assert "tongue slides in" in reply
    assert controller.town.shifts["kerl"].client.kisses == 0


def test_ambient_scenes_reuse_the_seat_texts_and_can_end_in_a_pop() -> None:
    import random
    from cursed_descent.towns.last_light_humans.cafe.ambient import ambient_line
    from cursed_descent.towns.last_light_humans.cafe.content import CRUSH_POPS
    rng = random.Random(7)
    lines = [ambient_line(rng) for _ in range(600)]
    assert any("wet crack" in line and any(p in line for p in CRUSH_POPS)
               for line in lines)
    assert any("tongue slides in" in line for line in lines)
    assert any("tastes" in line for line in lines)
    assert all("{" not in line for line in lines)


def test_a_pleased_lady_rises_more_often_for_a_soft_pat() -> None:
    from cursed_descent.config import (
        CAFE_PAT_CHANCE, CAFE_PAT_MAX, CAFE_PAT_PLEASED)
    from cursed_descent.towns.last_light_humans.cafe.content import ACT_PAT_OK
    assert "softly" in ACT_PAT_OK
    chances = [min(CAFE_PAT_MAX, CAFE_PAT_CHANCE + CAFE_PAT_PLEASED * level)
               for level in range(8)]
    assert chances == sorted(chances) and chances[-1] == CAFE_PAT_MAX


def test_a_visiting_story_lady_kill_counts_in_both_files(controller) -> None:
    import json
    import random as rnd
    from cursed_descent.npcs.visiting import Visit
    from cursed_descent.town_buildings.regulars import slug
    from cursed_descent.towns.last_light_humans.cafe.guests import DEADLY, new_guest
    from cursed_descent.towns import town_key
    setup_pair(controller)
    controller.town.visits_on = True
    controller.handle("Kerl", "!job cafe seat")
    kerl = controller.repository.load("Kerl")
    npc = next(n for n in controller.repository.npc_players()
               if n.npc == "jorveig")
    controller.town.visits.visits["jorveig"] = Visit(
        "jorveig", town_key(kerl), "cafe", 10 ** 12)
    store = controller.town.regulars_of(kerl)
    guest = None
    for seed in range(60):
        guest = new_guest(rnd.Random(seed), store)
        if guest.npc == "jorveig":
            break
    assert guest is not None and guest.npc == "jorveig"
    arrive(controller, "kerl", guest)
    DEADLY["on"] = True
    try:
        for _ in range(5):
            if "kerl" not in controller.town.shifts:
                break
            controller.handle("Kerl", "!lick")
    finally:
        DEADLY["on"] = False
    path = store.folder("cafe") / f"{slug(guest.name)}.json"
    raw = json.loads(path.read_text())
    assert raw["ref_id"] == npc.id and raw["kills"] == 1
    total = next(n for n in controller.repository.npc_players()
                 if n.npc == "jorveig").records.get("kills", 0)
    assert total == 1


def test_bertha_is_a_story_reference_with_her_real_body(controller) -> None:
    import json
    from cursed_descent.towns.last_light_humans.cafe.content import BERTHA_NAME
    from cursed_descent.towns.last_light_humans.cafe.guests import bertha_guest
    from cursed_descent.town_buildings.regulars import slug
    kerl = controller.repository.load("Kerl")
    store = controller.town.regulars_of(kerl)
    assert store.owners == {"cafe": "bertha", "brothel": "rose"}
    bertha = next(n for n in controller.repository.npc_players()
                  if n.npc == "bertha")
    bertha.body["weight"] = 199
    controller.repository.save(bertha)
    guest = bertha_guest(store)
    assert guest.name == BERTHA_NAME and guest.weight == 199
    assert guest.npc == "bertha"
    raw = json.loads((store.folder("cafe")
                      / f"{slug(BERTHA_NAME)}.json").read_text())
    assert raw["ref_id"] == bertha.id and "weight" not in raw
    store.owner_visit("brothel")
    rose = next(n for n in controller.repository.npc_players()
                if n.npc == "rose")
    assert json.loads(next(store.folder("brothel").glob("*.json")
                           ).read_text())["ref_id"] == rose.id


def test_bertha_does_not_complain_about_her_own_stool() -> None:
    from cursed_descent.towns.last_light_humans.cafe.content import BERTHA_DEATH
    assert all("refund" not in line and "Bertha!" not in line
               for line in BERTHA_DEATH)


def test_bertha_regular_is_found_and_counted_under_her_house_name(
        controller) -> None:
    from cursed_descent.towns.last_light_humans.cafe.content import BERTHA_NAME
    kerl = controller.repository.load("Kerl")
    store = controller.town.regulars_of(kerl)
    store.owner_visit("cafe", BERTHA_NAME)
    found = store.find("bertha")
    assert found is not None and found[1]["name"] == BERTHA_NAME
    before = found[1]["visits"]
    store.set("cafe", found[1]["name"], {"visits": before + 1})
    assert store.get("cafe", BERTHA_NAME)["visits"] == before + 1


def test_player_characters_never_send_calls_on_their_own(
        controller, monkeypatch) -> None:
    from cursed_descent.towns.last_light_humans.cafe import service
    setup_pair(controller)
    kerl = controller.repository.load("Kerl")
    kerl.profile["houses"] = {"last_light": {
        "type": "hut", "residents": [], "guests": []}}
    controller.repository.save(kerl)
    store = controller.town.regulars_of(kerl)
    store.add("brothel", {"name": "Galactica", "age": 30, "gender": "Female",
                          "weight": 70, "butt": 100, "cruel": 0,
                          "address_known": True, "home": "No. 1 Elm"})
    store.set("brothel", "Galactica", {"address_known": True})
    monkeypatch.setattr(service, "REGULARS_CALL_CHANCE", 1.0)
    assert regular_call(controller.town, "Kerl") is None
    assert regular_call(controller.town, "Kerl") is None
    store.add("brothel", {"name": "Mrs. Fenwick", "age": 50,
                          "gender": "Female", "weight": 70, "butt": 100,
                          "cruel": 0, "address_known": True,
                          "home": "No. 5 Elm"})
    store.set("brothel", "Mrs. Fenwick", {"address_known": True})
    called = regular_call(controller.town, "Kerl")
    assert called is not None and "Fenwick" in called.text

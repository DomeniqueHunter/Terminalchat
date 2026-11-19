import random

from cursed_descent.models import Player
from cursed_descent.town_buildings.brothel.shift import rent, serve
from cursed_descent.town_buildings.shifts import work
from cursed_descent.town_buildings.work.jobs import (
    JOBS, building_menu, find_job, jobs_of,
)


def hero(gold:int=100, gender:str="Herm") -> Player:
    player = Player(name="Hero", gender=gender)
    player.gold = gold
    return player


def text(messages) -> str:
    return "\n".join(message.text for message in messages)


def test_both_places_list_their_jobs_and_owner() -> None:
    tavern = text(building_menu("tavern", hero()))
    brothel = text(building_menu("brothel", hero()))
    assert "Hilda Cask" in tavern and "waiter" in tavern
    assert "Madame Rose" in brothel and "whore" in brothel
    assert "escort" in brothel and "book" in brothel
    assert "escort" not in tavern


def test_job_lists_match_the_design() -> None:
    tavern = {job.key for job in jobs_of("tavern")}
    brothel = {key for place, key in JOBS if place == "brothel"}
    assert tavern == {"waiter", "milk", "dancer"}
    assert brothel == {"whore", "waiter", "milk", "dancer", "escort"}


def test_tavern_shift_pays_minus_the_owner_cut() -> None:
    player = hero(0)
    shifts = {}
    messages = work(player, "tavern", "waiter", False, shifts,
                    random.Random(1))
    assert "keeps" in text(messages) and player.gold > 0
    assert shifts == {}


def test_nothing_works_inside_a_run() -> None:
    player = hero(0)
    assert "shut" in text(work(player, "brothel", "escort", True, {},
                               random.Random(1)))
    assert player.gold == 0


def test_brothel_cut_is_thirty_percent() -> None:
    player = hero(0)
    rng = random.Random(5)
    messages = text(work(player, "brothel", "escort", False, {}, rng))
    earned = int(messages.split("Earned ")[1].split(" gold")[0])
    cut = int(messages.split("keeps ")[1].split(".")[0])
    assert cut == round(earned * 0.3) and player.gold == earned - cut


def test_prostitute_shift_runs_six_clients_then_pays() -> None:
    player = hero(0)
    shifts = {}
    rng = random.Random(3)
    first = text(work(player, "brothel", "whore", False, shifts, rng))
    assert "Client 1/6" in first and "Hero" in shifts
    for number in range(2, 7):
        reply = text(serve(player, "bdsm give", shifts, rng))
        assert f"Client {number}/6" in reply
    last = text(serve(player, "oral receive", shifts, rng))
    assert "Shift over" in last and shifts == {} and player.gold > 0


def test_matching_the_clients_taste_pays_more() -> None:
    from cursed_descent.town_buildings.brothel.clients import Client
    from cursed_descent.town_buildings.work.jobs import JOBS, Shift
    results = {}
    for liked in (True, False):
        player = hero(0)
        job = JOBS[("brothel", "whore")]
        shift = Shift("brothel", job, 2,
                      client=Client("x", True, (("anal", "give"), ("bdsm", "give"))))
        act = "anal give" if liked else "trampling give"
        serve(player, act, {"Hero": shift}, random.Random(9))
        results[liked] = shift.earned
    assert results[True] > results[False]


def test_serve_needs_a_shift_and_a_valid_act() -> None:
    player = hero()
    assert "not on a shift" in text(serve(player, "anal", {},
                                          random.Random(1)))
    shifts = {}
    work(player, "brothel", "whore", False, shifts, random.Random(2))
    assert "give|receive" in text(serve(player, "tickling", shifts,
                                        random.Random(2)))
    assert "give|receive" in text(serve(player, "anal", shifts,
                                        random.Random(2)))
    assert "Finish your current shift" in text(
        work(player, "brothel", "waiter", False, shifts, random.Random(2)))


def test_rent_costs_gold_and_relieves_arousal() -> None:
    player = hero(100)
    player.needs["arousal"] = 80
    rent(player, "classic", False)
    assert player.gold == 40 and player.needs["arousal"] == 0
    assert "wants" in text(rent(player, "fetish", False))
    assert "shut" in text(rent(player, "classic", True))


def test_job_aliases() -> None:
    assert find_job("brothel", "prostitute").key == "whore"
    assert find_job("tavern", "whore") is None


def test_commands_through_the_controller(controller) -> None:
    reply = text(controller.handle("Kerl", "!job tavern waiter", now=0.0))
    for step in range(1, 6):
        reply += text(controller.tick(now=step * 20.0))
    assert "Shift over" in reply
    assert "Hilda Cask" in text(controller.handle("Kerl", "!tavern"))
    assert "Madame Rose" in text(controller.handle("Kerl", "!brothel"))
    assert "[job tavern" in text(controller.handle("Kerl", "!job"))


def test_every_practice_has_give_and_receive_variants() -> None:
    from cursed_descent.town_buildings.brothel.practices_content import (
        ACT_LABELS, PRACTICES, TOWN_LABELS,
    )
    assert set(PRACTICES) == set(ACT_LABELS) | set(TOWN_LABELS)
    for act, roles in PRACTICES.items():
        assert set(roles) == {"give", "receive"}
        for role, variants in roles.items():
            assert len(variants) >= 3, (act, role)
            assert all(len(text) > 120 for _, text in variants)
    assert len(PRACTICES["foot"]["give"]) >= 7


def test_placeholders_match_their_tags_and_always_fill() -> None:
    import string
    from cursed_descent.config import GENDERS
    from cursed_descent.town_buildings.brothel.practices import can_do, describe
    from cursed_descent.town_buildings.brothel.practices_anatomy import anatomy
    from cursed_descent.town_buildings.brothel.practices_content import PRACTICES
    needs = {"cock": "cock", "balls": "cock"}
    for roles in PRACTICES.values():
        for variants in roles.values():
            for tags, template in variants:
                fields = {name for _, name, _, _ in
                          string.Formatter().parse(template) if name}
                for field, tag in needs.items():
                    assert field not in fields or tag in tags, template
                if "bust" in fields:
                    assert "bust" in tags, template
    for gender in GENDERS:
        for height in (140, 170, 210):
            player = Player(name="X", gender=gender)
            player.body.update({"height": height, "weight": 60 + height // 3})
            info = anatomy(player)
            assert set(info["tags"]) >= {"cock", "bust", "tall"}
            for act in PRACTICES:
                for role in ("give", "receive"):
                    if not can_do(gender, act, role, player.body):
                        continue
                    for seed in range(15):
                        out = describe(player, act, role,
                                       random.Random(seed))
                        assert "{" not in out and out


def test_descriptions_follow_the_body() -> None:
    from cursed_descent.town_buildings.brothel.practices import describe
    hung = Player(name="H", gender="Male")
    hung.body.update({"endowment": 24, "girth": 15, "balls": 9})
    flat = Player(name="F", gender="Female")
    flat.body.update({"bust": 0})
    seen = [describe(hung, "anal", "give", random.Random(seed))
            for seed in range(30)]
    assert any("24 cm" in line for line in seen)
    assert any("massive" in line or "heavy balls" in line for line in seen)
    other = [describe(flat, "anal", "receive", random.Random(seed))
             for seed in range(30)]
    assert not any("cock" in line for line in other)


def test_variety_across_runs() -> None:
    from cursed_descent.town_buildings.brothel.practices import describe
    player = Player(name="H", gender="Herm")
    lines = {describe(player, "foot", "give", random.Random(seed))
             for seed in range(40)}
    assert len(lines) >= 5


def test_foot_give_is_overwhelming_for_a_big_heavy_body() -> None:
    from cursed_descent.town_buildings.brothel.practices import describe
    giant = Player(name="G", gender="Female")
    giant.body.update({"height": 205, "weight": 130, "muscle": 80})
    lines = " ".join(describe(giant, "foot", "give", random.Random(seed))
                     for seed in range(40))
    for word in ("size", "weight", "despair", "helpless"):
        assert word in lines


def test_anal_and_vaginal_depend_on_the_body() -> None:
    from cursed_descent.town_buildings.brothel.practices import can_do
    assert can_do("Male", "anal", "give") and can_do("Male", "anal", "receive")
    assert not can_do("Female", "anal", "give")
    assert can_do("Female", "vaginal", "receive")
    assert not can_do("Female", "vaginal", "give")
    assert can_do("Shemale", "vaginal", "give")
    assert not can_do("Male", "vaginal", "receive")
    assert can_do("Herm", "vaginal", "give") and can_do("Herm", "vaginal",
                                                        "receive")
    for act in ("facesitting", "bdsm", "trampling", "foot"):
        assert can_do("None", act, "give") and can_do("None", act, "receive")


def test_a_refused_choice_does_not_cost_a_client() -> None:
    player = hero(0, "Female")
    shifts = {}
    work(player, "brothel", "whore", False, shifts, random.Random(4))
    left = shifts["Hero"].left
    assert "can't" in text(serve(player, "anal give", shifts,
                                 random.Random(4)))
    assert shifts["Hero"].left == left


def test_clients_only_wish_for_things_you_can_do() -> None:
    from cursed_descent.town_buildings.brothel.practices import can_do
    from cursed_descent.town_buildings.brothel.clients import new_client
    player = hero(0, "Female")
    rng = random.Random(11)
    for _ in range(60):
        client = new_client(player, rng)
        assert all(can_do("Female", act, role) for act, role in client.likes)


def test_practices_command_lists_and_describes(controller) -> None:
    overview = text(controller.handle("Kerl", "!practices"))
    assert "FACESITTING" in overview and "give" in overview
    detail = text(controller.handle("Kerl", "!practices bdsm"))
    assert "✔ give" in detail and "bdsm".upper() in detail.upper()


def milk(gender:str, variant:str, body:dict | None=None, seed:int=1) -> str:
    player = hero(0, gender)
    player.body.update(body or {})
    return text(work(player, "tavern", f"milk {variant}".strip(), False,
                     {}, random.Random(seed)))


def test_barrel_shows_breasts_and_or_cock_by_body() -> None:
    female = " ".join(milk("Female", "barrel", {"bust": 500}, seed)
                      for seed in range(15))
    assert "barrel" in female and "cock" not in female
    assert "breasts" in female
    male = " ".join(milk("Male", "barrel", {"bust": 0}, seed)
                    for seed in range(15))
    assert "cock" in male and "breasts" not in male
    herm = " ".join(milk("Herm", "barrel", {"bust": 500}, seed)
                    for seed in range(20))
    assert "breasts" in herm and "cock" in herm


def test_barrel_needs_something_to_tap() -> None:
    reply = milk("None", "barrel", {"bust": 0})
    assert "nothing to tap" in reply and "Shift over" not in reply


def test_counter_works_for_every_body() -> None:
    for gender in ("None", "Female", "Male", "Herm"):
        reply = milk(gender, "counter")
        assert "squat" in reply and "Shift over" in reply


def test_unspecified_milk_picks_a_variant() -> None:
    seen = set()
    for seed in range(30):
        reply = milk("Herm", "", None, seed)
        seen.add("oak barrel" in reply)
    assert seen == {True, False}


def test_milk_menu_explains_both_variants() -> None:
    menu = text(building_menu("tavern", hero()))
    assert "milk barrel" in menu and "milk counter" in menu


def test_oral_is_offered_with_give_and_receive() -> None:
    from cursed_descent.town_buildings.brothel.practices import can_do, options_for
    from cursed_descent.town_buildings.brothel.practices_content import ACT_LABELS
    assert "oral" in ACT_LABELS
    for gender in ("Male", "Female", "Herm", "Shemale", "Cunt-boy"):
        assert can_do(gender, "oral", "give")
        assert can_do(gender, "oral", "receive")
    assert can_do("None", "oral", "give")
    assert not can_do("None", "oral", "receive")
    assert ("oral", "give") in options_for("None")


def test_oral_receive_follows_the_body() -> None:
    from cursed_descent.town_buildings.brothel.practices import describe
    male = Player(name="M", gender="Male")
    male.body.update({"endowment": 22, "balls": 8})
    female = Player(name="F", gender="Female")
    males = [describe(male, "oral", "receive", random.Random(i))
             for i in range(30)]
    females = [describe(female, "oral", "receive", random.Random(i))
               for i in range(30)]
    assert all("cock" in line or "balls" in line for line in males)
    assert not any("cock" in line for line in females)
    assert any("tongue" in line for line in females)


def test_serving_oral_in_a_shift() -> None:
    player = hero(0, "Female")
    shifts = {}
    work(player, "brothel", "whore", False, shifts, random.Random(6))
    reply = text(serve(player, "oral receive", shifts, random.Random(6)))
    assert "client" in reply.lower() or "gold" in reply
    assert "can't" not in reply


def test_titfuck_needs_a_cock_to_give_and_breasts_to_receive() -> None:
    from cursed_descent.town_buildings.brothel.practices import can_do
    assert can_do("Male", "titfuck", "give", {"bust": 0})
    assert not can_do("Female", "titfuck", "give", {"bust": 500})
    assert can_do("Female", "titfuck", "receive", {"bust": 300})
    assert not can_do("Female", "titfuck", "receive", {"bust": 0})
    assert not can_do("Male", "titfuck", "receive", {"bust": 100})


def test_watersports_and_scat_exist_for_every_body() -> None:
    from cursed_descent.town_buildings.brothel.practices import can_do, describe
    for act in ("watersports", "scat"):
        for role in ("give", "receive"):
            for gender in ("None", "Female", "Male", "Herm"):
                player = Player(name="P", gender=gender)
                assert can_do(gender, act, role, player.body)
                assert describe(player, act, role, random.Random(1))


def test_the_new_acts_are_dominant_wishes_too() -> None:
    from cursed_descent.town_buildings.brothel.practices_content import (
        DOMINANT_ACTS,
    )
    assert {"watersports", "scat"} <= set(DOMINANT_ACTS)


def test_titfuck_receive_follows_the_chest() -> None:
    from cursed_descent.town_buildings.brothel.practices import describe
    player = Player(name="B", gender="Female")
    player.body.update({"bust": 700})
    seen = " ".join(describe(player, "titfuck", "receive", random.Random(i))
                    for i in range(20))
    assert "breasts" in seen or "bust" in seen


def test_watersports_scale_with_the_body() -> None:
    from cursed_descent.town_buildings.brothel.practices import describe
    from cursed_descent.town_buildings.brothel.practices_anatomy import flow_word
    small = Player(name="S", gender="Female")
    small.body.update({"height": 160, "weight": 52})
    big = Player(name="B", gender="Herm")
    big.body.update({"height": 195, "weight": 110, "endowment": 26})
    giant = Player(name="G", gender="Herm")
    giant.body.update({"height": 215, "weight": 140, "endowment": 32})
    assert flow_word(small.body, False) == "a warm, steady stream"
    assert "shower" in flow_word(big.body, True)
    assert "flood" in flow_word(giant.body, True)
    seen = " ".join(describe(big, "watersports", "give", random.Random(i))
                    for i in range(40))
    assert "shower" in seen
    seen_small = " ".join(describe(small, "watersports", "give",
                                   random.Random(i)) for i in range(40))
    assert "shower" not in seen_small and "monsoon" not in seen_small
    seen_giant = " ".join(describe(giant, "watersports", "give",
                                   random.Random(i)) for i in range(60))
    assert "monsoon" in seen_giant


def test_piss_nursing_is_part_of_watersports_giving() -> None:
    from cursed_descent.town_buildings.brothel.practices import can_do, parse_choice
    from cursed_descent.town_buildings.brothel.practices_content import ACT_LABELS
    assert "pissnursing" not in ACT_LABELS
    assert can_do("Female", "watersports", "give")
    assert parse_choice(["piss", "nursing", "give"]) == ("watersports",
                                                         "give")
    assert parse_choice(["nursing", "receive"]) == ("watersports",
                                                    "receive")


def test_nursing_variants_only_come_with_a_cock_and_scale() -> None:
    from cursed_descent.town_buildings.brothel.practices import describe
    giant = Player(name="G", gender="Herm")
    giant.body.update({"height": 215, "weight": 140, "endowment": 32})
    seen = " ".join(describe(giant, "watersports", "give",
                             random.Random(i)) for i in range(120))
    assert "nursed" in seen and "swallow" in seen and "flood" in seen
    female = Player(name="F", gender="Female")
    lines = " ".join(describe(female, "watersports", "give",
                             random.Random(i)) for i in range(120))
    assert "nursed" not in lines and "Piss Nursing" not in lines
    receive = " ".join(describe(female, "watersports", "receive",
                                random.Random(i)) for i in range(60))
    assert "nursing" in receive


def test_piss_nursing_in_a_shift() -> None:
    player = hero(0, "Herm")
    shifts = {}
    work(player, "brothel", "whore", False, shifts, random.Random(8))
    reply = text(serve(player, "watersports give", shifts,
                       random.Random(8)))
    assert "can't" not in reply and "gold" in reply


def test_tub_scene_nearly_drowns_the_client_with_a_safe_signal() -> None:
    from cursed_descent.town_buildings.brothel.practices import describe
    giant = Player(name="G", gender="Herm")
    giant.body.update({"height": 215, "weight": 140, "endowment": 32})
    seen = " ".join(describe(giant, "watersports", "give",
                             random.Random(i)) for i in range(200))
    assert "almost drown" in seen and "bell" in seen
    small = Player(name="S", gender="Female")
    lines = " ".join(describe(small, "watersports", "give",
                              random.Random(i)) for i in range(200))
    assert "drown" not in lines and "bell" not in lines


def start(gender:str="Herm", seed:int=3, personality:str=""):
    player = hero(0, gender)
    player.personality = personality
    shifts = {}
    first = text(work(player, "brothel", "whore", False, shifts,
                      random.Random(seed)))
    return player, shifts, first


def test_client_greets_you_when_they_walk_in() -> None:
    from cursed_descent.town_buildings.brothel.dialogue_content import (
        GREETINGS,
    )
    _, shifts, first = start()
    client = shifts["Hero"].client
    assert client.hello in first and client.temper in GREETINGS
    assert "tone:" in first and "sweet | teasing | stern" in first


def test_both_sides_speak_after_every_service() -> None:
    from cursed_descent.town_buildings.brothel.dialogue_content import (
        PLAYER_LINES, REACTIONS,
    )
    player, shifts, _ = start()
    client = shifts["Hero"].client
    reply = text(serve(player, "bdsm give stern", shifts,
                       random.Random(4)))
    assert "You (stern):" in reply
    assert any(line in reply for line in PLAYER_LINES["stern"]["give"])
    verdicts = [line for kind in REACTIONS[client.temper].values()
                for line in kind]
    assert any(line in reply for line in verdicts)
    assert client.name[0].upper() in reply


def test_matching_tone_pays_a_quarter_more() -> None:
    from cursed_descent.town_buildings.brothel.clients import Client
    from cursed_descent.town_buildings.brothel.shift import judge
    shy = Client("a shy tailor", False, (("oral", "give"),), "shy")
    sweet, liked = judge(shy, "anal", "give", "sweet", 40)
    stern, _ = judge(shy, "anal", "give", "stern", 40)
    assert sweet == round(40 * 1.25) and stern == 40 and not liked
    needy = Client("x", True, (("bdsm", "give"),), "needy")
    assert judge(needy, "bdsm", "give", "stern", 40)[0] == round(
        40 * 2.0 * 1.25)


def test_default_tone_follows_the_personality() -> None:
    from cursed_descent.town_buildings.brothel.dialogue import default_tone
    assert default_tone(hero(0)) == "teasing"
    shy = hero(0)
    shy.personality = "shy and kind"
    assert default_tone(shy) == "sweet"
    cold = hero(0)
    cold.personality = "cold, strict"
    assert default_tone(cold) == "stern"


def test_tone_is_optional_and_shown_in_the_scene() -> None:
    player, shifts, _ = start(personality="warm")
    reply = text(serve(player, "oral give", shifts, random.Random(5)))
    assert "You (sweet):" in reply


def test_dominated_clients_are_needy() -> None:
    from cursed_descent.town_buildings.brothel.clients import new_client
    player = hero(0)
    rng = random.Random(1)
    seen = {(c.dominated, c.temper) for c in
            (new_client(player, rng) for _ in range(200))}
    assert all(t == "needy" for d, t in seen if d)
    assert all(t != "needy" for d, t in seen if not d)


def test_all_dialogue_tables_are_complete() -> None:
    from cursed_descent.town_buildings.brothel import dialogue_content as d
    temper_all = set(d.TEMPERS) | {d.DOMINATED_TEMPER}
    assert set(d.GREETINGS) == temper_all == set(d.REACTIONS)
    assert set(d.PREFERRED_TONE) == temper_all
    for tone in d.TONES:
        assert set(d.PLAYER_LINES[tone]) == {"give", "receive"}
    for temper in temper_all:
        assert len(d.GREETINGS[temper]) >= 3
        assert set(d.REACTIONS[temper]) == {"liked", "fine"}


def test_town_buildings_are_sorted_into_folders() -> None:
    from pathlib import Path
    import cursed_descent.town_buildings as tb
    root = Path(tb.__file__).parent
    folders = {p.name for p in root.iterdir()
               if p.is_dir() and not p.name.startswith("_")}
    assert {"brothel", "work"} <= folders
    assert "maidschool" not in folders
    assert (root.parent / "towns" / "last_light_humans"
            / "maidschool").is_dir()
    loose = {p.name for p in root.glob("*.py")}
    assert not any(name.startswith(("practices", "maid_", "work"))
                   for name in loose)
    assert (root / "brothel" / "practices_content.py").exists()


def test_scat_giving_always_tells_the_client_to_open_wide() -> None:
    from cursed_descent.town_buildings.brothel.practices_content import (
        PRACTICES,
    )
    for _, text in PRACTICES["scat"]["give"]:
        assert "open" in text.casefold() and "wide" in text.casefold()


def test_ballbusting_give_for_everyone_receive_needs_balls() -> None:
    from cursed_descent.town_buildings.brothel.practices import (
        can_do, describe,
    )
    from cursed_descent.town_buildings.brothel.practices_content import (
        DOMINANT_ACTS,
    )
    assert "ballbusting" in DOMINANT_ACTS
    for gender in ("None", "Female", "Male", "Herm"):
        assert can_do(gender, "ballbusting", "give")
    assert can_do("Male", "ballbusting", "receive")
    assert not can_do("Female", "ballbusting", "receive")
    male = Player(name="M", gender="Male")
    male.body.update({"balls": 9})
    seen = " ".join(describe(male, "ballbusting", "receive",
                             random.Random(i)) for i in range(30))
    assert "balls" in seen and "green" in seen.casefold()
    female = Player(name="F", gender="Female")
    assert describe(female, "ballbusting", "give", random.Random(1))


def test_ballbusting_scenes_keep_a_safe_word_and_aftercare() -> None:
    from cursed_descent.town_buildings.brothel.practices_content import (
        PRACTICES,
    )
    for role in ("give", "receive"):
        joined = " ".join(text for _, text in PRACTICES["ballbusting"][role])
        assert any(word in joined for word in ("green", "word", "signal"))


def test_scat_giving_makes_the_client_eat_what_they_are_given() -> None:
    from cursed_descent.town_buildings.brothel.practices_content import (
        PRACTICES,
    )
    for _, text in PRACTICES["scat"]["give"]:
        assert "eat" in text.casefold()

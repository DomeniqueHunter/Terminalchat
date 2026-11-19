import random
from pathlib import Path

from cursed_descent.controller import GameController
from cursed_descent.events.caravaneer.npc import (
    fill, random_pony, roster, trim,
)
from cursed_descent.events.caravaneer.config import CAP, START
from cursed_descent.models import Player
from cursed_descent.spawns import RULES_BY_KIND
from tests.ready import confirm


def say(controller:GameController, name:str, text:str) -> str:
    return "\n".join(m.text for m in controller.handle(name, text))


def start(tmp_path:Path, names:tuple[str, ...]=("Hero", "Lena", "Mira"),
          genders:dict[str, str] | None=None) -> GameController:
    genders = genders or {"Lena": "Female", "Mira": "Herm"}
    controller = GameController(tmp_path, debug=True)
    for name in names:
        controller.repository.save(Player(
            name=name, gold=500, gender=genders.get(name, "Male")))
    say(controller, names[0], "!lobby")
    for name in names[1:]:
        say(controller, name, "!join")
    say(controller, names[0], "!start")
    confirm(controller)
    say(controller, names[0], "!trigger caravaneer")
    return controller


def test_caravaneer_is_registered_with_a_segment_limit() -> None:
    rule = RULES_BY_KIND["caravaneer"]
    assert rule.min_stage == 1 and rule.per_segment == 2


def test_the_wagon_starts_with_two_ponies_and_examine_lists_them(
        tmp_path:Path) -> None:
    controller = start(tmp_path)
    assert controller.session.events.event["kind"] == "caravaneer"
    assert len(roster(controller.repository)) == START
    text = say(controller, "Hero", "!examine")
    assert "harness" in text and text.count("(") >= START


def test_majority_vote_trades_the_chosen_lady(tmp_path:Path) -> None:
    controller = start(tmp_path)
    say(controller, "Hero", "!offer Lena")
    assert controller.session.events.event["kind"] == "caravaneer"
    output = say(controller, "Mira", "!offer Lena")
    lena = controller.repository.load("Lena")
    assert lena.last_fate == "caravaned" and not lena.alive
    ponies = roster(controller.repository)
    assert any(pony.profile.get("origin") == "Lena" for pony in ponies)
    pony = next(pony for pony in ponies
                if pony.profile.get("origin") == "Lena")
    assert pony.full_name == "Lena" and pony.profile["adventurer"]
    assert "Lena" not in [member.name for member in
                          controller.session.living()]
    assert "receives the chest" in output


def test_departing_votes_refuse_the_trade(tmp_path:Path) -> None:
    controller = start(tmp_path)
    say(controller, "Hero", "!depart")
    output = say(controller, "Lena", "!depart")
    assert "turns the deal down" in output
    assert controller.repository.load("Lena").alive


def test_only_the_named_ladies_can_be_offered(tmp_path:Path) -> None:
    controller = start(tmp_path)
    output = say(controller, "Hero", "!offer Hero")
    assert "nobody called that" in output.lower()
    assert controller.session.events.event["kind"] == "caravaneer"


def test_the_oldest_pony_leaves_above_the_cap(tmp_path:Path) -> None:
    controller = start(tmp_path)
    repository = controller.repository
    rng = random.Random(1)
    for _ in range(CAP):
        random_pony(repository, rng)
    before = roster(repository)
    lines = trim(repository)
    after = roster(repository)
    assert len(after) == CAP and lines
    assert before[0].name not in [pony.name for pony in after]
    assert len(fill(repository, rng)) == CAP


def test_no_eligible_lady_skips_the_event_but_not_a_forced_one(
        tmp_path:Path) -> None:
    controller = start(tmp_path, ("Hero", "Pal"), {})
    event = controller.session.events
    assert event.event["kind"] == "caravaneer"
    assert "depart" in event.available()
    assert "offer" not in event.available()


def test_the_event_is_limited_per_segment(tmp_path:Path) -> None:
    controller = start(tmp_path)
    events = controller.session.events
    for _ in range(2):
        events.note_segment("caravaneer")
    rule = RULES_BY_KIND["caravaneer"]
    stage = controller.session.stage
    assert events.segment_full(rule, stage)
    assert not events.segment_full(rule, stage + 40)


def test_the_ware_is_fixed_and_shown_in_the_location_panel(
        tmp_path:Path) -> None:
    from cursed_descent.web.run_panels import run_shop_panel
    controller = start(tmp_path)
    hero = controller.repository.load("Hero")
    panel = run_shop_panel(controller, hero)
    ware = controller.session.events.event["data"]["ware"]
    from cursed_descent.content import ITEMS
    assert ITEMS[ware]["name"] in "\n".join(panel.lines)
    commands = [button.command for button in panel.buttons]
    assert "!offer Lena" in commands and "!offer Mira" in commands
    assert "!depart" in commands
    say(controller, "Hero", "!offer Lena")
    panel = run_shop_panel(controller, hero)
    text = "\n".join(panel.lines)
    assert "Your vote: Lena" in text and "Still to vote" in text
    say(controller, "Mira", "!offer Lena")
    receivers = [member for member in controller.session.living()
                 if ware in member.inventory]
    assert len(receivers) == 1


def test_every_female_or_futa_member_gets_an_offer_button(
        tmp_path:Path) -> None:
    from cursed_descent.web.run_panels import run_shop_panel
    names = ("Hero", "Anna", "Bea", "Cleo", "Dora")
    controller = start(tmp_path, names, {
        "Anna": "Female", "Bea": "Shemale", "Cleo": "Male-Herm"})
    hero = controller.repository.load("Hero")
    commands = [button.command
                for button in run_shop_panel(controller, hero).buttons]
    for name in ("Anna", "Bea", "Cleo"):
        assert f"!offer {name}" in commands
    assert "!offer Hero" not in commands


def test_the_ware_goes_to_a_human_with_room_not_to_an_npc() -> None:
    from cursed_descent.events.caravaneer.event import reward_taker
    human = Player(name="Human")
    full = Player(name="Full")
    full.inventory = ["potion_small"] * full.bag_size
    npc = Player(name="Merc", npc="mercenary")
    for _ in range(30):
        assert reward_taker([human, npc]) is human
        assert reward_taker([full, human, npc]) is human
    assert reward_taker([full, npc]) is full


def test_the_wares_are_unique_legendaries_and_never_loot() -> None:
    from cursed_descent.content import ITEMS
    from cursed_descent.dungeon import roll_item
    from cursed_descent.events.caravaneer.event import rare_item
    wares = {key: item for key, item in ITEMS.items()
             if item.get("caravan")}
    assert len(wares) >= 6
    for key, item in wares.items():
        assert item["rarity"] == "legendary" and item["no_loot"], key
        assert not item["shops"], key
        if item["slot"] == "weapon":
            assert item["damage"] >= 80, key
    assert max(item.get("armor", 0) for item in wares.values()) >= 60
    for _ in range(200):
        assert rare_item(10) in wares
        assert roll_item(10) not in wares

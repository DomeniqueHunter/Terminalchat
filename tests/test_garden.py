from pathlib import Path

from cursed_descent.content import ITEMS
from cursed_descent.furnishing import garden, rules
from cursed_descent.furnishing.layout import slots_of
from cursed_descent.furnishing.plants import (
    BLOOM, HUNGRY_AFTER, WILT_AFTER,
)
from cursed_descent.plants import PLANTS
from cursed_descent.houses import grow_gardens
from cursed_descent.web import furnish
from cursed_descent.web.hub import GameHub
from tests.test_furnishing import home, player_of, setup


def spot(kind:str="hut") -> str:
    return next(s for s, k in slots_of(kind).items() if k == "plant")


def with_seed(hub:GameHub) -> tuple[str, int]:
    player = player_of(hub)
    player.inventory = ["seductress_seed"]
    hub.controller.repository.save(player)
    return spot(), 1


def test_a_seed_is_planted_and_listed(data_path:Path) -> None:
    hub = GameHub(data_path)
    setup(hub)
    slot, number = with_seed(hub)
    text = hub.controller.handle("kerl", f"!home plant {slot} {number}")
    assert "seed" in text[0].text.casefold()
    assert player_of(hub).inventory == []
    assert home(hub)["plants"][slot]["kind"] == "seductress"
    assert "heart-shaped seed" in rules.describe(home(hub))
    again = hub.controller.handle("kerl", f"!home plant {slot} 1")
    assert "do not carry" in again[0].text


def test_only_seeds_go_into_garden_spots(data_path:Path) -> None:
    hub = GameHub(data_path)
    setup(hub)
    player = player_of(hub)
    player.inventory = ["wool_rug"]
    hub.controller.repository.save(player)
    text = hub.controller.handle("kerl", f"!home plant {spot()} 1")
    assert "not something you can plant" in text[0].text
    text = hub.controller.handle("kerl", "!home plant bedroom:0 1")
    assert "garden spot" in text[0].text


def test_growth_needs_water_each_run(data_path:Path) -> None:
    hub = GameHub(data_path)
    setup(hub)
    slot, number = with_seed(hub)
    hub.controller.handle("kerl", f"!home plant {slot} {number}")
    state = home(hub)["plants"][slot]
    for _ in range(6):
        hub.controller.handle("kerl", f"!home water {slot}")
        grow_gardens(player_of(hub))
    assert state["growth"] == PLANTS["seductress"]["need"][BLOOM]
    assert rules.blooming(home(hub))
    hub.controller.handle("kerl", f"!home water {slot}")
    text = hub.controller.handle("kerl", f"!home water {slot}")
    assert "watered already" in text[0].text


def test_a_dry_plant_wilts_and_can_be_revived(data_path:Path) -> None:
    hub = GameHub(data_path)
    setup(hub)
    slot, number = with_seed(hub)
    hub.controller.handle("kerl", f"!home plant {slot} {number}")
    state = home(hub)["plants"][slot]
    for _ in range(WILT_AFTER):
        grow_gardens(player_of(hub))
    assert state["wilted"] and state["growth"] == 0
    assert "limp and grey" in rules.describe(home(hub))
    hub.controller.handle("kerl", f"!home water {slot}")
    assert not state["wilted"]


def test_harvest_gives_nectar_and_regrows(data_path:Path) -> None:
    hub = GameHub(data_path)
    setup(hub)
    slot, number = with_seed(hub)
    hub.controller.handle("kerl", f"!home plant {slot} {number}")
    early = hub.controller.handle("kerl", f"!home harvest {slot}")
    assert "not in bloom" in early[0].text
    state = home(hub)["plants"][slot]
    state["growth"] = PLANTS["seductress"]["need"][BLOOM]
    player = player_of(hub)
    player.inventory = []
    hub.controller.repository.save(player)
    hub.controller.handle("kerl", f"!home harvest {slot}")
    inventory = player_of(hub).inventory
    assert inventory.count("seductress_nectar") in (1, 2)
    assert state["growth"] == PLANTS["seductress"]["need"][
        PLANTS["seductress"]["regrow"]]
    assert ITEMS["seductress_nectar"]["heal"] > 0


def test_a_blooming_plant_adds_comfort_and_a_buff(data_path:Path) -> None:
    hub = GameHub(data_path)
    setup(hub)
    slot, number = with_seed(hub)
    hub.controller.handle("kerl", f"!home plant {slot} {number}")
    before = rules.comfort_of(home(hub))
    home(hub)["plants"][slot]["growth"] = 6
    assert rules.comfort_of(home(hub)) == before + 4
    player = player_of(hub)
    assert "scent" in rules.comfort_buff(player, home(hub)).casefold()
    assert "home_bloom" in player.buffs


def test_uproot_and_overlay(data_path:Path) -> None:
    hub = GameHub(data_path)
    setup(hub)
    slot, number = with_seed(hub)
    view = furnish.plant_view(player_of(hub), home(hub), slot, True)
    assert view["seeds"][0]["command"] == f"!home plant {slot} 1"
    hub.controller.handle("kerl", f"!home plant {slot} {number}")
    view = furnish.plant_view(player_of(hub), home(hub), slot, True)
    assert [a["label"] for a in view["actions"]] == [
        "Water", "Harvest", "Uproot"]
    assert furnish.plant_view(player_of(hub), home(hub), "bedroom:0",
                              True) is None
    hub.controller.handle("kerl", f"!home uproot {slot}")
    assert slot not in home(hub)["plants"]
    assert garden.seed_kind("seductress_seed") == "seductress"


def test_garden_slot_shows_the_plant_name(data_path:Path) -> None:
    hub = GameHub(data_path)
    setup(hub)
    slot, number = with_seed(hub)

    def label() -> str:
        slots = [entry for room in rules.rooms_view(home(hub))
                 for entry in room["slots"] if entry["id"] == slot]
        return slots[0]["label"]

    assert label() == "Garden Bed (empty)"
    hub.controller.handle("kerl", f"!home plant {slot} {number}")
    assert label() == "Seductress Vine (Seedling)"


def planted(hub:GameHub) -> tuple[str, dict]:
    slot, number = with_seed(hub)
    hub.controller.handle("kerl", f"!home plant {slot} {number}")
    return slot, home(hub)["plants"][slot]


def ready(hub:GameHub, sweat:int=30) -> None:
    player = player_of(hub)
    player.gender = "Male"
    player.body.update(endowment=15, balls=5)
    player.sweat = sweat
    hub.controller.repository.save(player)


def test_feeding_needs_size_and_sweat(data_path:Path) -> None:
    hub = GameHub(data_path)
    setup(hub)
    slot, state = planted(hub)
    player = player_of(hub)
    player.gender = "Female"
    assert "nothing to take" in garden.feed(player, home(hub), slot)[0].text
    ready(hub, sweat=0)
    player = player_of(hub)
    assert "too dry" in garden.feed(player, home(hub), slot)[0].text
    player.sweat = 30
    player.body["endowment"] = 9
    assert "not big enough" in garden.feed(player, home(hub), slot)[0].text
    player.body.update(endowment=15, balls=3)
    assert "not big enough" in garden.feed(player, home(hub), slot)[0].text


def test_feeding_waters_grows_and_stores_nectar(data_path:Path) -> None:
    hub = GameHub(data_path)
    setup(hub)
    slot, state = planted(hub)
    ready(hub)
    state["growth"] = PLANTS["seductress"]["need"][2]
    text = hub.controller.handle("kerl", f"!home feed {slot}")
    assert "cock" in text[0].text
    player = player_of(hub)
    assert player.sweat == 0 and "home_afterglow" in player.buffs
    assert state["watered"] and state["stored"] == 1
    again = hub.controller.handle("kerl", f"!home feed {slot}")
    assert "already" in again[0].text
    before = state["growth"]
    grow_gardens(player_of(hub))
    assert state["growth"] == before + 2 and state["fed_by"] == []


def test_a_guest_can_feed_the_plant(data_path:Path) -> None:
    hub = GameHub(data_path)
    setup(hub)
    slot, state = planted(hub)
    view = furnish.plant_view(player_of(hub), home(hub), slot, False)
    assert view["actions"] == []
    ready(hub)
    player = player_of(hub)
    view = furnish.plant_view(player, home(hub), slot, False)
    assert [a["command"] for a in view["actions"]] == [
        f"!home feed {slot}"]
    garden.feed(player, home(hub), slot)
    assert furnish.plant_view(player, home(hub), slot, False)[
        "actions"] == []


def test_harvest_adds_stored_nectar(data_path:Path) -> None:
    hub = GameHub(data_path)
    setup(hub)
    slot, state = planted(hub)
    state.update(growth=PLANTS["seductress"]["need"][BLOOM], stored=3)
    player = player_of(hub)
    player.inventory = []
    hub.controller.repository.save(player)
    hub.controller.handle("kerl", f"!home harvest {slot}")
    assert player_of(hub).inventory.count("seductress_nectar") >= 4
    assert state["stored"] == 0


def test_a_neglected_overgrown_plant_drains_the_owner(
        data_path:Path) -> None:
    hub = GameHub(data_path)
    setup(hub)
    slot, state = planted(hub)
    state["growth"] = PLANTS["seductress"]["need"][-1]
    for _ in range(HUNGRY_AFTER):
        grow_gardens(player_of(hub))
    assert rules.starving(home(hub))
    player = player_of(hub)
    assert "drains" in rules.comfort_buff(player, home(hub))
    assert "home_drained" in player.buffs
    hub.controller.repository.save(player)
    hub.controller.handle("kerl", f"!home harvest {slot}")
    assert "home_drained" not in player_of(hub).buffs
    assert not rules.starving(home(hub))


def test_a_visitor_feeds_the_hosts_plant(data_path:Path) -> None:
    hub = GameHub(data_path)
    setup(hub)
    slot, state = planted(hub)
    repository = hub.controller.repository
    guest = repository.load("galactica")
    home(hub)["guests"].append({"id": guest.id, "name": guest.name})
    guest.profile["home_host"] = player_of(hub).id
    guest.gender = "Male"
    guest.body.update(endowment=15, balls=5)
    guest.sweat = 30
    repository.save(guest)
    text = hub.controller.handle("galactica", f"!home feed {slot}")
    assert "cock" in text[0].text
    assert state["fed_by"] == [guest.id]
    assert home(hub)["plants"][slot]["fed_by"] == [guest.id]


def test_irrigation_keeps_plants_alive_but_does_not_grow_them(
        data_path:Path) -> None:
    hub = GameHub(data_path)
    setup(hub)
    slot, state = planted(hub)
    utility = next(s for s, k in slots_of(home(hub)["type"]).items()
                   if k == "utility")
    player = player_of(hub)
    player.inventory = ["irrigation_system"]
    hub.controller.repository.save(player)
    hub.controller.handle("kerl", f"!home place {utility} 1")
    assert rules.irrigated(home(hub))
    assert "Copper pipes" in rules.describe(home(hub))
    for _ in range(WILT_AFTER + 2):
        grow_gardens(player_of(hub))
    assert not state["wilted"] and state["growth"] == 0
    hub.controller.handle("kerl", f"!home water {slot}")
    grow_gardens(player_of(hub))
    assert state["growth"] == 1
    hub.controller.handle("kerl", f"!home clear {utility}")
    for _ in range(WILT_AFTER):
        grow_gardens(player_of(hub))
    assert state["wilted"]


def test_a_big_plant_holds_the_feeder_until_pulled_free(
        data_path:Path) -> None:
    hub = GameHub(data_path)
    setup(hub)
    slot, state = planted(hub)
    ready(hub)
    state["growth"] = PLANTS["seductress"]["need"][BLOOM]
    text = hub.controller.handle("kerl", f"!home feed {slot}")
    assert "pull free" in text[0].text
    assert player_of(hub).profile["vine_held"]["left"] == 2
    blocked = hub.controller.handle("kerl", f"!home water {slot}")
    assert "Pull free first" in blocked[0].text
    assert "Pull free first" in hub.controller.town.held_text(
        player_of(hub))
    view = furnish.plant_view(player_of(hub), home(hub), slot, True)
    assert view["actions"][0]["command"] == "!home pull"
    first = hub.controller.handle("kerl", "!home pull")
    assert player_of(hub).profile["vine_held"]["left"] == 1
    assert first[0].text
    last = hub.controller.handle("kerl", "!home pull")
    assert "tear yourself" in last[0].text
    assert "vine_held" not in player_of(hub).profile
    assert "Nothing holds you" in hub.controller.handle(
        "kerl", "!home pull")[0].text
    hub.controller.handle("kerl", f"!home water {slot}")


def test_a_small_plant_does_not_hold(data_path:Path) -> None:
    hub = GameHub(data_path)
    setup(hub)
    slot, state = planted(hub)
    ready(hub)
    state["growth"] = PLANTS["seductress"]["need"][2]
    hub.controller.handle("kerl", f"!home feed {slot}")
    assert "vine_held" not in player_of(hub).profile


def test_the_overlay_shows_the_growth_progress(data_path:Path) -> None:
    hub = GameHub(data_path)
    setup(hub)
    slot, state = planted(hub)
    view = furnish.plant_view(player_of(hub), home(hub), slot, True)
    assert view["progress"].startswith("Seedling ░░ 0/2 → Vine")
    assert "thirsty" in view["progress"]
    hub.controller.handle("kerl", f"!home water {slot}")
    state["growth"] = 5
    text = garden.progress_text(state)
    assert "Bud ▓░ 5/6 → Bloom" in text and "watered" in text
    state["growth"] = 9
    state["hungry"] = 1
    text = garden.progress_text(state)
    assert "Overgrown ▓▓▓▓ fully grown" in text and "hungry 1/2" in text


def test_a_hungry_plant_looks_threatening(data_path:Path) -> None:
    hub = GameHub(data_path)
    setup(hub)
    slot, state = planted(hub)
    state["growth"] = PLANTS["seductress"]["need"][-1]
    assert "overgrown its stake" in rules.describe(home(hub))
    state["hungry"] = 1
    assert "gone quiet" in rules.describe(home(hub))
    state["hungry"] = 2
    assert "rustles with no wind" in rules.describe(home(hub))
    view = furnish.plant_view(player_of(hub), home(hub), slot, True)
    assert "rustles with no wind" in view["text"]

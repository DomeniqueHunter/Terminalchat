import asyncio
from pathlib import Path

from cursed_descent.content import ITEMS
from cursed_descent.furnishing import rules
from cursed_descent.furnishing.layout import LAYOUTS, slots_of
from cursed_descent.houses import home_of
from cursed_descent.locations.shop.location import buy_price
from cursed_descent.web.hub import GameHub
from tests.test_web_log_scope import connect


def setup(hub:GameHub, kind:str="hut", gold:int=10 ** 7) -> None:
    player = hub.controller.repository.load("kerl")
    player.gold = gold
    hub.controller.repository.save(player)
    hub.controller.handle("kerl", f"!home buy {kind}")


def player_of(hub:GameHub):
    return hub.controller.repository.load("kerl")


def home(hub:GameHub) -> dict:
    return home_of(player_of(hub), "last_light")


def send(hub:GameHub, client, text:str) -> None:
    asyncio.run(hub.handle(client, f'{{"action": "cmd", "viewer": "kerl", '
                                   f'"text": "{text}"}}'))


def test_every_house_type_has_rooms_a_garden_and_known_kinds() -> None:
    from cursed_descent.config import HOUSE_TYPES
    assert set(LAYOUTS) == set(HOUSE_TYPES)
    for key in LAYOUTS:
        slots = slots_of(key)
        assert any(slot.startswith("garden:") for slot in slots)
        assert any(kind == "bed" for kind in slots.values())


def test_furniture_items_are_complete() -> None:
    for key in rules.catalogue():
        assert ITEMS[key]["price"] > 0
    kinds = {item["furniture"] for item in ITEMS.values()
             if item.get("slot") == "furniture"}
    assert {"bed", "seat", "rug", "shelf", "table", "lamp", "decor",
            "bath", "stove", "plant"} <= kinds


def test_new_house_comes_with_starter_furniture(data_path:Path) -> None:
    hub = GameHub(data_path)
    setup(hub)
    placed = rules.furniture_of(home(hub))
    assert sorted(placed.values()) == ["straw_pallet", "tallow_candle",
                                       "three_legged_stool"]
    assert "Straw Pallet" in rules.describe(home(hub))


def test_place_swap_and_clear(data_path:Path) -> None:
    hub = GameHub(data_path)
    setup(hub)
    player = player_of(hub)
    player.inventory = ["feather_bed", "oak_table"]
    hub.controller.repository.save(player)
    bed = next(slot for slot, item in rules.furniture_of(home(hub)).items()
               if item == "straw_pallet")
    hub.controller.handle("kerl", "!home place living:5 2")
    wrong = hub.controller.handle("kerl", f"!home place {bed} 2")
    assert "does not fit" in wrong[0].text
    hub.controller.handle("kerl", f"!home place {bed} 1")
    player = player_of(hub)
    assert rules.furniture_of(home(hub))[bed] == "feather_bed"
    assert "straw_pallet" in player.inventory
    hub.controller.handle("kerl", f"!home clear {bed}")
    assert bed not in rules.furniture_of(home(hub))
    assert "feather_bed" in player_of(hub).inventory


def test_catalogue_order_costs_gold_and_skips_epic(data_path:Path) -> None:
    hub = GameHub(data_path)
    setup(hub, gold=10 ** 7)
    player = player_of(hub)
    player.inventory = []
    hub.controller.repository.save(player)
    before = player.gold
    hub.controller.handle("kerl", "!home carpenter wool_rug")
    hub.controller.handle("kerl", "!home carpenter canopy_bed")
    player = player_of(hub)
    assert player.inventory.count("wool_rug") == 1
    assert "canopy_bed" not in player.inventory
    price = buy_price("wool_rug", player)
    assert 0 < price <= ITEMS["wool_rug"]["price"]
    assert player.gold == before - price


def test_comfort_buff_on_sleep_and_storage_bonus(data_path:Path) -> None:
    hub = GameHub(data_path)
    setup(hub, "row")
    house = home(hub)
    slots = slots_of("row")
    house["furniture"] = {}
    beds = [s for s, k in slots.items() if k == "bed"]
    shelves = [s for s, k in slots.items() if k == "shelf"]
    house["furniture"][beds[0]] = "feather_bed"
    house["furniture"][shelves[0]] = "iron_bound_cabinet"
    assert rules.comfort_of(house) == 6
    assert rules.storage_bonus(house) == 9
    text = hub.controller.handle("kerl", "!home sleep")[0].text
    assert "Feather Bed" in text
    assert "home_rested" in player_of(hub).buffs
    account = hub.controller.repository.houses.account(home(hub))
    assert account.capacity == rules.capacity_of(home(hub))


def test_only_the_owner_changes_the_furnishing(data_path:Path) -> None:
    hub = GameHub(data_path)
    setup(hub)
    out = rules.private("x", player_of(hub))
    assert out
    from cursed_descent.houses import furnish_command
    guest = hub.controller.repository.load("Galactica")
    owner = player_of(hub)
    text = furnish_command(guest, owner, home(hub), "clear", ["living:0"],
                           hub.controller.repository)[0].text
    assert "Only the owner" in text


def test_overlay_shows_the_floor_plan_and_closes(data_path:Path) -> None:
    hub = GameHub(data_path)
    setup(hub, "townhouse")
    player = player_of(hub)
    player.inventory = ["feather_bed"]
    hub.controller.repository.save(player)
    hub.controller.handle("kerl", "!home")
    client = connect(hub, "kerl")
    send(hub, client, "!house open")
    page = hub.panels_for(client)
    assert 'id="house-backdrop"' in page
    for name in ("Living room", "Kitchen", "Bedroom", "Bath", "Garden"):
        assert name in page
    send(hub, client, "!house slot bedroom:0")
    page = hub.panels_for(client)
    assert "Feather Bed" in page and "!home place bedroom:0 1" in page
    assert "Carpenter" in page
    send(hub, client, "!house close")
    assert 'id="house-backdrop"' not in hub.panels_for(client)


def test_overlay_closes_when_you_leave_home(data_path:Path) -> None:
    hub = GameHub(data_path)
    setup(hub)
    hub.controller.handle("kerl", "!home")
    client = connect(hub, "kerl")
    send(hub, client, "!house open")
    hub.controller.handle("kerl", "!town")
    assert 'id="house-backdrop"' not in hub.panels_for(client)
    assert client.house is False


def test_loot_can_roll_furniture_without_crashing() -> None:
    from cursed_descent.dungeon import loot_stats
    for key in ("canopy_bed", "wool_rug"):
        loot_stats(key)


def test_catalogue_follows_the_selected_spot(data_path:Path) -> None:
    from cursed_descent.web import furnish
    hub = GameHub(data_path)
    setup(hub)
    hub.controller.handle("kerl", "!home")
    player = player_of(hub)
    page = furnish.overlay(hub.controller, player, "living:0")
    kinds = {rules.fits(row["command"].split()[-1], "bed")
             for row in page["catalogue"]}
    assert kinds == {True}
    assert len(furnish.overlay(hub.controller, player, "")["catalogue"]) > 10


def test_bath_resets_sweat_and_gives_a_buff(data_path:Path) -> None:
    hub = GameHub(data_path)
    setup(hub, "townhouse")
    house = home(hub)
    slot = next(s for s, k in slots_of("townhouse").items() if k == "bath")
    house["furniture"] = {slot: "wooden_tub"}
    player = player_of(hub)
    player.sweat = 80
    hub.controller.repository.save(player)
    text = hub.controller.handle("kerl", f"!home use {slot}")[0].text
    assert "Wooden Tub" in text
    player = player_of(hub)
    assert player.sweat == 0 and "home_bathed" in player.buffs


def test_use_needs_a_usable_piece(data_path:Path) -> None:
    hub = GameHub(data_path)
    setup(hub, "townhouse")
    text = hub.controller.handle("kerl", "!home use living:0")[0].text
    assert "nothing to use" in text


def test_kinky_slots_and_items_exist() -> None:
    assert sum(kind == "kinky" for kind in slots_of("manor").values()) >= 4
    assert not any(kind == "kinky" for kind in slots_of("hut").values())
    for key in ("facesitting_throne", "foot_smothering_box"):
        assert ITEMS[key]["furniture"] == "kinky"
    assert "foot_smothering_box" in rules.catalogue()
    assert "facesitting_throne" not in rules.catalogue()


def test_kinky_pieces_run_scenes_with_a_guest(data_path:Path) -> None:
    import random
    from cursed_descent.house_kinky import kinky_use
    hub = GameHub(data_path)
    setup(hub, "manor")
    repository = hub.controller.repository
    house = home(hub)
    slots = [s for s, k in slots_of("manor").items() if k == "kinky"]
    uses = ("facesitting_throne", "foot_smothering_box", "leather_bench",
            "spanking_horse")
    house["furniture"] = dict(zip(slots, uses))
    host = player_of(hub)
    guest = repository.load("galactica")
    for slot in house["furniture"]:
        for place in ("top", "bottom"):
            messages = kinky_use(host, guest, house, slot, repository,
                                 random.Random(1), "", place)
            assert len(messages[0].text) > 80
    assert "home_afterglow" in player_of(hub).buffs


def test_equal_roles_must_negotiate(data_path:Path) -> None:
    import random
    from cursed_descent.house_kinky import default_place, settle
    hub = GameHub(data_path)
    setup(hub)
    host = player_of(hub)
    guest = hub.controller.repository.load("galactica")
    host.profile["prefs"] = {"role": "dom", "flow": {}, "positions": []}
    guest.profile["prefs"] = {"role": "dom", "flow": {}, "positions": []}
    assert default_place(host, guest) == ""
    place, notes = settle(host, guest, "", "bedroom:0", "foot_smothering_box",
                          random.Random(1))
    assert place == "" and "top" in notes[0]
    guest.profile["prefs"]["role"] = "sub"
    assert default_place(host, guest) == "top"
    host.profile["prefs"]["role"] = "switch"
    guest.profile["prefs"]["role"] = "dom"
    assert default_place(host, guest) == "bottom"


def test_bed_and_new_pieces_exist() -> None:
    for key in ("leather_bench", "spanking_horse", "bondage_frame",
                "cage_bed"):
        assert ITEMS[key]["furniture"] == "kinky"
    assert ITEMS["feather_bed"]["use"] == "bed"


def test_npc_guest_must_like_the_act(data_path:Path) -> None:
    from cursed_descent.house_kinky import accepts
    hub = GameHub(data_path)
    setup(hub)
    guest = hub.controller.repository.load("galactica")
    guest.npc = "nobody_special"
    guest.profile["prefs"] = {"role": "switch", "flow": {"foot": "G"},
                              "positions": []}
    assert not accepts(guest, "foot")
    assert accepts(guest, "foot", "top")
    guest.profile["prefs"]["flow"]["foot"] = "T"
    assert accepts(guest, "foot")

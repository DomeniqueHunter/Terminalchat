import random

from cursed_descent.combat import choose_fate, fate_text
from cursed_descent.config import FUTA_GENDERS, VINE_FULL_SWEAT
from cursed_descent.content import BIOMES, ENEMIES, FATES, ITEMS
from cursed_descent.controller import GameController
from cursed_descent.dungeon import build_enemy, spawn_stage, vine_ambush
from cursed_descent.locations.pod_garden.location import pod_variant
from cursed_descent.models import Player
from cursed_descent.town_buildings.tavern.pods import price_of
from tests.test_enter_buildings import texts
from tests.test_maid import start_pair


def swamp() -> dict:
    return next(b for b in BIOMES if b["name"] == "Vine Swamp")


def party(controller:GameController, gender:str, sweat:int) -> list[Player]:
    start_pair(controller)
    kerl = controller.session.member("kerl")
    kerl.gender = gender
    kerl.sweat = sweat
    return [kerl]


def bloom(stage:int=17):
    return build_enemy(1, "pheromone_bloom", ENEMIES["pheromone_bloom"],
                       stage)


def plain(stage:int=17) -> list:
    return [build_enemy(1, "green_slime", ENEMIES["green_slime"], stage),
            build_enemy(2, "acid_ooze", ENEMIES["acid_ooze"], stage)]


def test_biome_monster_and_boss_exist() -> None:
    biome = swamp()
    assert biome["min_stage"] == 16
    assert "pheromone_bloom" in biome["enemies"]
    assert biome["boss"]["name"] == "Swamp Seductress Ylvara"
    assert ENEMIES["pheromone_bloom"]["name"] == "Pheromone Bloom"
    assert "podded" in FATES and "vined" in FATES


def test_the_bloom_is_not_a_stray_in_other_biomes() -> None:
    other = next(b for b in BIOMES if b["name"] == "Goblin Warrens")
    for _ in range(200):
        assert all(e.template_id != "pheromone_bloom"
                   for e in spawn_stage(30, "x", ""))
    assert "pheromone_bloom" not in other["enemies"]


def test_a_very_sweaty_futa_is_always_ambushed(
        controller:GameController) -> None:
    members = party(controller, "Herm", int(VINE_FULL_SWEAT * 0.7))
    for _ in range(20):
        enemies = plain()
        lines = vine_ambush(swamp(), members, enemies, 17)
        assert all(e.template_id == "pheromone_bloom" for e in enemies)
        assert any("🌿" in line for line in lines)


def test_a_dry_futa_and_other_genders_are_left_alone(
        controller:GameController) -> None:
    for gender, sweat in (("Herm", 0), ("Female", 100), ("Male", 100)):
        members = party(controller, gender, sweat)
        enemies = plain()
        vine_ambush(swamp(), members, enemies, 17)
        assert all(e.template_id != "pheromone_bloom" for e in enemies)


def test_a_mildly_sweaty_futa_is_sometimes_ambushed(
        controller:GameController) -> None:
    members = party(controller, "Shemale", int(VINE_FULL_SWEAT * 0.4))
    random.seed(1)
    hits = 0
    for _ in range(200):
        enemies = plain()
        vine_ambush(swamp(), members, enemies, 17)
        hits += any(e.template_id == "pheromone_bloom" for e in enemies)
    assert 40 < hits < 160


def test_no_ambush_outside_the_swamp(controller:GameController) -> None:
    members = party(controller, "Herm", 99)
    enemies = plain()
    other = next(b for b in BIOMES if b["name"] == "The Crypt")
    assert vine_ambush(other, members, enemies, 17) == []


def test_futas_are_podded_and_others_are_vined(
        controller:GameController) -> None:
    members = party(controller, "Herm", 0)
    kerl = members[0]
    kerl.last_hit_by = bloom()
    for gender in FUTA_GENDERS:
        kerl.gender = gender
        assert choose_fate(kerl, kerl.last_hit_by) == "podded"
    for gender in ("Male", "Female"):
        kerl.gender = gender
        assert choose_fate(kerl, kerl.last_hit_by) == "vined"


def test_the_pod_variant_is_read_from_the_fate_text(
        controller:GameController) -> None:
    members = party(controller, "Herm", 0)
    kerl = members[0]
    seen = set()
    for _ in range(400):
        seen.add(pod_variant(fate_text(kerl, "podded", bloom())))
    assert seen == {"classic", "pumpkin", "tuber", "cocoon", "nectar", "flytrap",
                    "burrow"}


def podded_entry(controller:GameController, **extra) -> dict:
    remains = controller.session.remains
    remains.add("Lorelei", "Herm", "podded", 17, "Pheromone Bloom",
                "vines", "old-run", detail="pumpkin")
    entry = remains.entries[-1]
    entry.update(extra)
    return entry


def test_the_pod_garden_lists_and_harvests_pods_once(
        controller:GameController) -> None:
    start_pair(controller)
    entry = podded_entry(controller)
    session = controller.session
    session.events.offer_location("pod_garden", 1.0)
    assert "harvest 1" in session.events.available()
    assert "Pumpkin Pod" in texts(controller.handle("kerl", "!examine",
                                                    now=2.0))
    kerl = session.member("kerl")
    kerl.inventory = []
    reply = texts(controller.handle("kerl", "!harvest 1", now=3.0))
    assert "pod_pumpkin" in kerl.inventory
    assert entry["harvested"] is True
    assert "Pumpkin Pod" in reply
    assert "harvest 1" not in session.events.available()


def test_a_pod_returns_the_preserved_gear(
        controller:GameController) -> None:
    start_pair(controller)
    entry = podded_entry(controller, item="leather_boots", looted=False)
    session = controller.session
    session.events.offer_location("pod_garden", 1.0)
    kerl = session.member("kerl")
    kerl.inventory = []
    controller.handle("kerl", "!harvest 1", now=3.0)
    assert "leather_boots" in kerl.inventory and entry["looted"]


def test_the_garden_without_pods_only_offers_to_leave(
        controller:GameController) -> None:
    start_pair(controller)
    session = controller.session
    session.events.offer_location("pod_garden", 1.0)
    assert session.events.available() == ["examine", "depart"]


def test_the_tavern_pays_well_for_pods(controller:GameController) -> None:
    kerl = controller.repository.load("kerl")
    kerl.inventory = ["pod_classic", "pod_pumpkin"]
    kerl.gold = 0
    controller.repository.save(kerl)
    controller.handle("kerl", "!tavern")
    reply = texts(controller.handle("kerl", "!sellpods 1"))
    kerl = controller.repository.load("kerl")
    assert kerl.inventory == ["pod_pumpkin"]
    assert kerl.gold == price_of("pod_classic")
    assert price_of("pod_classic") > ITEMS["pod_classic"]["price"]
    assert "cheers" in reply
    controller.handle("kerl", "!sellpods all")
    kerl = controller.repository.load("kerl")
    assert kerl.inventory == []
    assert kerl.gold == price_of("pod_classic") + price_of("pod_pumpkin")


def test_the_pod_garden_only_appears_in_the_vine_swamp() -> None:
    from cursed_descent.locations.venues import location_at
    random.seed(3)
    elsewhere = {location_at(48, frozenset(), "The Crypt")
                 for _ in range(300)}
    assert "pod_garden" not in elsewhere
    inside = [location_at(48, frozenset(), "Vine Swamp")
              for _ in range(300)]
    assert inside.count("pod_garden") > 40


def test_every_pod_variant_has_its_own_look_and_harvest_text() -> None:
    from cursed_descent.locations.pod_garden.content import (
        HARVEST_SCENES, KIND_NAMES, POD_LOOKS,
    )
    assert set(KIND_NAMES) == set(POD_LOOKS) == set(HARVEST_SCENES)
    assert len({text for text in POD_LOOKS.values()}) == len(POD_LOOKS)


def swamp_seed(stage:int) -> str:
    from cursed_descent.dungeon import current_biome
    return next(str(seed) for seed in range(500)
                if current_biome(stage, str(seed), "")["name"]
                == "Vine Swamp")


def test_swamp_groups_are_either_all_vines_or_no_vines() -> None:
    seed = swamp_seed(17)
    kinds = set()
    for _ in range(300):
        enemies = spawn_stage(17, seed, "")
        templates = {e.template_id for e in enemies}
        assert templates == {"pheromone_bloom"} or (
            "pheromone_bloom" not in templates)
        kinds.add("pheromone_bloom" in templates)
    assert kinds == {True, False}


def test_a_bloom_never_fights_next_to_other_monsters(
        controller:GameController) -> None:
    members = party(controller, "Male", 0)
    mixed = plain() + [bloom()]
    vine_ambush(swamp(), members, mixed, 17)
    assert [e.template_id for e in mixed] == ["pheromone_bloom"]


def test_vines_drop_seductress_seeds(controller:GameController) -> None:
    from cursed_descent.dungeon import seed_drops as vine_seeds
    from cursed_descent.plants.seductress.drops import DROP
    members = party(controller, "Female", 0)
    assert ITEMS["seductress_seed"]["seed"] == "seductress"
    blooms = [bloom(), bloom(), bloom(), bloom()]
    counts = set()
    for _ in range(300):
        members[0].inventory = []
        lines = vine_seeds(blooms, members)
        counts.add(len(lines))
        assert members[0].inventory.count("seductress_seed") == len(lines)
    assert counts == set(range(DROP["max"] + 1))
    assert vine_seeds(plain(), members) == []
    blooms[0].boss = True
    assert len(vine_seeds(blooms, members)) == DROP["boss"]


def test_the_seed_cannot_be_eaten(controller:GameController) -> None:
    members = party(controller, "Female", 0)
    members[0].inventory = ["seductress_seed"]
    controller.repository.save(members[0])
    output = texts(controller.handle("kerl", "!consume Seductress Seed"))
    assert "Usage: consume" in output

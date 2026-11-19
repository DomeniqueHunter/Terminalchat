from .content import ITEMS
from .config import AFFINITY_NAMES, EQUIPMENT_SLOTS, STAT_NAMES
from .formulas import enemy_scale, max_hp, max_mana
from .models import Message, Player


GODDESS = "Claudia"
POWER_PER_SCALE = 60000
AFFINITY_CAP = 250
START_STAGE = 100
GOLD = 1_000_000
LEVEL = 100


def best_item(slot:str, gender:str) -> str | None:
    found = [
        (item.get("damage", 0) + item.get("armor", 0)
         + item.get("allure", 0), item_id)
        for item_id, item in ITEMS.items()
        if item.get("slot") == slot and item.get("for", "both") in (
            "both", "lady" if gender == "Female" else "gent")]
    return max(found)[1] if found else None


def parse_stage(args:list[str]) -> int:
    if args and args[0].isdigit():
        return max(1, int(args[0]))
    return START_STAGE


def build_goddess(player:Player, stage:int) -> None:
    power = max(100, round(enemy_scale(stage) * POWER_PER_SCALE))
    player.gender = "Female"
    player.level = LEVEL
    player.exp = 0
    player.free_points = 0
    player.gold = GOLD
    player.stats = {stat: power for stat in STAT_NAMES}
    player.stats["agility"] = 100
    player.affinity = {name: AFFINITY_CAP for name in AFFINITY_NAMES}
    player.equipment = {slot: best_item(slot, player.gender)
                        for slot in EQUIPMENT_SLOTS}
    player.alive = True
    player.hp = max_hp(player)
    player.mana = max_mana(player)


def make_goddess(repository, args:list[str], sender:str) -> list[Message]:
    stage = parse_stage(args)
    player = repository.load(GODDESS)
    created = player is None
    if created:
        player = Player(name=GODDESS, first_name=GODDESS, gender="Female")
        repository.add(player)
    build_goddess(player, stage)
    repository.save(player)
    verb = "created" if created else "reset"
    return [Message(
        f"✨ {GODDESS} {verb}: level {LEVEL}, power sized for stage "
        f"{stage} (stats {player.stats['strength']}, melee/magic/dodge/"
        f"guard/heal {AFFINITY_CAP}), best gear, {GOLD} gold. "
        f"Lobby with [lobby] as {GODDESS}.", sender)]

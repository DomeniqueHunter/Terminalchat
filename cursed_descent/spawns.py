from importlib import import_module

from . import seasons
from .spawn_rule import SpawnRule


SPAWN_MODULES = (
    "events.wanderer.spawn",
    "events.ogre.spawn",
    "events.lich.spawn",
    "events.adept.spawn",
    "events.recruiter.spawn",
    "events.null_master.spawn",
    "locations.lodge.spawn",
    "locations.boutique.spawn",
    "locations.butcher.spawn",
    "locations.farm.spawn",
    "locations.couch.spawn",
    "locations.bivouac.spawn",
    "locations.brewery.spawn",
    "locations.sweatery.spawn",
    "locations.smokery.spawn",
    "locations.mage_tower.spawn",
    "locations.wardrobe.spawn",
    "locations.throne.spawn",
    "locations.glory_hole.spawn",
    "locations.wedding.spawn",
    "locations.fisher.spawn",
    "locations.grill.spawn",
    "locations.dairy.spawn",
    "locations.privy.spawn",
    "locations.pod_garden.spawn",
    "events.maid.spawn",
    "events.caravaneer.spawn",
    "events.drainer.spawn",
    "events.mrs_claus.spawn",
    "locations.north_pole.spawn",
)


def load_rules() -> list[SpawnRule]:
    rules: list[SpawnRule] = []
    for module in SPAWN_MODULES:
        rules += import_module(f".{module}", __package__).RULES
    kinds = [rule.kind for rule in rules]
    if len(kinds) != len(set(kinds)):
        raise ValueError("duplicate spawn rule kind")
    return sorted(rules, key=lambda rule: rule.order)


SPAWN_RULES = load_rules()
RULES_BY_KIND = {rule.kind: rule for rule in SPAWN_RULES}


AWAY_KINDS: set[str] = set()


def eligible(stage:int, slot:str="event") -> list[SpawnRule]:
    return [rule for rule in SPAWN_RULES
            if rule.slot == slot and rule.allows(stage)
            and rule.kind not in AWAY_KINDS
            and seasons.active(rule.season)]


def min_stage(kind:str) -> int:
    return RULES_BY_KIND[kind].min_stage

from dataclasses import dataclass, field
from typing import Any

from .config import (
    INVENTORY_SIZE,
    AFFINITY_NAMES, DEFAULT_AGE, DEFAULT_GENDER, EQUIPMENT_SLOTS, START_FREE_POINTS,
    START_GOLD, START_STAT_VALUE, STAT_NAMES,
)
from .body import DEFAULT_BODY, normalize_body
from .content import COMBO_TITLES, ITEMS, TITLES
from .identity import is_character, new_id
from .items import item_from_json, item_to_json, pack_items, unpack_items
from .migrations import SCHEMA_VERSION, migrate_player
from .needs import new_needs
from .settings import fill


LEGACY_AFFINITY = {"fire": "magic"}


@dataclass
class Message:
    text: str
    recipient: str = ""
    style: str = ""
    place: str = ""
    witness: str = ""
    lobby: str = ""

    def __post_init__(self) -> None:
        self.text = fill(self.text)
        self.witness = fill(self.witness)

    @property
    def is_private(self) -> bool:
        return bool(self.recipient)


@dataclass
class Action:
    kind: str
    target: str = ""
    spell: str = ""
    item: str = ""


@dataclass
class Player:
    name: str
    id: str = field(default_factory=new_id)
    account_id: str | None = None
    first_name: str = ""
    last_name: str = ""
    gender: str = DEFAULT_GENDER
    level: int = 1
    exp: int = 0
    free_points: int = START_FREE_POINTS
    gold: int = START_GOLD
    body: dict[str, Any] = field(default_factory=lambda: dict(DEFAULT_BODY))
    stats: dict[str, int] = field(
        default_factory=lambda: {stat: START_STAT_VALUE for stat in STAT_NAMES}
    )
    affinity: dict[str, int] = field(
        default_factory=lambda: {name: 0 for name in AFFINITY_NAMES}
    )
    equipment: dict[str, str | None] = field(
        default_factory=lambda: {slot: None for slot in EQUIPMENT_SLOTS}
    )
    inventory: list[str] = field(default_factory=lambda: ["potion_small"] * 2)
    records: dict[str, int] = field(
        default_factory=lambda: {"deepest_stage": 0, "runs": 0, "kills": 0}
    )
    deaths: dict[str, int] = field(default_factory=dict)
    pregnant: str = ""
    offspring: list[dict[str, str]] = field(default_factory=list)
    body_mods: dict[str, Any] = field(default_factory=dict)
    enhancements: list[str] = field(default_factory=list)
    hp: int = 0
    mana: int = 0
    alive: bool = True
    action: Action | None = None
    last_hit_by: Any = None
    last_fate: str = ""
    last_fate_text: str = ""
    soul_weapon: str = ""
    sweat: int = 0
    buffs: list[str] = field(default_factory=list)
    body_backup: dict[str, Any] | None = None
    needs: dict[str, int] = field(default_factory=new_needs)
    npc: str = ""
    age: int = DEFAULT_AGE
    spouse: str = ""
    personality: str = ""
    race: str = ""
    profile: dict[str, Any] = field(default_factory=dict)
    bag_extra: int = 0

    @property
    def bag_size(self) -> int:
        return INVENTORY_SIZE + self.bag_extra

    def __post_init__(self) -> None:
        normalize_body(self.body)

    @property
    def full_name(self) -> str:
        parts = [part for part in (self.first_name, self.last_name) if part]
        return " ".join(parts) or self.name

    def owns(self, entry:dict[str, Any]) -> bool:
        return is_character(entry, self.id, self.name)

    @property
    def title(self) -> str:
        ranked = sorted(self.affinity.items(), key=lambda kv: kv[1],
                        reverse=True)
        (top, top_value), (second, second_value) = ranked[0], ranked[1]
        if top_value < 20:
            return "Novice"
        if second_value >= top_value * 0.6:
            return COMBO_TITLES[frozenset({top, second})]
        return TITLES[top]

    def fix_equipment(self) -> None:
        for slot, item_id in list(self.equipment.items()):
            if item_id is None:
                continue
            if item_id not in ITEMS:
                self.equipment[slot] = None
                continue
            target = ITEMS[item_id]["slot"]
            if target == slot:
                continue
            self.equipment[slot] = None
            if self.equipment.get(target) is None:
                self.equipment[target] = item_id
            else:
                self.inventory.append(item_id)

    def add_affinity(self, name:str, amount:int=1) -> None:
        self.affinity[name] = self.affinity.get(name, 0) + amount

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "id": self.id,
            "account_id": self.account_id,
            "name": self.name,
            "needs": self.needs,
            "npc": self.npc,
            "age": self.age,
            "spouse": self.spouse,
            "personality": self.personality,
            "race": self.race,
            "profile": self.profile,
            "bag_extra": self.bag_extra,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "gender": self.gender,
            "level": self.level,
            "exp": self.exp,
            "free_points": self.free_points,
            "gold": self.gold,
            "body": self.body_backup or self.body,
            "stats": self.stats,
            "affinity": self.affinity,
            "equipment": {slot: item_to_json(item) if item else None
                          for slot, item in self.equipment.items()},
            "inventory": pack_items(self.inventory),
            "records": self.records,
            "deaths": self.deaths,
            "pregnant": self.pregnant,
            "offspring": self.offspring,
            "body_mods": self.body_mods,
            "enhancements": self.enhancements,
        }

    @classmethod
    def from_dict(cls, data:dict[str, Any]) -> "Player":
        data, _ = migrate_player(data)
        player = cls(name=data["name"])
        player.id = data["id"]
        player.account_id = data.get("account_id")
        player.needs.update(data["needs"])
        player.npc = data.get("npc", "")
        player.age = data.get("age", DEFAULT_AGE)
        player.spouse = data.get("spouse", "")
        player.personality = data.get("personality", "")
        player.race = data.get("race", "")
        player.profile = dict(data.get("profile", {}))
        player.bag_extra = data.get("bag_extra", 0)
        player.first_name = data["first_name"]
        player.last_name = data["last_name"]
        player.gender = data.get("gender", DEFAULT_GENDER)
        player.level = data.get("level", 1)
        player.exp = data.get("exp", 0)
        player.free_points = data.get("free_points", 0)
        player.gold = data.get("gold", START_GOLD)
        stored = dict(DEFAULT_BODY)
        stored.update(data.get("body", {}))
        player.body = normalize_body(stored)
        player.stats.update(data.get("stats", {}))
        for name, value in data.get("affinity", {}).items():
            name = LEGACY_AFFINITY.get(name, name)
            if name in player.affinity:
                player.affinity[name] = max(player.affinity[name], value)
        for slot, item_id in data.get("equipment", {}).items():
            if slot in player.equipment:
                player.equipment[slot] = (
                    item_from_json(item_id) if item_id else None)
        player.fix_equipment()
        player.inventory = unpack_items(data.get("inventory", []))
        player.records.update(data.get("records", {}))
        player.deaths = dict(data["deaths"])
        player.pregnant = data.get("pregnant", "")
        player.offspring = list(data.get("offspring", []))
        player.body_mods = dict(data.get("body_mods", {}))
        player.enhancements = list(data.get("enhancements", []))
        return player


@dataclass
class Enemy:
    uid: int
    template_id: str
    name: str
    max_hp: int
    hp: int
    attack: int
    defense: int
    agility: int
    exp: int
    fates: list[str]
    actions: list[tuple[str, int]]
    boss: bool = False
    tribe: str = "monsters"
    melee_mult: float = 1.0
    magic_mult: float = 1.0
    mindless: bool = False
    intent: str = ""
    intent_target: str = ""
    killed_by: str = ""
    origin: str = ""
    temp_id: str = ""

    @property
    def alive(self) -> bool:
        return self.hp > 0

    @property
    def label(self) -> str:
        return f"[{self.uid}] {self.name}"

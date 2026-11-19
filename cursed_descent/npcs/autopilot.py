from ..config import NPC_GUARD_HP_RATIO, NPC_HEAL_HP_RATIO
from ..content import SPELLS
from ..formulas import knows_spell, max_hp
from ..models import Enemy, Player


def weakest_enemy(enemies:list[Enemy]) -> Enemy | None:
    living = [enemy for enemy in enemies if enemy.alive]
    return min(living, key=lambda enemy: (enemy.hp, enemy.uid),
               default=None)


def weakest_ally(party:list[Player]) -> Player | None:
    living = [member for member in party if member.alive]
    return min(living, key=lambda member: member.hp / max(max_hp(member), 1),
               default=None)


def affordable(player:Player, kind:str, target:str) -> list[str]:
    return [spell_id for spell_id, spell in SPELLS.items()
            if spell["kind"] == kind and spell["target"] == target
            and spell["mana"] <= player.mana and knows_spell(player, spell_id)]


def best_spell(player:Player, kind:str, target:str) -> str:
    options = affordable(player, kind, target)
    return max(options, key=lambda spell_id: SPELLS[spell_id]["mana"],
               default="")


def heal_choice(player:Player, party:list[Player]) -> tuple[str, list[str]]:
    patient = weakest_ally(party)
    if patient is None:
        return "", []
    ratio = patient.hp / max(max_hp(patient), 1)
    if ratio > NPC_HEAL_HP_RATIO:
        return "", []
    circle = best_spell(player, "heal", "allies")
    hurt = [member for member in party if member.alive
            and member.hp / max(max_hp(member), 1) <= NPC_HEAL_HP_RATIO]
    if circle and len(hurt) >= 2:
        return "cast", [circle]
    single = best_spell(player, "heal", "ally")
    if single:
        return "cast", [single, patient.name]
    return "", []


def autopilot_choice(player:Player, party:list[Player],
                     enemies:list[Enemy]) -> tuple[str, list[str]]:
    kind, args = heal_choice(player, party)
    if kind:
        return kind, args
    if player.hp / max(max_hp(player), 1) <= NPC_GUARD_HP_RATIO:
        return "guard", []
    target = weakest_enemy(enemies)
    if target is None:
        return "guard", []
    living = [enemy for enemy in enemies if enemy.alive]
    area = best_spell(player, "damage", "all")
    if area and len(living) >= 3:
        return "cast", [area]
    single = best_spell(player, "damage", "single")
    if single:
        return "cast", [single, str(target.uid)]
    return "hit", [str(target.uid)]

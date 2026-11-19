TITLES = {
    "melee": "Berserker",
    "magic": "Mage",
    "dodge": "Rogue",
    "guard": "Guardian",
    "heal": "Cleric",
}

COMBO_TITLES = {
    frozenset({"melee", "magic"}): "Battlemage",
    frozenset({"heal", "guard"}): "Paladin",
    frozenset({"melee", "dodge"}): "Blade Dancer",
    frozenset({"magic", "heal"}): "Druid",
    frozenset({"melee", "guard"}): "Knight",
    frozenset({"dodge", "magic"}): "Warlock",
    frozenset({"dodge", "guard"}): "Survivor",
    frozenset({"heal", "melee"}): "War Priest",
    frozenset({"heal", "dodge"}): "Wandering Healer",
    frozenset({"magic", "guard"}): "Rune Warden",
}

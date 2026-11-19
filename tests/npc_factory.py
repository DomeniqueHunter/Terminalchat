import random

from cursed_descent.npcs.generator import make_maid, make_mercenary


def merc(name:str="Brom", focus:tuple[str, str]=("strength", "vitality"),
         gender:str="Male", seed:int=1):
    npc = make_mercenary(random.Random(seed), set(), gender)
    npc.name = npc.first_name = name
    npc.last_name = "Ironhide"
    npc.profile["focus"] = list(focus)
    base = 5
    for stat in npc.stats:
        npc.stats[stat] = base
    for index, stat in enumerate(focus):
        npc.stats[stat] = base + (5, 4)[index]
    return npc


def maid(name:str="Lotte", seed:int=1):
    npc = make_maid(random.Random(seed), set())
    npc.name = npc.first_name = name
    npc.age = 24
    npc.personality = "hard-working, cheerful, stubborn"
    return npc


def add_merc(controller, name:str="Brom", **kwargs):
    npc = merc(name, **kwargs)
    controller.repository.add(npc)
    return npc

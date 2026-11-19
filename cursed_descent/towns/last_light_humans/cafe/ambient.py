import random
from dataclasses import dataclass

from ....config import (
    AMBIENT_ACTION_CHANCE, AMBIENT_DEATH_CHANCE, CAFE_GUEST_WEIGHT,
    MIN_NPC_AGE,
)
from ....town_buildings.bodies import body_line
from .content import CLENCH_PLEAS, CRUSH_POPS, GUEST_NAMES
from .guests import Guest, guest_butt
from .stools import NAMES, Stool, describe, new_stool


SCENES = (
    "{lady} sweeps in, lowers herself onto {man} without a glance, and "
    "orders tea.",
    "{lady} sits down heavily on {man}. He grunts. She asks for the cake "
    "menu.",
    "{lady} arrives with her husband {man} on a leash and settles onto "
    "his face. 'Do not wriggle, dear.'",
    "{lady} brings her grown-up son {man} along, sits on him, and "
    "chats with the next table about the weather.",
    "{lady} eats a slice of cheesecake on top of {man}. Crumbs rain onto "
    "his face; he does not complain.",
    "{lady} finishes her cream puff, pats {man}'s head, leaves a tip and "
    "sails out of the café.",
    "{lady} rises with a satisfied sigh. {man} lies flat and breathes "
    "for a long moment.",
    "{man} whimpers somewhere under {lady}, a thin muffled sound.",
    "{man} taps weakly on the floorboards. {lady} laughs and sits a "
    "little deeper.",
    "The ladies laugh and clink their teacups. Nobody is in a hurry.",
    "A stool-boy carries a tray of cakes between the ladies. Everybody is "
    "in a good mood.",
    "{lady} shifts her weight on {man}. 'Oh, this is lovely,' she tells "
    "her friend.",
    "{man} gasps under {lady}'s weight: 'Please… a moment…' She keeps "
    "chatting.",
    "{lady} drags a second chair over, props her feet on {man}'s back, "
    "and sips her tea.",
)


GIRLFRIENDS = ("Anya", "Lena", "Mira", "Svea", "Tilda", "Nora", "Ilka",
               "Runa")
FAMILY_SCENES = (
    "{lady} arrives with her grown son {man} and his girlfriend {gf}. "
    "'Ladies first,' she says, and sits on {man}'s face herself while "
    "{gf} giggles and waits her turn.",
    "{lady} brings her grown son {man} and his girlfriend {gf}. {gf} "
    "takes the first turn on his face while {lady} supervises: 'Deeper, "
    "dear. He is used to more.'",
    "{lady} and {gf} swap places on {man}'s face. He is {lady}'s son and "
    "{gf}'s boyfriend, and he whimpers for air under both of them.",
    "{lady} sits on her grown son {man}, her feet on {gf}'s lap. '"
    "{gf}, dear, you are next. He does not mind – do you, {man}?'",
    "{gf} sits on her boyfriend {man}'s face, and {lady}, his mother, "
    "nods in approval. 'Good girl. Hold him there.'",
)


MOM_LINES = ("Mom knows best.", "Mom was here first.")
GIRLFRIEND_LINES = ("Now he is my seat~",)


@dataclass
class Family:
    lady: Guest
    girlfriend: Guest
    son: Stool


def make_family(rng:random.Random, regulars=None) -> Family:
    known = regulars.pick("cafe", rng) if regulars is not None else None
    if known is not None:
        known = regulars.remember("cafe", known)
        lady = Guest(known["name"], known.get("weight", 100),
                     known.get("butt", 130), cruel=known.get("cruel", 1),
                     kills=known.get("kills", 0),
                     age=known.get("age", rng.randint(40, 64)),
                     height=known.get("height", rng.randint(150, 185)),
                     sweat=known.get("sweat", 0),
                     musk=known.get("musk", 0))
        weight = lady.weight
    else:
        weight = rng.randint(*CAFE_GUEST_WEIGHT)
        lady = Guest(rng.choice(GUEST_NAMES), weight,
                     guest_butt(weight, rng), age=rng.randint(40, 64),
                     height=rng.randint(150, 185))
    girl_weight = rng.randint(50, 85)
    girlfriend = Guest(rng.choice(GIRLFRIENDS), girl_weight,
                       max(95, guest_butt(girl_weight, rng) - 20),
                       age=rng.randint(MIN_NPC_AGE, 30),
                       height=rng.randint(155, 182))
    son = new_stool(rng, (MIN_NPC_AGE, 30))
    if known is not None and known.get("son"):
        son.name = known["son"]
    if known is not None and known.get("girlfriend"):
        girlfriend.name = known["girlfriend"]
    return Family(lady, girlfriend, son)


def family_scene(rng:random.Random, family:Family | None=None) -> str:
    family = family or make_family(rng)
    scene = rng.choice(FAMILY_SCENES).format(
        lady=family.lady.name, man=family.son.name,
        gf=family.girlfriend.name)
    lines = [f"{family.lady.name}: '{rng.choice(MOM_LINES)}'",
             f"{family.girlfriend.name}: '{rng.choice(GIRLFRIEND_LINES)}'"]
    rng.shuffle(lines)
    return "\n".join([scene] + lines)


def family_look(family:Family, wanted:str) -> str:
    name = wanted.strip().casefold()

    def hit(person:str) -> bool:
        return name == person.casefold() or name in person.casefold(
        ).replace(".", "").split()
    lady, girl, son = family.lady, family.girlfriend, family.son
    if hit(lady.name):
        return (f"{lady.name}: {body_line(lady.age, lady.height, lady.weight)}"
                f", {lady.butt} cm of rear – {son.name}'s mother, "
                f"firmly in charge."
                + (f" Kills on her ledger: {lady.kills}."
                   if lady.kills else ""))
    if hit(girl.name):
        return (f"{girl.name}: {body_line(girl.age, girl.height, girl.weight)}"
                f", {girl.butt} cm of rear – {son.name}'s girlfriend, "
                f"grinning and waiting for her turn.")
    if hit(son.name):
        return (f"{describe(son)} He is {lady.name}'s son and "
                f"{girl.name}'s boyfriend – stamina {son.stamina}.")
    return ""


ACTION_SCENES = {
    "clench": "{lady} clenches her cheeks around {man}'s face and grinds "
              "down. {plea}",
    "wiggle": "{lady} wiggles her rear slowly over {man}'s mouth and nose, "
              "smearing herself over his face. {plea}",
    "kiss": "{man} kisses {lady}'s rear with devotion. She purrs: "
            "'Good boy.'",
    "french": "{man} kisses {lady}'s rear a third time and his tongue "
              "slides in deep, wet and open-mouthed. {lady} gasps and "
              "rolls her hips down: 'Oh, you filthy darling…'",
    "lick": "{man} licks {lady}'s asshole slowly and thoroughly. {taste}",
    "crush": "{lady} clamps down with everything she has. Something gives "
             "way under her with a wet crack, and {man} goes still. "
             "{pop} Bertha clicks her tongue: 'Waste not.'",
}
ACTION_TASTES = (
    "She smells of soap and warm skin, and tastes clean and faintly "
    "salty.",
    "She smells of warm skin and a hint of sweat; she tastes salty and "
    "a little sweet.",
    "A musky, sweaty warmth hangs around them; she tastes salty, earthy "
    "and unmistakably of herself.",
    "The smell is thick and heady, sweat and musk together, and the taste "
    "clings to his tongue.",
    "The smell hits like a wall, heavy sweat and ripe musk, and the taste "
    "is overwhelming, bitter-salty and strong.",
)
QUIET_ACTIONS = ("clench", "wiggle", "kiss", "french", "lick")


def action_scene(rng:random.Random) -> str:
    kind = ("crush" if rng.random() < AMBIENT_DEATH_CHANCE
            else rng.choice(QUIET_ACTIONS))
    man = rng.choice(NAMES)
    plea = rng.choice(CLENCH_PLEAS[rng.randint(1, 3)]).format(seat=man)
    return ACTION_SCENES[kind].format(
        lady=rng.choice(GUEST_NAMES), man=man, plea=plea,
        taste=rng.choice(ACTION_TASTES), pop=rng.choice(CRUSH_POPS))


def ambient_line(rng:random.Random) -> str:
    if rng.random() < AMBIENT_ACTION_CHANCE:
        return action_scene(rng)
    if rng.random() < 0.25:
        return family_scene(rng)
    scene = rng.choice(SCENES)
    return scene.format(lady=rng.choice(GUEST_NAMES),
                        man=rng.choice(NAMES))

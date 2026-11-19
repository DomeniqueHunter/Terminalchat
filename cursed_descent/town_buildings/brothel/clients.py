import random
from dataclasses import dataclass, field

from ...models import Message, Player
from ...config import (
    BROTHEL_HOUSE_GUEST_CHANCE, BROTHEL_PURSE, HOUSE_GUEST_BUILDINGS,
    MIN_NPC_AGE, REGULARS_AUTO, REGULAR_BANNED_GENDERS, VISIT_GUEST_CHANCE,
)
from ...npcs.visiting import quirk_line
from ...towns import town_key
from ...body import bust_label
from ..body_taste import taste_hints
from ..bodies import body_line, client_body, in_pref, pref_of
from .content import (
    CLIENTS, FEMININE_CLIENTS, HOUSE_GUEST_HELLOS, OPERATOR_GUEST_HELLOS,
)
from .dialogue import greeting, pick_temper, speaker
from .dialogue_content import TONES
from .practices import can_do, option_text, options_for
from .practices_content import DOMINANT_ACTS
from ...preferences import pick_likes
from ..regular_body import (
    body_values, random_gender, smell_note, smell_word,
)


FEMININE = ("Female", "Herm", "Shemale")


@dataclass
class Client:
    name:str
    dominated:bool
    likes:tuple[tuple[str, str], ...]
    temper:str = "playful"
    hello:str = ""
    visits:int = 0
    age:int = 0
    height:int = 0
    weight:int = 0
    history:dict = field(default_factory=dict)
    dominant:bool = False
    purse:int = 0
    player:str = ""
    belly:int = 0
    gender:str = "Male"
    bust:int = 0
    endowment:int = 0
    sweat:int = 0
    musk:int = 0
    npc:str = ""


def other_side(role:str) -> str:
    return "receive" if role == "give" else "give"


def client_can(client:"Client", act:str, role:str) -> bool:
    return can_do(client.gender, act, other_side(role),
                  {"bust": client.bust})


def client_options(player:Player, client:"Client"
                   ) -> list[tuple[str, str]]:
    town = town_key(player)
    return [(act, role) for act, role in options_for(
        player.gender, player.body, town) if client_can(client, act, role)]


def pool_for(player:Player, dominated:bool, dominant:bool=False,
             gender:str="Male", bust:int=0) -> list[tuple[str, str]]:
    options = [(act, role) for act, role in options_for(
        player.gender, player.body, town_key(player))
        if can_do(gender, act, other_side(role), {"bust": bust})]
    if dominant:
        return [(act, role) for act, role in options
                if act in DOMINANT_ACTS and role == "receive"]
    return [(act, role) for act, role in options
            if not dominated or (act in DOMINANT_ACTS and role == "give")]


def fits_mode(dominated:bool, dominant:bool, mode:str) -> bool:
    if mode == "domina":
        return dominated
    if mode == "sub":
        return dominant
    return not dominant


def from_record(player:Player, record:dict,
                rng:random.Random, mode:str="") -> Client | None:
    dominated = bool(record.get("dominated", False))
    dominant = bool(record.get("dominant", False))
    if not fits_mode(dominated, dominant, mode):
        return None
    traits = body_values("brothel", record["name"])
    gender = record.get("gender", traits["gender"])
    bust = record.get("bust", traits["bust"])
    pool = pool_for(player, dominated, dominant, gender, bust)
    likes = tuple(tuple(like) for like in record.get("likes", ()))
    if not likes and len(pool) >= 1:
        likes = pick_likes(player, pool, rng)
    if not all(like in pool for like in likes):
        return None
    temper = record.get("temper") or (
        rng.choice(("gruff", "playful")) if dominant
        else pick_temper(dominated, rng))
    age, height, weight = client_body(rng)
    return Client(record["name"], dominated, likes, temper,
                  greeting(temper, rng), record.get("visits", 1),
                  max(MIN_NPC_AGE, record.get("age", age)),
                  record.get("height", height),
                  record.get("weight", weight),
                  dict(record.get("history", {})), dominant,
                  rng.randint(*BROTHEL_PURSE), record.get("belly", 0),
                  gender=gender, bust=bust,
                  endowment=record.get("endowment", traits["endowment"]),
                  sweat=record.get("sweat", traits["sweat"]),
                  musk=record.get("musk", traits["musk"]))


def house_guests(player:Player) -> tuple[list, object]:
    from ...towns import town_of
    from ...towns.localize import operator_of
    town = town_of(player)
    owner = operator_of(town, "brothel")
    return [person for person in town.residents
            if person.building in HOUSE_GUEST_BUILDINGS
            and (person.building != "brothel" or person is owner)], owner


def house_guest(player:Player, rng:random.Random,
                mode:str="") -> Client | None:
    people, owner = house_guests(player)
    if not people:
        return None
    person = rng.choice(people)
    dominant = mode == "sub"
    dominated = mode == "domina" or (mode == "" and rng.random() < 0.4)
    values = dict(person.body)
    traits = body_values("brothel", person.first_name, person.gender)
    bust = values.get("bust", traits["bust"])
    pool = pool_for(player, dominated, dominant, person.gender, bust)
    if not pool:
        return None
    hellos = (OPERATOR_GUEST_HELLOS if person is owner
              else HOUSE_GUEST_HELLOS)
    temper = (rng.choice(("gruff", "playful")) if dominant
              else pick_temper(dominated, rng))
    return Client(person.first_name, dominated,
                  pick_likes(player, pool, rng), temper, rng.choice(hellos),
                  1, max(MIN_NPC_AGE, person.age),
                  values.get("height", 170), values.get("weight", 65),
                  dominant=dominant, purse=rng.randint(*BROTHEL_PURSE),
                  gender=person.gender, bust=bust,
                  endowment=values.get("endowment", 0),
                  sweat=traits["sweat"], musk=traits["musk"])


def new_client(player:Player, rng:random.Random,
               regulars=None, mode:str="") -> Client:
    pref = pref_of(player)
    visitors = regulars.visiting("brothel") if regulars is not None else []
    if visitors and rng.random() < VISIT_GUEST_CHANCE:
        record = rng.choice(visitors)
        visitor = from_record(player, record, rng, mode)
        if visitor is not None:
            regulars.visit("brothel", record)
            visitor.npc = record["npc"]
            return visitor
    if rng.random() < BROTHEL_HOUSE_GUEST_CHANCE:
        guest = house_guest(player, rng, mode)
        if guest is not None:
            return guest
    if regulars is not None:
        known = regulars.pick("brothel", rng)
        if known is not None and not in_pref(
                known.get("age", pref[0]), pref):
            known = None
        client = (from_record(player, known, rng, mode)
                  if known else None)
        if client is not None:
            regulars.remember("brothel", known)
            regulars.fill("brothel", client.name, {
                "dominated": client.dominated,
                "likes": [list(like) for like in client.likes],
                "temper": client.temper, "age": client.age,
                "height": client.height, "weight": client.weight,
            "history": dict(client.history), "belly": client.belly})
            client.visits += 1
            return client
    dominant = mode == "sub"
    dominated = mode == "domina" or (mode == "" and rng.random() < 0.4)
    gender = random_gender("brothel", rng)
    if gender in REGULAR_BANNED_GENDERS.get("brothel", ()):
        gender = "Male"
    name = rng.choice(FEMININE_CLIENTS if gender in FEMININE
                      else CLIENTS)
    traits = body_values("brothel", name, gender)
    pool = pool_for(player, dominated, dominant, gender, traits["bust"])
    likes = pick_likes(player, pool, rng)
    temper = (rng.choice(("gruff", "playful")) if dominant
              else pick_temper(dominated, rng))
    age, height, weight = client_body(rng, pref)
    client = Client(name, dominated, likes, temper,
                    greeting(temper, rng), 1, age, height, weight,
                    dominant=dominant, purse=rng.randint(*BROTHEL_PURSE),
                    gender=gender, bust=traits["bust"],
                    endowment=traits["endowment"], sweat=traits["sweat"],
                    musk=traits["musk"])
    if regulars is not None and REGULARS_AUTO:
        stored = regulars.remember("brothel", {
            "name": client.name, "dominated": dominated,
            "likes": [list(like) for like in likes], "temper": temper,
            "age": age, "height": height, "weight": weight,
            "dominant": dominant, "gender": gender, "bust": client.bust,
            "endowment": client.endowment, "sweat": client.sweat,
            "musk": client.musk})
        client = from_record(player, stored, rng, mode) or client
        client.visits = stored.get("visits", 1)
    return client


def client_record(client:Client) -> dict:
    return {"name": client.name, "dominated": client.dominated,
            "likes": [list(like) for like in client.likes],
            "dominant": client.dominant, "temper": client.temper,
            "age": client.age, "height": client.height,
            "weight": client.weight, "gender": client.gender,
            "bust": client.bust, "endowment": client.endowment,
            "sweat": client.sweat, "musk": client.musk}


def history_text(client:Client) -> str:
    if not client.history:
        return ""
    parts = {"give": [], "receive": []}
    for key, times in sorted(client.history.items()):
        act, role = key.split("/")
        parts[role].append(f"{act} x{times}")
    lines = []
    if parts["give"]:
        lines.append("you gave: " + ", ".join(parts["give"]))
    if parts["receive"]:
        lines.append("you received: " + ", ".join(parts["receive"]))
    return "\nBetween you so far – " + "; ".join(lines) + "."


def wish_text(client:Client, prompt:bool=False) -> str:
    if client.dominant:
        return ("wants to dominate you – you submit and [serve <act> "
                "receive]" if prompt else "wants to dominate you")
    if client.dominated:
        return ("wants to be dominated – you decide what to offer"
                if prompt else "wants to be dominated")
    return "pays for whatever you offer"


def purse_word(purse:int) -> str:
    low, high = BROTHEL_PURSE
    share = (purse - low) / max(high - low, 1)
    return ("a light purse" if share < 0.34
            else "a fat purse" if share > 0.66 else "a decent purse")


def detail_text(client:Client) -> str:
    parts = [client.gender]
    if client.bust > 0:
        parts.append(f"{bust_label(client.bust)} bust "
                     f"({round(client.bust)} cc)")
    if client.endowment > 0:
        parts.append(f"{client.endowment} cm of cock")
    parts.append(f"sweat {smell_word(client.sweat)}")
    parts.append(f"musk {smell_word(client.musk)}")
    lines = [f"\nBody: {', '.join(parts)}.",
             f"Pockets: {purse_word(client.purse)}."]
    note = smell_note(client.name, client.sweat, client.musk)
    if note:
        lines.append(note)
    if client.visits > 1 and client.likes:
        lines.append("Known favourites: " + ", ".join(
            f"{act} ({role})" for act, role in client.likes) + ".")
    return "\n".join(lines)


def describe_client(client:Client) -> str:
    wish = wish_text(client)
    known = (f"A regular – visit number {client.visits}."
             if client.visits > 1 else "A new face.")
    body = body_line(client.age, client.height, client.weight)
    belly = (f" Belly swollen by {client.belly} cm from your loads."
             if client.belly else "")
    return (f"{client.name}: {body}. {client.temper.capitalize()} temper, "
            f"{wish}. {known}{belly}{detail_text(client)}"
            f"{history_text(client)}")


def client_prompt(shift, player:Player) -> Message:
    client = shift.client
    wish = wish_text(client, prompt=True)
    done = shift.job.sessions - shift.left + 1
    count = (f"{shift.served + 1}" if shift.endless
             else f"{done}/{shift.job.sessions}")
    options = " | ".join(f"{act} {role}" for act, role
                         in client_options(player, client))
    quirk = (quirk_line(client.npc, "brothel_arrive", random) + "\n"
             if client.npc else "")
    return Message(
        f"Client {count}: {client.name} {wish}.\n{quirk}"
        f"{speaker(client.name)}: {client.hello}\n"
        + "".join(f"{line}\n" for line in taste_hints(player, client.name))
        + f"[serve {options}] + optional tone: {' | '.join(TONES)}",
        player.name)

import random

from ...config import (
    BROTHEL_CUT, CAFE_CUT, CAFE_SEAT_SESSIONS, HUNG_GENDERS, RENT_PRICES,
)
from ...body import fake_amount
from ...models import Message, Player
from .. import registry
from ..brothel.practices_anatomy import anatomy
from .model import Job, Shift
from .content import (
    CLOSED, INCIDENT_CHANCE, INCIDENTS, MILK_OUTPUT, OWNERS, PLACES,
    SESSION_LINES,
)
from .milk_content import (
    BARREL, COUNTER, INTROS, NO_BARREL, VARIANT_WORDS, VARIANTS,
)


MILK_FLOOR = 0.3


JOBS = {
    ("brothel", "whore"): Job("whore", "Prostitute", "brothel", 6, 30,
                              "vitality", "Clients pay you, you choose "
                              "what to offer.", interactive=True),
    ("brothel", "waiter"): Job("waiter", "Waiter", "brothel", 4, 14,
                               "agility", "Serve the lounge."),
    ("brothel", "milk"): Job("milk", "Milk Barrel", "brothel", 3, 22,
                             "vitality", "The house's favourite tap."),
    ("brothel", "dancer"): Job("dancer", "Dancer", "brothel", 4, 20,
                               "agility", "Dance in the velvet lounge."),
    ("brothel", "escort"): Job("escort", "Escort", "brothel", 1, 120,
                               "intelligence", "One evening, big pay, "
                               "anything can happen."),
    ("cafe", "seat"): Job("seat", "Seat", "cafe", CAFE_SEAT_SESSIONS, 9,
                          "vitality", "Be the stool. Ladies sit, you hold. "
                          "[quit] is your safeword.", interactive=True),
    ("cafe", "server"): Job("server", "Server", "cafe", 4, 14, "agility",
                            "Carry tea and cake between the ladies."),
    ("cafe", "trainer"): Job("trainer", "Seat Trainer", "cafe", 3, 18,
                             "strength", "Break in the new stools."),
    ("cafe", "baker"): Job("baker", "Baker", "cafe", 4, 15, "intelligence",
                           "The back kitchen needs hands."),
    ("cafe", "usher"): Job("usher", "Usher", "cafe", 3, 13, "agility",
                           "Guide the ladies to their stools."),
    ("cafe", "cleaner"): Job("cleaner", "Cleaner", "cafe", 4, 11,
                             "vitality", "Scrub cushions, mop crumbs."),
}
CUTS = {}
CAFE_WORDS = {"seat": "seat", "stool": "seat", "chair": "seat",
              "server": "server", "waiter": "server", "waitress": "server",
              "trainer": "trainer", "rider": "trainer", "baker": "baker",
              "bake": "baker", "usher": "usher", "cleaner": "cleaner",
              "clean": "cleaner"}
FIRST_WORDS = {"waiter": "waiter", "milk": "milk", "barrel": "milk",
               "dancer": "dancer", "dance": "dancer", "whore": "whore",
               "prostitute": "whore", "escort": "escort"}


def jobs_of(building:str) -> list[Job]:
    jobs = [job for (place, _), job in JOBS.items() if place == building]
    spec = registry.get(building)
    return jobs + (list(spec.jobs) if spec else [])


def jobs_for(building:str, player:Player) -> list[Job]:
    jobs = jobs_of(building)
    if building == "cafe" and player.gender == "Male":
        return [job for job in jobs if job.key == "seat"]
    return jobs


def find_job(building:str, text:str) -> Job | None:
    words = text.strip().casefold().split()
    spec = registry.get(building)
    if spec is not None and spec.jobs:
        word = words[0] if words else ""
        key = spec.job_words.get(word, word)
        found = next((job for job in spec.jobs if job.key == key), None)
        if found is None and len(spec.jobs) == 1:
            return spec.jobs[0]
        return found
    table = CAFE_WORDS if building == "cafe" else FIRST_WORDS
    key = table.get(words[0], "") if words else ""
    job = JOBS.get((building, key))
    if job is not None:
        return job
    return next((job for job in jobs_of(building) if job.key == key), None)


def find_variant(text:str) -> str:
    words = text.strip().casefold().split()
    return VARIANT_WORDS.get(words[1], "") if len(words) > 1 else ""


def building_menu(building:str, player:Player) -> list[Message]:
    lines = [PLACES[building], f"Owner: {OWNERS[building]} – keeps "
             f"{round(CUTS[building] * 100)}% of your pay.",
             f"💰 Gold: {player.gold}", "Jobs ([job <building> <job>]):"]
    for job in jobs_for(building, player):
        lines.append(f"  {job.key:<8} {job.title} – {job.sessions} "
                     f"session(s), about {job.base}+ gold each. "
                     f"{job.blurb}")
        if job.key == "milk":
            lines.append("           [job <building> milk barrel] – "
                         "crouched in a barrel, only breasts/cock "
                         "sticking out; [job <building> milk counter] – "
                         "squatting on the counter, used by the "
                         "patrons. No word = random.")
    if building == "cafe":
        if player.gender == "Male":
            lines.append("Men are furniture here: the seat is the only "
                         "job for you. Bertha: 'Do try not to wobble.'")
        lines.append("Ladies sit with [sit <name>] on a seat who is on "
                     "shift, and stand up with [rise].")
    if building == "brothel":
        lines.append(f"[book classic|fetish] – book a worker for yourself "
                     f"({RENT_PRICES['classic']}/{RENT_PRICES['fetish']} "
                     f"gold)")
    return [Message("\n".join(lines), player.name)]


def session_pay(player:Player, job:Job, rng:random.Random) -> int:
    return job.base + rng.randint(0, job.base // 2)


def milk_word(player:Player) -> str:
    if player.gender == "Herm":
        return MILK_OUTPUT["both"]
    return MILK_OUTPUT["hung" if player.gender in HUNG_GENDERS
                        else "other"]


def real_share(player:Player) -> float:
    body = player.body
    shares = []
    if body.get("breasts", "None") != "None" and body.get("bust", 0):
        shares.append(1 - fake_amount(body, "bust") / body["bust"])
    if player.gender in HUNG_GENDERS and body.get("balls", 0):
        shares.append(1 - fake_amount(body, "balls") / body["balls"])
    return sum(shares) / len(shares) if shares else 1.0


def milk_yield(player:Player) -> float:
    return MILK_FLOOR + (1 - MILK_FLOOR) * real_share(player)


def finish(player:Player, shift:Shift) -> list[Message]:
    if shift.endless:
        return [Message(f"Shift over. {shift.served} served, {shift.earned} "
                        f"gold earned in total (paid out as you went). "
                        f"💰 {player.gold}", player.name)]
    cut = round(shift.earned * CUTS[shift.building])
    player.gold += shift.earned - cut
    messages = [Message(f"Shift over. Earned {shift.earned} gold, "
                        f"{OWNERS[shift.building]} keeps {cut}. You take "
                        f"home {shift.earned - cut}. 💰 {player.gold}",
                        player.name)]
    spec = registry.get(shift.building)
    if spec is not None and spec.finish_hook is not None:
        messages += spec.finish_hook(player, shift)
    return messages


def closed(building:str, player:Player) -> list[Message]:
    return [Message(CLOSED[building], player.name)]


def milk_line(player:Player, variant:str, rng:random.Random) -> str:
    info = anatomy(player)
    pool = BARREL if variant == "barrel" else COUNTER
    fits = [text for tags, text in pool
            if all(info["tags"][tag] for tag in tags)]
    return rng.choice(fits).format(output=milk_word(player),
                                   **info["words"])


def barrel_possible(player:Player) -> bool:
    info = anatomy(player)["tags"]
    return bool(info["bust"] or info["cock"])


def auto_shift(player:Player, building:str, job:Job,
               rng:random.Random, variant:str="") -> list[Message]:
    shift = Shift(building, job, job.sessions)
    lines = []
    if job.key == "milk":
        if variant == "barrel" and not barrel_possible(player):
            return [Message(NO_BARREL, player.name)]
        variant = variant or rng.choice(
            [v for v in VARIANTS if v != "barrel"
             or barrel_possible(player)])
        lines.append(INTROS[variant])
    for number in range(1, job.sessions + 1):
        pay = session_pay(player, job, rng)
        line = (milk_line(player, variant, rng) if job.key == "milk"
                else rng.choice(SESSION_LINES[job.key]))
        lines.append(f"{number}. {line} +{pay} gold")
        shift.earned += pay
        if rng.random() < INCIDENT_CHANCE:
            text, bonus = rng.choice(INCIDENTS)
            lines.append(f"   ✦ {text} +{bonus} gold")
            shift.earned += bonus
    return [Message("\n".join(lines), player.name)] + finish(player, shift)


CUTS = registry.Layered(CUTS, "cut")

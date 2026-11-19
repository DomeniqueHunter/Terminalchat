import random

from ...config import (
    BROTHEL_VISIT_PRICE, CAFE_RIDER_RELIEF, TAVERN_VISIT_PRICE,
    WORK_TICK_SECONDS,
)
from ...models import Message, Player
from ...needs import satisfy
from ..work.jobs import Shift, milk_word
from .clients import Client, client_prompt, pool_for


USABLE = ("whore", "dancer", "milk")
USE_TEXTS = {
    "dancer": ("{visitor} slips a coin into {worker}'s hand, pulls a chair "
               "to the edge of the stage and has {worker} dance for him "
               "alone, closer and closer, until the coins are gone.",
               "{visitor} takes {worker} by the waist and dances with "
               "{worker} between the tables, hands everywhere, until "
               "both are out of breath."),
    "milk": ("{visitor} kneels at {worker}'s barrel, takes his time, "
             "and drinks straight from the tap until {worker} whimpers "
             "and the {output} runs down his chin.",
             "{visitor} fills a mug at {worker}'s tap, drinks it slowly "
             "in front of the whole room and orders another."),
}


def use_price(shift:Shift) -> int:
    return (BROTHEL_VISIT_PRICE if shift.building == "brothel"
            else TAVERN_VISIT_PRICE)


def use_worker(visitor:Player, worker:Player, shift:Shift,
               rng:random.Random) -> list[Message]:
    price = use_price(shift)
    if visitor.gold < price:
        return [Message(f"That costs {price} gold.", visitor.name)]
    visitor.gold -= price
    shift.earned += price
    satisfy(visitor.needs, {"arousal": -CAFE_RIDER_RELIEF})
    text = rng.choice(USE_TEXTS[shift.job.key]).format(
        visitor=visitor.name, worker=worker.name,
        output=milk_word(worker))
    return [Message(f"{text} -{price} gold (💰 {visitor.gold})",
                    visitor.name),
            Message(f"{text} +{price} gold for the house", worker.name)]


def worker_shift(shifts:dict[str, Shift],
                 name:str) -> tuple[str, Shift] | None:
    wanted = name.strip().casefold()
    for key, shift in shifts.items():
        if (shift.building in ("brothel", "tavern")
                and shift.job.key in USABLE
                and key.casefold() == wanted):
            return key, shift
    return None


def visitor_client(visitor:Player, worker:Player, mode:str,
                   rng:random.Random) -> Client:
    dominated = mode == "domina"
    dominant = mode == "sub"
    pool = pool_for(worker, dominated, dominant)
    likes = tuple(rng.sample(pool, min(2, len(pool))))
    hello = ("'Mistress, I came to serve you.'" if dominated else
             "'I came to see you work.'")
    return Client(visitor.name, dominated, likes, "playful", hello, 1,
                  visitor.age, visitor.body.get("height", 0),
                  visitor.body.get("weight", 0), dominant=dominant,
                  player=visitor.name)


def visit_worker(visitor:Player, worker:Player, shift:Shift,
                 rng:random.Random, now:float) -> list[Message]:
    if visitor.name == worker.name:
        return [Message("You cannot visit yourself.", visitor.name)]
    if not shift.job.interactive:
        return use_worker(visitor, worker, shift, rng)
    current = shift.client
    if current is not None and getattr(current, "player", ""):
        return [Message(f"{current.player} is with {worker.name} right "
                        f"now.", visitor.name)]
    if visitor.gold < BROTHEL_VISIT_PRICE:
        return [Message(f"Madame <<npc.rose_first>> wants {BROTHEL_VISIT_PRICE} gold at "
                        f"the door.", visitor.name)]
    visitor.gold -= BROTHEL_VISIT_PRICE
    shift.earned += BROTHEL_VISIT_PRICE
    satisfy(visitor.needs, {"arousal": -CAFE_RIDER_RELIEF})
    shift.client = visitor_client(visitor, worker, shift.mode, rng)
    shift.due = now + WORK_TICK_SECONDS
    return [Message(f"You pay {BROTHEL_VISIT_PRICE} gold and Madame <<npc.rose_first>> "
                    f"shows you to {worker.name}'s room. 💰 {visitor.gold}",
                    visitor.name),
            Message(f"{visitor.name} has come to you – the next client "
                    f"waits no more.", worker.name),
            client_prompt(shift, worker)]

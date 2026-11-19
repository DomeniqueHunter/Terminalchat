from ....town_buildings.counter import Offer, Special
from ....town_buildings.work.model import Job


KEY = "carrying_house"
TITLE = "The Carrying House"
BLURB = ("Baskets, litters and leather harnesses on every wall. In "
         "Brandholm everyone is carried by someone.")
OWNER = "Hallgerd Torfadottir"
PLACE = "🧺 The Carrying House – Hallgerd carries, Eyjolf holds the poles."
CLOSED = "The Carrying House is shut while you are in the dungeon."
CUT = 0.25
RIDE_PRICE = 20
RIDE_HEAL = 0.4
HIRE_PAY = 35
HIRE_COST = 0.10

JOBS = (
    Job("bear", "Bearer", KEY, 4, 24, "strength",
        "Shoulder the poles and carry what needs carrying."),
)
SESSION_LINES = {
    "bear": [
        "You shoulder a litter pole and walk it across the snow.",
        "Eyjolf shows you how to set your feet. 'Knees, not back.'",
        "You carry a basket of laundry up the Hall steps.",
        "You set a heavy litter down as gently as you can.",
    ],
}
RIDE = [
    "Hallgerd lifts you into a basket with one hand and slings it onto "
    "her back. The whole street slides past under her stride, warm and "
    "rocking, and you are asleep before the Hall steps.",
    "Eyjolf holds the poles while Hallgerd settles you into the litter. "
    "'Hands inside,' she says. The snow squeaks under her bare feet all "
    "the way across town.",
]
HIRE = [
    "A giantess hires you for the afternoon. You are hoisted onto her "
    "shoulder like a sack of grain and carried through the market. She "
    "chats the whole way, and you are paid when she sets you down.",
    "A woman at the Hall door lifts you under one arm and carries you "
    "up the long steps without a word. Hallgerd counts out your coins "
    "at the bottom.",
]

SPECIAL = Special(
    KEY, TITLE, BLURB, "🧺", OWNER,
    "'Hold on, small one. Up you go.'",
    (Offer("Work the poles (4 rounds, 25% cut)", "job", item="bear"),
     Offer("Ride in a basket (heal and rest)", "ride", price=RIDE_PRICE),
     Offer(f"Be carried for hire (+{HIRE_PAY} gold)", "hire")))

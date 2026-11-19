from ..work.model import Job


TAVERN_CUT = 0.2
TAVERN_ROOMS = {"common": 8, "private": 25}
TAVERN_THEFT_CHANCE = 0.15
TAVERN_THEFT_GOLD = (3, 15)

OWNER = "Hilda Cask"
PLACE = ("🍺 The Gilded Tankard – <<npc.hilda_first>> <<npc.hilda_last>> pours, shouts and counts "
         "every coin twice.")
CLOSED = "The Gilded Tankard is shut while you are in the dungeon."
GREETING = ("Need coin? Pour for the guests with [job tavern waiter], "
            "dance with [job tavern dancer] or take the milk barrel "
            "with [job tavern milk].")
HELP = """\
  tavern                    – list the jobs
  order tavern <nr|name> [take] – ale, water, stew, bread, roast (hunger and thirst)
  job tavern <job>          – work a shift: waiter, milk, dancer
  job tavern milk barrel    – crouch in a barrel, only breasts/cock out
  job tavern milk counter   – squat on the counter, used by the patrons"""

JOBS = (
    Job("waiter", "Waiter", "tavern", 4, 12, "agility",
        "Carry mugs, dodge hands."),
    Job("milk", "Milk Barrel", "tavern", 3, 18, "vitality",
        "Be the house's tap."),
    Job("dancer", "Dancer", "tavern", 4, 16, "agility",
        "Dance for coins on the stage."),
)

MENU = {
    "ale": ("Mug of ale", 4, {"thirst": -35, "hunger": -5}),
    "water": ("Jug of water", 1, {"thirst": -45}),
    "stew": ("Bowl of hot stew", 8, {"hunger": -45, "thirst": -10}),
    "bread": ("Bread and cheese", 5, {"hunger": -30}),
    "roast": ("Roast with gravy", 14, {"hunger": -65, "thirst": -10}),
}
MENU_TITLE = "Gilded Tankard"
DISH_KG = {"ale": 1, "water": 0, "stew": 2, "bread": 1, "roast": 3}

ROOM_TEXTS = {
    "common": ("You roll out a straw mattress in the common room between a "
               "snoring carter and a sleeping bard. <<npc.hilda_first>> <<npc.hilda_last>> counts your "
               "coins, nods at the corner and blows out the lamp. You "
               "wake rested, stiff and a little smelly."),
    "private": ("<<npc.hilda_first>> <<npc.hilda_last>> hands you a brass key. The room under the roof "
                "has a real bed, a basin and a window to the lanterns. You "
                "sleep like the dead, and a maid leaves bread and small "
                "beer at your door."),
}
THEFT_TEXT = ("A light-fingered neighbour in the common room has been at "
              "your purse: -{gold} gold.")
ROOM_USAGE = ("[room common|private] – sleep in the Gilded Tankard: "
              + ", ".join(f"{kind} {price} gold"
                          for kind, price in TAVERN_ROOMS.items()))

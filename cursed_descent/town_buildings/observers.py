from ..models import Message
from ..towns import town_key


WITNESS_TUNING = ("You see {actor} follow a coach behind the silk screen. "
                  "A while later they come out, flushed and quiet.")
PAID_SCENES = {
    "forge": ("smith", "You see {actor} hold a glowing piece of steel up to "
                       "the light while the smith grunts approval."),
    "mod": ("clinic", "You see two nurses lead {actor} behind the curtain. "
                      "A while later {actor} walks out, a little "
                      "differently."),
    "tuning_room": ("tuning_room", WITNESS_TUNING),
    "room": ("tavern", "You see {actor} slap coins on the bar and climb the "
                       "stairs with a key."),
}
BET_WON = ("You see {actor} whoop and collect a pouch from Grakka as the "
           "red corner wins.")
BET_LOST = "You see {actor} curse as the red corner goes down in the sand."
ARRIVAL = "You see {actor} step off the train with a bag over one shoulder."
SHIFT_DONE = {
    ("mine_guild", "haul"): "You see {actor} come up from the shaft, grey "
                            "with dust, coins in hand.",
    ("brewhouse", "brew"): "You see {actor} climb down from the vats, sticky "
                           "and smelling of malt.",
    ("rune_forge", "carve"): "You see {actor} blow the soot off a freshly "
                             "carved rune.",
}
COUNTER_SCENES = {
    ("blood_bank", "donate"): "You see {actor} roll up a sleeve and look away "
                              "while a nurse fills a bag with blood.",
    ("blood_bank", "vial"): "You see {actor} pocket a warm vial and try not "
                            "to think about it.",
    ("lab", "experiment"): "A hiss and a purple cloud: {actor} stumbles out "
                           "of the booth, coughing.",
    ("black_market", "item"): "You see {actor} slip something under a coat "
                              "and leave without a word.",
    ("workshop", "item"): "You see {actor} hold a bottle up to the light and "
                          "nod at the tinkerer behind the counter.",
    ("rune_forge", "item"): "You see {actor} close a hand around a faintly "
                            "glowing trinket.",
    ("salon", "guest"): "You see {actor} take a seat among the pale guests "
                        "and lift a teacup.",
    ("salon", "serve"): "You see {actor} glide between the tables with a "
                        "silver tray.",
    ("salon", "bite"): "You see {actor} tilt their head to a guest's fangs "
                       "and wince.",
    ("salon", "gossip"): "You see {actor} lean close to a guest and slide a "
                         "coin across the table.",
    ("salon", "present"): "You see {actor} bow low as the Steward's gaze "
                          "passes over them.",
    ("castle", "audience"): "You see {actor} follow a herald through the tall "
                            "doors.",
    ("castle", "banquet"): "You see {actor} take a seat at the long banquet "
                           "table.",
}
BANK_SCENES = {
    "deposit": "You see {actor} hand a heavy purse over the counter while "
               "the clerk counts it twice.",
    "withdraw": "You see {actor} sign the ledger and tuck a purse into "
                "their coat.",
}
Seen = tuple[str, int, str, int]


def before(controller, sender:str) -> Seen | None:
    player = controller.repository.load(sender)
    if player is None or player.npc:
        return None
    return (controller.town.where(player), player.gold, town_key(player),
            len(player.inventory))


def scene(command:str, args:list[str], seen:Seen, player,
          text:str) -> str:
    where, gold, town, bag = seen
    paid = player.gold < gold
    if command in PAID_SCENES and paid:
        return PAID_SCENES[command][1]
    if command == "arena" and args[:1] == ["1"] and where == "arena":
        if "collects" in text:
            return BET_WON
        if "goes down" in text:
            return BET_LOST
    if command == "travel" and town_key(player) != town:
        return ARRIVAL
    if command in BANK_SCENES and (
            paid_or_gained(player, gold) or len(player.inventory) != bag):
        return BANK_SCENES[command]
    return counter_scene(command, args, seen, player)


def paid_or_gained(player, gold:int) -> bool:
    return player.gold != gold


def counter_scene(command:str, args:list[str], seen:Seen, player) -> str:
    from . import registry
    where, gold = seen[0], seen[1]
    spec = registry.get(command)
    if (spec is None or spec.counter is None or where != command
            or not args or not args[0].isdigit()
            or not 1 <= int(args[0]) <= len(spec.counter.offers)):
        return ""
    kind = spec.counter.offers[int(args[0]) - 1].kind
    if command == "castle":
        from ..towns.dusk_hollow_vampires.castle.content import INVITE_KEY
        if not player.profile.get(INVITE_KEY):
            return ""
    elif not paid_or_gained(player, gold):
        return ""
    return COUNTER_SCENES.get((command, kind), "")


def after(controller, sender:str, command:str, args:list[str],
          seen:Seen | None, messages:list[Message]) -> None:
    if seen is None:
        return
    mine = next((message for message in messages
                 if message.recipient == sender), None)
    player = controller.repository.load(sender)
    if mine is None or player is None or mine.witness:
        return
    mine.witness = scene(command, args, seen, player, mine.text)


def shift_done(building:str, job:str) -> str:
    return SHIFT_DONE.get((building, job), "")

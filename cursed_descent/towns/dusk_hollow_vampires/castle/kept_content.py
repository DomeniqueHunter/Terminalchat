from typing import NamedTuple


class Master(NamedTuple):
    title:str
    name:str
    sign:str
    serve:str


KEY = "kept"
HOURS = 24
PAY = 300
FREE_PRICE = 150
MAX_SERVES = 6
SERVE_GOLD = (25, 45)
BLOCKED = ("lobby", "join", "start", "force")
GLOW_BUFF = "kept_glow"
OFFER_PREFIX = "Contract of Keeping – "

# Title overrides are plain data: any master can ask for another one.
MASTERS = {
    "delphine": Master(
        "Mistress", "Delphine",
        "Delphine measures your wrists with her tape, writes a number in "
        "the margin of the contract and nods. 'Twenty-four hours. I will "
        "fit the cuffs myself. I do not tolerate sloppy work.'",
        "Delphine pins the cuff with chalk-white fingers, steps back to "
        "judge the line of it and adjusts it a finger's width. 'Better,' "
        "she says. 'Again.'"),
    "camilla": Master(
        "Mistress", "Camilla",
        "Camilla leans over the contract with a pen that is far too small "
        "for her hand. 'One day, darling. You will be on my arm, you "
        "will be on my leash, and you will be adored. Sign.'",
        "Camilla sweeps you onto the cushions of the Velvet Vein, drapes "
        "a chain across your shoulders and tells the room that you are "
        "hers tonight. Nobody argues."),
    "cassian": Master(
        "Master", "Cassian",
        "Cassian reads the contract once, signs it with one sharp "
        "stroke and slides it back. 'A day,' he says. 'You will carry "
        "what I tell you to carry, and kneel where I tell you to kneel.'",
        "Cassian drops the harness straps over your shoulders, tests "
        "each buckle with a tug that rocks you forward, and tells you "
        "to hold the pose until he says otherwise."),
    "ignatius": Master(
        "Master", "Ignatius",
        "Ignatius wipes soot from his hands before touching the "
        "contract. 'You will work in my forge for a day,' he says, "
        "'bound where I can see you, and fed when I am done.'",
        "Ignatius ties your wrists to the beam above the anvil with "
        "a wide leather strap. 'Hold still,' he says, and works, and "
        "the heat of the forge licks your skin."),
    "leopoldine": Master(
        "Mistress", "Leopoldine",
        "Leopoldine reviews the contract like a chart. 'Twenty-four "
        "hours, voluntary, withdrawal at any time,' she reads aloud. "
        "'Good. I will observe you carefully.'",
        "Leopoldine fastens the straps of the examination table one by "
        "one, checks your pulse with two cool fingers and makes a note. "
        "'Excellent. Do not move.'"),
}

SIGNED = [
    "{title} {master} takes the contract, signs it and hands you a "
    "collar of black leather with a ring at the throat. 'For the next "
    "{hours} hours you are mine,' says {title} {master}. 'Your word "
    "ends it at any time. Until then: kneel.' The collar closes with a "
    "small click.",
]
SERVE = [
    "{name} kneels while {title} {master} fits the leash to the collar. "
    "'Eyes down,' says {title} {master}, and {name} obeys, feeling "
    "every link of the chain against {their} skin.",
    "Wrists crossed, {name} is bound with soft rope and told to wait. "
    "{title} {master} circles slowly, adjusts a knot, and tells {name} "
    "to count to a hundred aloud, which {they} do.",
    "The blindfold goes on and the room disappears. {title} {master}'s "
    "voice moves around {name}, one cool hand on {their} shoulder, "
    "giving orders that are easy to follow and hard to ignore.",
    "{name} spends an hour at {title} {master}'s feet, cuffed and "
    "silent, as a guest of the house to be admired and a servant to be "
    "used. {title} {master} praises {their} patience.",
    "A spreader bar between the ankles, a chain from collar to wrist: "
    "{title} {master} sets {name} in the middle of the room as "
    "an ornament. Visitors look, and {name} holds the pose.",
    "{title} {master} checks every buckle on {name}, asks for the "
    "colour, hears 'green' and carries on. 'Good,' says {title} "
    "{master}. 'You are very easy to keep.'",
]
SERVE_PAY = "💰 +{gold} gold for the service ({count}/{limit})."
SERVE_LIMIT = ("{title} {master} shakes {their} head. 'You have served "
               "enough for today. Rest until the contract ends.'")
FINISHED = (
    "The contract ends. {title} {master} unlocks the collar with a small "
    "key and sets it on the table. 'Free,' says {title} {master}. 'Well "
    "done.' 💰 +{pay} gold. A warm glow stays in your skin, and you "
    "stand a little taller.")
BOUGHT_OUT = (
    "You say your word. {title} {master} unclips the chain at once and "
    "names the price: {price} gold. The collar comes off, the contract "
    "is torn, and nobody asks why.")
CANNOT_PAY = ("{title} {master} waits. 'The price of an early end is "
              "{price} gold.'")
KEPT_BLOCK = ("You are kept by {title} {master} for another {left}. "
              "[castle] to serve, or buy out your contract.")
ALREADY = ("You are already kept by {title} {master}. The contract runs "
           "for another {left}.")
NOT_KEPT = "You have no contract here."
IN_RUN = "The contract can only be signed in town, not down in the dungeon."
STATUS = ("🔒 Kept by {title} {master} – {left} left, "
          "{serves}/{limit} services.")

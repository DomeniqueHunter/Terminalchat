VARIANTS = ("barrel", "counter")

VARIANT_WORDS = {"barrel": "barrel", "fass": "barrel", "tap": "barrel",
                 "counter": "counter", "bar": "counter",
                 "theke": "counter"}

INTROS = {
    "barrel": "You are lifted into the oak barrel and folded into a "
              "tight squat inside it. The lid is fitted around your "
              "waist; only what the house wants tapped sticks out "
              "through the holes.",
    "counter": "You climb onto the counter, spread your knees wide and "
               "settle into a deep squat above the polished wood. The "
               "regulars gather around with their mugs.",
}

NO_BARREL = ("The barrel has nothing to tap on you – a barrel needs "
             "breasts or a cock sticking out. Try the counter.")

def T(text:str, *tags:str) -> tuple[tuple[str, ...], str]:
    return tags, text

BARREL = [
    T("Two round holes frame your {bust}, nipples out in the lamplight. "
      "A patron fits a little brass tap and the first {output} runs "
      "into his mug. The room cheers and the barrel's keeper counts "
      "the pints.", "bust"),
    T("Your {bust} hang through the holes of the barrel front, squeezed "
      "and milked by one customer after another. Each one pays a coin "
      "and gets a pat on your head through the hatch.", "bust"),
    T("A cup is held beneath each nipple and filled slowly while you "
      "shiver inside the dark oak. 'Fresh from the barrel,' the "
      "tapster announces, and the house toasts you.", "bust"),
    T("Your {cock} juts out through the bung-hole at the front of the "
      "barrel and a patron wraps both hands around it, milking steadily "
      "into a tankard. Your {balls} rest on the edge. Inside the dark "
      "you cannot see anything, only feel the strokes and hear the "
      "cheers.", "cock"),
    T("A queue forms at the barrel: every customer gets a minute "
      "with your {cock}, and a tally of mugs filled is chalked up "
      "on the lid. Your legs shake in the squat and the oak "
      "creaks every time you spill.", "cock"),
    T("Both are on display: your {bust} on top, your {cock} below, "
      "everything else hidden in oak. The tavern calls it the "
      "'double-tap' and charges extra. You are milked from both ends "
      "until your thighs burn.", "bust", "cock"),
]

COUNTER = [
    T("You squat on the counter, knees apart, hands on your thighs "
      "while the regulars take turns with you between rounds. "
      "'Don't spill the ale,' <<npc.hilda_first>> calls, 'or the "
      "customers.'"),
    T("Your {bust} sway as patrons take turns milking them over "
      "mugs, laughing and clinking glasses. Between customers you "
      "wipe your forehead and keep your squat steady on the wet "
      "wood.", "bust"),
    T("Your {cock} hangs low between your spread thighs and every "
      "passing patron stops to stroke, squeeze or lap at it. By the "
      "end of the hour the counter below you is a slick, "
      "shining mess.", "cock"),
    T("A drunk sellsword spanks your {butt} to make you rock and the "
      "whole bar laughs. They use you like a bar stool and a toy at "
      "once, and tip by the dozen.", "butt"),
    T("The bar lines up and you are used in a slow rotation, squatting "
      "on the counter with your knees shaking. You thank each one by "
      "name and they tip in coins, kisses and slaps."),
    T("You hold your squat for a whole hour while patrons pass "
      "you from hand to hand, mouth to mouth, mug to mug. By the "
      "last call you are hoarse, slick and strangely proud of the "
      "tally on the wall."),
]

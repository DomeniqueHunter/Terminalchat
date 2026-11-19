import random

from .guests import Guest


CHILD_WORDS = {"son": ("son", "his"), "daughter": ("daughter", "her")}
SIT = (
    "{rider} looks down at {seat}, her {child}, and her cock stirs "
    "against the heavy folds of her thighs. 'Mommy is much bigger than "
    "you remember, {seat}. Open up – you came into this world "
    "between these thighs, you can survive being under them.'",
    "'Look at you,' {rider} purrs, lowering herself over {seat}'s face "
    "inch by inch. 'My own {child}, pinned under {rider}'s whole "
    "backside. Every kilo of me, every centimetre. Be proud, sweetheart "
    "– not many {child}s get this much Mommy.'",
)
LOOK = (
    "Your own mother is sitting on your face. The weight that once "
    "rocked you to sleep now keeps you from breathing, and somewhere "
    "above you her cock is hardening at the thought.",
    "You know this smell, this voice, this warmth – and you have never "
    "been under so much of it. Mom is a mountain, and she is smiling.",
)
CLENCH = (
    "'Hush, {seat},' {rider} whispers as her cheeks close tight. 'Mommy "
    "is only holding you. You always needed a firm hand.'",
    "{rider} clenches and gives a low, shaky moan. 'My good {child}. "
    "Stay under Mommy, right where you belong.'",
)
WIGGLE = (
    "{rider} grinds in a slow circle and her cock leaves a damp line "
    "across {seat}'s forehead. 'You wanted to be close to Mommy, "
    "didn't you?'",
    "'Did you think this was a punishment?' {rider} laughs, rolling her "
    "hips. 'It is a hug, {seat} – a very large one.'",
)
ROUND = (
    "Through the dark you hear {rider}'s voice, thick and tender: 'Mommy "
    "is so proud of you, {seat}. Take one more breath of me.'",
    "{rider} strokes herself lazily while she sits. 'Say it, {seat}. "
    "Say whose seat you are.' The only answer is a muffled 'Mom.'",
)
RISE = (
    "{rider} finally rises, flushed and glistening, and ruffles {seat}'s "
    "hair. 'Same time next week, sweetheart? Mommy will bring dessert.'",
)

SWALLOW_RIDER = (
    "'Come home, {seat},' you purr, and rock back until your {child} "
    "slides into you inch by inch. 'You started in my belly. Tonight you "
    "can end in my ass.' His struggling fades into a warm, muffled "
    "heartbeat deep inside you.",
    "You rise once, lick your lips, and sit down hard. {seat} vanishes "
    "between your cheeks, whimpering 'Mom...' until the word is only a "
    "tremor you can feel low in your body. 'Hush, sweetheart. Mommy has "
    "you.'",
)
SWALLOW_SEAT = (
    "'Mom!' you manage once, and then the darkness closes over you. "
    "{rider} swallows her own {child} with a satisfied sigh, and the "
    "last thing you hear is her soft 'Sleep now, sweetheart.'",
    "The weight of the woman who raised you folds around you, warm and "
    "huge and total. Her voice follows you down: 'There. Safe inside "
    "Mommy again.'",
)


def child_of(guest:Guest) -> tuple[str, str]:
    return CHILD_WORDS.get(guest.kin, ("child", "their"))


LICK = (
    "{rider} goes rigid for one heartbeat. 'Oh. Oh, {seat}... my own "
    "{child}, with that tongue.' Her thighs tremble around you. 'Where "
    "did you learn that? No – don't tell Mommy. Don't stop.'",
    "'Good {child},' {rider} breathes, one hand finding the back of "
    "{seat}'s head. 'Just like that. Mommy raised you well, didn't she? "
    "Deeper, sweetheart – you know exactly what Mommy likes.'",
    "Her cheeks loosen as the tongue works, and {rider} lets out a long, "
    "unsteady sigh. 'Mommy was going to scold you for being rude... but "
    "oh, {seat}, you have talent. Keep going.'",
    "'Such a dirty little {child},' {rider} scolds, voice cracking "
    "halfway into a moan. 'Licking Mommy there... I should be ashamed of "
    "you. I should be ashamed of both of us.' She presses down harder.",
    "{rider} lets out a heavy, shuddering sigh and her cock throbs "
    "against her thigh. 'Mommy needed this more than she will ever admit, "
    "{seat}. Thank you, baby. Now do it again.'",
    "'Mm... there.' {rider} rocks softly over {seat}'s tongue, her voice "
    "warm and drowsy. 'You always were my sweetest {child}. Stay right "
    "there, and Mommy will make it worth your while.'",
)
KISS = (
    "{rider} makes a small, startled sound. 'A kiss? There? From my own "
    "{child}...' Her breath hitches and her cheeks soften. 'Oh, "
    "{seat}. Mommy did not expect that.'",
    "'Good {child},' {rider} murmurs, stroking {seat}'s hair. 'So "
    "devoted. Mommy sees it. Mommy always saw how much you wanted to be "
    "near her.'",
    "Her whole weight eases for a moment as {seat} kisses her. 'That's "
    "it, sweetheart. Be gentle with Mommy and Mommy will be gentle with "
    "you.'",
    "'Don't you dare get sentimental on Mommy now,' {rider} scolds "
    "without any heat, blushing furiously. 'It's... it's allowed. Just "
    "this once. Maybe twice.'",
    "{rider} lets out a long, content sigh and pats {seat}'s head. "
    "'Mommy is so proud. Nobody kisses like my {child}.'",
)


def kin_text(texts:tuple[str, ...], guest:Guest, seat:str,
             rng:random.Random) -> str:
    child, _ = child_of(guest)
    return rng.choice(texts).format(rider=guest.name, seat=seat,
                                    child=child)

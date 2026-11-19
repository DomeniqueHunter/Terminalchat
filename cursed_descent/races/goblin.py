from . import Race


ADVICE = {'bust': 'Bigger, heavier udders for you, dearie – big enough to slosh. Stuffed in nice and tight: [mod bust up].', 'butt': 'More behind, dearie! Something to slap: [mod butt up].', 'cock': 'More cock, dearie. The spirits love it: [mod cock up].', 'balls': 'Big swinging balls! Stuffed full: [mod balls up].', 'build_thin': 'Too lean. Eat. Or I will add some for you.', 'build_heavy': 'Mmm, plenty of meat. I can add more.', 'fine': 'Nothing wrong. Yet. Let the spirits decide.'}

OFFERS = {
    "shop": "Junk, treasure, same thing! [shop]. Sell me yours, I "
            "pay almost fair.",
    "smith": "Bring it! I hit it, it gets better. Or louder.",
    "bank": "Coins in, coins out. [deposit <gold>], [withdraw "
            "<gold>]. Pawn shop rules: I keep a finger on it.",
    "tavern": "Pour for the drunks with [job tavern waiter], dance on "
              "the tables with [job tavern dancer] or take the barrel "
              "with [job tavern milk].",
    "brothel": "Dirty, loud, fun. [job brothel whore], [job brothel "
               "dancer], [job brothel waiter] or [job brothel milk] – "
               "the mud stays outside, mostly.",
}
DROP_IN_WORKING = (
    "Madame Rose bursts in cackling, slaps your rump hard enough to "
    "ring the bells in her ears and drops a handful of coins. 'More "
    "of that! Louder!'",
    "Madame Rose perches on a stool, gnawing a bone, and watches the "
    "whole thing. 'Good show. You earn extra.'",
)
DROP_IN_SUB = (
    "Madame Rose kicks the client out the window, locks the door and "
    "grins with all her crooked teeth. 'Mine!' She is rough, she is "
    "loud, she pays.",
    "Madame Rose drags you across the bed by the ankle. 'My turn, "
    "pet.' When she is done, the bells on her ears ring for a while "
    "and the coins are on the pillow.",
)
RACE = Race(
    key='goblin',
    name='goblin',
    plural='goblins',
    height=(105, 135),
    weight=(30, 75),
    roughness=1.5,
    roughness_style='with a cackle and no mercy at all',
    advice=ADVICE,
    clinic_special=' I only do implants, dearie – bone, bladder and bladder-skin, stuffed in tight. Real growth is for fools.',
    taste=("bust", "big", "fake"),
    taste_pull=0.6,
    offers=OFFERS,
    drop_in_working=DROP_IN_WORKING,
    drop_in_sub=DROP_IN_SUB,
    adventurers=False,
    implant_only=True,
    member=(12, 10, 5),
    member_shape="Knobbed",
    scent=(2, 2),
    skin=("sharp musk and wet moss", "tangy, bitter and wild"),
)

from . import Race


ADVICE = {'bust': 'A chest should be broad and heavy. Fill it out: [mod bust up].', 'butt': 'A solid rear carries a woman through any winter. More: [mod butt up].', 'cock': 'Length is honest work. Add some: [mod cock up].', 'balls': "A man's weight should hang low. Heavier balls: [mod balls up].", 'build_thin': 'Too thin. Muscle will do you good: [mod muscle up].', 'build_heavy': 'Good frame. Add muscle on top: [mod muscle up].', 'fine': 'Sound body. Nothing to fix.'}

OFFERS = {
    "shop": "Ropes, lamps, picks. Buy what you need, sell what you "
            "carry – [shop].",
    "smith": "Bring good steel and I will make it better. Bad steel "
             "goes in the furnace.",
    "bank": "The vault holds anything. [deposit <gold>], "
            "[withdraw <gold>]. No interest, no theft.",
    "tavern": "Work for your ale: [job tavern waiter], [job tavern "
              "dancer] or [job tavern milk] if you are built for it.",
    "brothel": "Strong hands, honest prices. Take [job brothel whore], "
               "[job brothel dancer], [job brothel waiter] or [job "
               "brothel milk].",
}
DROP_IN_WORKING = (
    "Madame Rose stamps in, arms folded, and watches the work like a "
    "foreman. 'Good. Steady. That is how it is done.' She drops a coin "
    "in your hand.",
    "Madame Rose leans on the doorframe until the client is done, then "
    "nods once. 'Solid work. Take this.'",
)
DROP_IN_SUB = (
    "Madame Rose shuts the door, rolls up her sleeves and says nothing "
    "at all. She takes what she wants with her thick hands and pays "
    "you well for it.",
    "Madame Rose sends the client out with one look. 'Mine now.' She "
    "handles you like good ore, firmly and thoroughly.",
)
RACE = Race(
    key='dwarf',
    name='dwarf',
    plural='dwarves',
    height=(120, 150),
    weight=(60, 120),
    roughness=1.3,
    roughness_style='with hands like vices',
    advice=ADVICE,
    clinic_special=' Honest strength is my speciality – through diet and tinctures.',
    taste=("butt", "big", "real"),
    taste_pull=0.5,
    offers=OFFERS,
    drop_in_working=DROP_IN_WORKING,
    drop_in_sub=DROP_IN_SUB,
    implant_only=False,
    member=(14, 14, 6),
    member_shape="Stout",
    scent=(1, 1),
    skin=("coal smoke and sweat-soaked leather", "salt and mineral iron"),
)

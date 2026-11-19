from . import Race


ADVICE = {
    'bust': 'Broad hall-women carry weight up front. More: [mod bust up].',
    'butt': 'A wide seat is a strong seat. More: [mod butt up].',
    'cock': 'In the hall, size is rank. More: [mod cock up].',
    'balls': 'Heavy and full, as the Matriarch likes them: [mod balls up].',
    'build_thin': 'Too thin for the winter. Eat, then [mod muscle up].',
    'build_heavy': 'A proper frame. Add some muscle: [mod muscle up].',
    'fine': 'Nothing to mend. The hall approves.',
}

OFFERS = {
    "shop": "Boots at the door, coin on the counter. [shop] shows what "
            "we keep, and I buy what you carry.",
    "bank": "Gold keeps warm in the Hall vault. [deposit <gold>], "
            "[withdraw <gold>].",
    "tavern": "Carry the mugs with [job tavern waiter], dance by the "
              "fire with [job tavern dancer] or give the cask what it "
              "wants with [job tavern milk].",
}

RACE = Race(
    key='nord',
    name='nord',
    plural='nords',
    height=(200, 340),
    weight=(120, 380),
    roughness=1.2,
    roughness_style='with broad, warm hands',
    advice=ADVICE,
    clinic_special=' Hold still, little one. The Hall pays for good work.',
    taste=("bust", "big", "real"),
    taste_pull=0.3,
    offers=OFFERS,
    adventurers=False,
    member=(34, 26, 11),
    member_shape="Human",
    scent=(1, 2),
    skin=("smoke and warm leather", "salt and peat"),
)

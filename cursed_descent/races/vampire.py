from . import Race


ADVICE = {
    'bust': 'A fuller chest suits the candlelight. Fill it out: [mod bust up].',
    'butt': 'Curves are the currency of the court. More: [mod butt up].',
    'cock': 'A little more weight, darling. [mod cock up].',
    'balls': 'Fuller, heavier, more elegant: [mod balls up].',
    'build_thin': 'Pale is fashionable. Gaunt is not. [mod muscle up].',
    'build_heavy': 'A lovely frame. A little tone on top: [mod muscle up].',
    'fine': 'Nothing to improve. How rare.',
}

OFFERS = {
    "shop": "Everything for the long night. [shop] shows what we keep, and "
            "I buy what you carry – quietly.",
    "bank": "Gold keeps better than blood. [deposit <gold>], [withdraw "
            "<gold>]. The vault never sleeps.",
    "tavern": "Pour for the guests with [job tavern waiter], dance for the "
              "candles with [job tavern dancer] or give the cask what it "
              "wants with [job tavern milk].",
}

RACE = Race(
    key='vampire',
    name='vampire',
    plural='vampires',
    height=(150, 210),
    weight=(45, 130),
    roughness=0.8,
    roughness_style='with cool, patient hands',
    advice=ADVICE,
    clinic_special=' Gentle work, darling. A little blood, a little patience.',
    taste=("butt", "big", "real"),
    taste_pull=0.4,
    offers=OFFERS,
    adventurers=False,
    member=(16, 13, 5),
    member_shape="Human",
    scent=(0, 1),
    skin=("cold stone and a trace of iron", "iron and old wine"),
)

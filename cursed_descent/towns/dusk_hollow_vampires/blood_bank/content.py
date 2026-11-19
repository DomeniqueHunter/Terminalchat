from ....town_buildings.counter import Offer, Special


KEY = "blood_bank"
TITLE = "Blood Bank"
BLURB = "Give blood for honest gold – or buy a warm vial."
DONATE_PAY = 30
DONATE_SHARE = 0.25
MIN_HP_SHARE = 0.4
FAINT_STEP = 0.15
FAINT_CAP = 0.6
DATA_KEY = "donations"
DAY_KEY = "donated_day"
VIAL_PRICE = 40
VIAL_HEAL = 0.6
SPECIAL = Special(
    KEY, TITLE, BLURB, "🩸", "Dr. Ambrose Vale",
    "'Voluntary, always. Only ever voluntary.'",
    (Offer("Donate blood (+30 gold, once a day for free)", "donate"),
     Offer("Buy a warm vial of blood", "vial", price=VIAL_PRICE),
     Offer("Chat with the staff", "talk")))

BLOOD_BUFFS = {
    "blood_faint": {
        "label": "Light-headed", "bonus": {"vitality": -1}, "text": "",
    },
    "blood_vigor": {
        "label": "Vampire vigor", "bonus": {"strength": 1, "agility": 1},
        "text": "",
    },
}

DONATE = [
    "{name} rolls up a sleeve. Mirela finds the vein at the first try and "
    "hums while the bag fills. Dr. Ambrose apologizes twice, labels the "
    "bag, and Mirela presses {pay} gold and a biscuit into {their} hand.",
    "The needle goes in with a polite pinch. Dr. Ambrose keeps his eyes on "
    "the gauge and does not look at the bag at all. 'Thank you,' he says "
    "carefully. {pay} gold change hands, and {name} leaves a little "
    "paler.",
    "{name} sits in the donor chair under a daylamp. Mirela counts "
    "backwards from ten, and the bag is full before she reaches three. "
    "'You are a natural,' she says, and pays {pay} gold.",
]

AGAIN = [
    "Dr. Ambrose frowns at the chart. 'You were here today already. The "
    "body does not refill that fast.' Mirela takes the second bag anyway, "
    "and {name} feels it all the way down to {their} knees.",
]

TOO_WEAK = [
    "Dr. Ambrose takes one look at {name} and shakes his head. 'Not today. "
    "You look like you are all out. Go and rest, or buy a vial.'",
]

FAINT = [
    "The room tilts. {name} wakes up on the cot with a wet cloth on "
    "{their} forehead and Mirela scolding Dr. Ambrose and {name} in equal "
    "parts. 'Three donations in a row. What did we say about stopping?' "
    "The gold is still counted out on the table.",
]

VIAL = [
    "Dr. Ambrose hands over a warm, dark vial. {name} drinks it before "
    "the taste can argue. Iron, salt and something older. A pulse of heat "
    "runs through {their} limbs, and Mirela slips a biscuit into "
    "{their} pocket without being asked.",
    "The vial is body-warm and thick. {name} swallows, coughs and straightens up. "
    "The cuts close, the headache lifts and Dr. Ambrose looks relieved "
    "and a little ashamed.",
]

TALK = [
    "'We do not keep slaves here,' says Dr. Ambrose, polishing a needle. "
    "'The Duchess keeps hers up the hill. We keep a ledger, and we pay "
    "our donors on the day.'",
    "Mirela leans on the counter. 'I came to sell one pint. Dr. Ambrose "
    "gave me a job and a biscuit. Do not tell the Steward.'",
    "'The Salon of the Pale thinks we are beneath them,' says Dr. "
    "Ambrose. 'They also drink our vintage. Both can be true.'",
    "Mirela lowers her voice: 'The Duchess's guards hang from their "
    "rings for being late. We treat them afterwards. Do not make them "
    "late.'",
    "'Everyone here is hungry,' says Dr. Ambrose gently. 'The question "
    "is only how politely.'",
]

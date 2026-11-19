from ....town_buildings.counter import Offer, Special
from .kept_content import FREE_PRICE, KEY as KEPT, MASTERS, OFFER_PREFIX


KEY = "castle"
TITLE = "Castle Markov"
BLURB = "The seat of the Duchess. Invitation only."
INVITE_KEY = "castle_invite"
FAVOR_GOLD = 60
GIFT_GOLD = 100
AUDIENCE_ODDS = (0.40, 0.65, 0.85)
HURT_SHARE = 0.1
LEASH_SHARE = 0.3
BANQUET_ODDS = 0.6
BANQUET_SHARE = 0.3
SPECIAL = Special(
    KEY, TITLE, BLURB, "🏰", "Steward Mina Vasek",
    "'The Duchess receives by invitation. Yours is missing.'",
    (Offer("Request an audience with the Duchess", "audience"),
     Offer("Join the banquet", "banquet"),
     Offer("Talk to the gate guards", "gate"),
     Offer("Offer yourself to the Duchess", "offer_self"),
     *(Offer(f"{OFFER_PREFIX}{master.title} {master.name} (24 h)",
             "kept_contract", item=key, hide_if=KEPT)
       for key, master in MASTERS.items()),
     Offer("Serve your master", "kept_serve", show_if=KEPT),
     Offer(f"Buy out your contract ({FREE_PRICE} gold)", "kept_free",
           show_if=KEPT)))

CASTLE_BUFFS = {
    "duchess_favor": {
        "label": "Duchess's favor", "bonus": {"strength": 2, "vitality": 2},
        "text": "",
    },
    "castle_leash": {
        "label": "On the leash", "bonus": {"agility": -2}, "text": "",
    },
    "castle_rings": {
        "label": "Hung by the rings", "bonus": {"strength": -2}, "text": "",
    },
    "kept_glow": {
        "label": "Kept glow", "bonus": {"vitality": 1}, "allure": 3,
        "text": "",
    },
    "castle_bitten": {
        "label": "Banquet bite", "bonus": {"vitality": -1}, "allure": 2,
        "text": "",
    },
}

NO_INVITE = [
    "Mina Vasek looks {name} over from the top of the steps, then looks "
    "past {them}. 'No invitation, no audience. The Salon of the Pale "
    "decides who is worth the stairs. Good evening.' The gate closes "
    "with a sound like a locked jaw.",
    "Kasia lowers her halberd across the gate. 'Not without a letter.' "
    "Behind her Mina Vasek does not even turn around. 'Present yourself "
    "at the Salon first.'",
]

FAVOR = [
    "The Duchess receives {name} in a hall of black marble. Edric kneels "
    "at her left heel, Tomas at her right, leashes slack in her fingers. "
    "Alexandra listens, smiling the way one smiles at a pet that has "
    "performed a small trick. 'Charming,' she decides. 'Take something "
    "for the road.' Mina counts out {gold} gold, and a warmth settles "
    "into {name}'s bones.",
    "Alexandra studies {name} for a long time, one eyebrow raised. The "
    "Duchess does not raise her voice. She does not need to. 'You have "
    "my favor,' she says, 'for as long as it amuses me.' A purse of "
    "{gold} gold follows.",
]

GIFT = [
    "The Duchess has no interest in {name} today. She hands over a "
    "heavy purse while Tomas compliments {name}'s boots, and Edric "
    "stares at the floor, as always. {gold} gold. The audience is over "
    "before it began.",
]

DISMISSED = [
    "Alexandra lets {name} finish, sets down her glass, and looks at "
    "{them} with great, gentle boredom. 'No,' she says. The guards "
    "escort {name} out, and one of them 'accidentally' trips {them} on "
    "the stairs.",
]

LEASH = [
    "'You will do,' says the Duchess, and hands {name} the end of a "
    "leash. Edric looks up, almost relieved. For one long hour {name} "
    "walks at her left heel, collar cold on {their} throat, learning "
    "exactly how heavy the chain is. When the hour ends the collar "
    "comes off. 'Next time,' says Alexandra, 'you stay.'",
]

RINGS = [
    "'Disrespect,' says the Duchess, almost kindly. Two guards hang "
    "{name} by the wrists in the hall, and Alexandra reaches out and "
    "tugs one heavy ring of her own, thoughtfully, as if to show how "
    "it is done. {name} hangs there for an hour, hearing every word "
    "about {them}. Then the ropes are cut. 'Next time,' says Alexandra, "
    "'a day.'",
]

BANQUET_HONOR = [
    "A table in the dark hall, silver-free and candlelit. {name} is "
    "seated at the Duchess's right and fed until {they} cannot move. "
    "Edric pours, Tomas flatters, and nobody bites. The whole castle "
    "agrees that {name} is a very good guest.",
]

BANQUET_MAIN = [
    "'The meal is wonderful,' says the Duchess. 'And so are you.' Hands "
    "turn {name}'s head to the side, and a cold mouth finds the pulse "
    "beneath {their} ear. The room politely turns away. When it is done "
    "{name} is guided back to the table, dizzy, flushed and still, "
    "somehow, hungry.",
]

GATE_TALK = [
    "Kasia keeps her eyes on the wall. 'Do not be late for anything "
    "here. I have hung by my rings for two days. I do not recommend "
    "it.'",
    "Nadia leans closer, whispering. 'The Duchess is only angry when she "
    "is quiet. Learn to hear when she is quiet.'",
    "'Lady Vesna presents people,' says Kasia. 'The Salon of the Pale. "
    "Ask her. Do not ask me.'",
    "'One of the Duchess's men is tired,' mutters Nadia. 'They are "
    "looking for another. Do not look like a candidate.'",
]

from ....town_buildings.counter import Offer, Special


KEY = "salon"
TITLE = "Salon of the Pale"
BLURB = "The Hollow's high society. Tea, gossip and teeth."
FAVOR_KEY = "salon_favor"
TEA_PRICE = 15
GOSSIP_PRICE = 10
PRESENT_PRICE = 30
PRESENT_FAVOR = 2
TEA_BITE_CHANCE = 0.15
SERVE_PAY = (20, 40)
SERVE_BITE_CHANCE = 0.25
BITE_PAY = 25
BITE_SHARE = 0.15
SMALL_SHARE = 0.1
SPECIAL = Special(
    KEY, TITLE, BLURB, "🥂", "Lady Vesna Orlov",
    "'Do sit. Everyone who stands eventually kneels.'",
    (Offer("Use: Take tea with the guests", "guest", price=TEA_PRICE),
     Offer("Work: Serve the guests", "serve"),
     Offer("Accept a guest's bite (+25 gold)", "bite"),
     Offer("Buy gossip", "gossip", price=GOSSIP_PRICE),
     Offer("Be presented to the Steward", "present", price=PRESENT_PRICE,
           hide_if="castle_invite")))

SALON_BUFFS = {
    "salon_poise": {
        "label": "Salon-worthy", "bonus": {"agility": 1}, "allure": 2,
        "text": "",
    },
    "pale_kiss": {
        "label": "Pale kiss", "bonus": {"vitality": -1}, "allure": 3,
        "text": "",
    },
}

TEA = [
    "{name} is waved to a velvet chair. Selene fans herself and asks "
    "whether {name} is boring. {name} says no, and the fan stops. Lucian "
    "tells an anecdote that has a fang in every sentence. By the end of "
    "the second cup {name} is, apparently, charming.",
    "Vesna pours the tea herself. 'We do not ask where our guests have "
    "been,' she says, 'only where they are going next.' The conversation "
    "turns to people {name} has never met and, politely, to "
    "{their} neck.",
    "{name} sits through an hour of exquisite insults, none of them "
    "aimed at {them}. When the tea is finished Vesna lifts an eyebrow. "
    "'You will do.'",
]

TEA_BITE = [
    "Mid-sentence, Lucian leans over and nips {name}'s wrist with a "
    "small, apologetic click. 'You were so close,' he sighs, dabbing his "
    "lips. 'I could not help it.'",
    "Selene's fan snaps shut at {name}'s collar. 'Oh dear,' she murmurs, "
    "and a small bite follows, quick and neat. 'There. Now we are "
    "friends.'",
]

SERVE = [
    "{name} carries a tray through the room for an hour. Hollis shows "
    "{them} where to stand, where not to look and which glass belongs to "
    "whom. Nobody says thank you. Coins appear on the tray anyway: {pay} "
    "gold.",
    "{name} refills glasses until the guests stop noticing. Vesna "
    "watches from her chair, and a nod from her is worth, in this room, "
    "{pay} gold.",
    "An hour of silent service, a glass broken, a glance from Selene "
    "that could have curdled the wine. When the evening ends there are "
    "{pay} gold on the tray.",
]

SERVE_BITE = [
    "A trembling glass, a guest's hand on {name}'s throat, a polite "
    "'Allow me.' The bite is quick and expert, and {name} keeps the tray "
    "steady through all of it. The tip is generous, in the end: {pay} "
    "gold.",
    "Lucian takes the tray from {name}'s hands, sets it down and takes "
    "{them} by the chin instead. 'The service here is excellent,' he "
    "announces to the room. {pay} gold appear on the tray afterwards.",
]

BITE = [
    "A guest rises from the sofa and offers a very polite bow. 'May "
    "I?' {name} nods. The bite is a hot, small shock and then a "
    "warm, drowsy, floating feeling. The guest pays {pay} gold and "
    "kisses {their} fingers.",
    "Lucian takes {name}'s wrist with both hands, like a gift, and "
    "drinks without a sound. 'Thank you, darling,' he whispers. {pay} "
    "gold, as agreed.",
]

GOSSIP = [
    "Hollis whispers behind his tray: 'The Duchess keeps two men on a "
    "leash. The old one is tired. They say she is shopping for a new "
    "one.'",
    "'The Steward counts every invitation,' says Hollis. 'You get one "
    "only if Lady Vesna presents you. She likes people who survive her "
    "tea.'",
    "'The guards wear rings in their chests,' Hollis murmurs. 'If they "
    "are late, they are hung by them. I have heard them count the "
    "hours.'",
    "'The Baron owes half the Hollow,' says Hollis. 'Do not lend him "
    "anything. Especially not your neck.'",
    "'The Duchess is enormous,' he whispers, red in the face. 'In every "
    "direction. I am not supposed to say that.'",
]

PRESENT_NO = [
    "Vesna looks {name} over the way one examines a glass. 'Not yet,' "
    "she says. 'Come back when the room knows your name.' Your {price} "
    "gold is returned with a small, cold smile.",
]

PRESENT_YES = [
    "Vesna rises, takes {name}'s arm and walks {them} to the foot of the "
    "stairs, where the Steward's lamp burns. 'This one has survived my "
    "tea,' she says. A note is written, sealed and pressed into {name}'s "
    "hand: an invitation to the castle.",
]

PRESENT_ALREADY = [
    "'You are already on the Steward's list,' says Vesna, a little "
    "amused. 'Do not make me introduce you twice.' The {price} gold are "
    "returned.",
]

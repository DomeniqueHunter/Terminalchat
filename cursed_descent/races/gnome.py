from . import Race


ADVICE = {'bust': 'Udders! Magnificent, heavy udders! Real growth, experimental: [mod bust up magic].', 'butt': 'I have a tincture that makes a rear grow by itself: [mod butt up magic]. Mostly safe.', 'cock': 'Real growth, no implants – my newest formula: [mod cock up magic].', 'balls': 'Bigger, heavier balls, grown, not stuffed: [mod balls up magic].', 'build_thin': 'You are lean. I can add muscle with a spring-wound tincture.', 'build_heavy': 'Splendid mass. Let us make it more interesting.', 'fine': 'Nothing to fix. Which is dull. Shall I experiment?'}

OFFERS = {
    "shop": "Gadgets, gizmos, spare parts – [shop]. Ask about the "
            "mystery box.",
    "smith": "Precision work. Bring the blade, bring the schematics, "
             "mind the sparks.",
    "bank": "The Engine will count it for you: [deposit <gold>], "
            "[withdraw <gold>]. Rarely wrong.",
    "tavern": "Pour cider with [job tavern waiter], work the piano "
              "stage with [job tavern dancer] or try the barrel with "
              "[job tavern milk].",
    "brothel": "Inventive hands, clever toys. [job brothel whore], [job "
               "brothel dancer], [job brothel waiter] or [job brothel "
               "milk] – ask for the gadgets.",
}
DROP_IN_WORKING = (
    "Madame Rose bustles in, goggles up, and tweaks something on a "
    "contraption beside you. 'Excellent test subject! Here, a bonus "
    "for science.'",
    "Madame Rose watches through a brass spyglass from the doorway, "
    "scribbles notes, then pats your hand. 'Wonderful. Keep it up.'",
)
DROP_IN_SUB = (
    "Madame Rose clicks the door shut, wheels in a polished brass "
    "device and grins. 'Hold still, darling. Testing.' She is "
    "thorough, and pays for the data.",
    "Madame Rose waves the client out and winds up a clockwork toy. "
    "'My turn to experiment.' It takes a long and noisy while.",
)
RACE = Race(
    key='gnome',
    name='gnome',
    plural='gnomes',
    height=(95, 115),
    weight=(30, 55),
    roughness=1.15,
    roughness_style='with a clockwork rhythm',
    advice=ADVICE,
    clinic_special=' Experimental growth is my speciality. Results may vary.',
    taste=("bust", "any", "fake"),
    taste_pull=0.5,
    offers=OFFERS,
    drop_in_working=DROP_IN_WORKING,
    drop_in_sub=DROP_IN_SUB,
    implant_only=False,
    member=(9, 8, 3),
    member_shape="Clockwork",
    scent=(0, 1),
    skin=("moss, herbs and warm earth", "green herbs and a touch of honey"),
)

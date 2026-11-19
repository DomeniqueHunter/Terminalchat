PLANT = {
    "name": "Seductress Vine",
    "need": (0, 2, 4, 6, 9),
    "comfort": (0, 1, 2, 4, 5),
    "regrow": 2,
    "nectar": (1, 2),
    "nectar_overgrown": (2, 3),
    "nectar_item": "seductress_nectar",
    "seed_item": "seductress_seed",
    "seed_chance": 0.4,
    "feed": {"label": "Feed the plant", "min_endowment": 10,
             "min_balls": 4, "min_sweat_tier": 1, "store_from": 2,
             "store_cap": 4},
    "hold": {3: 2, 4: 4},
    "neglect": {"warn": 7, "evil": 14, "rescue": 3, "seduce": 0.15},
    "pod_kinds": ("classic", "nectar", "cocoon", "flytrap"),
    "looks": (
        "A dark, heart-shaped seed sits in the soil and gives off a "
        "faint warmth.",
        "A thin, glossy vine has pushed up and winds slowly around "
        "its stake, leaning toward whoever walks past.",
        "The vine has thickened and carries tight, deep red buds that "
        "smell of honey and sweat.",
        "The Seductress has bloomed. Heavy red flowers hang open, "
        "dripping thick nectar, and the whole garden smells sweet "
        "and a little indecent.",
        "The Seductress has overgrown its stake. Fat vines hang "
        "across the garden, flowers heavy as fists, and the thick "
        "scent follows you into every room.",
    ),
    "hungry_looks": (
        "The Seductress has gone very still. Every flower has turned "
        "toward the door, and the air smells of hunger.",
        "The Seductress is hungry. Its vines slither over the floor "
        "and under the door, and its flowers whisper your name.",
    ),
    "wilted": "The vine hangs limp and grey. It needs water, soon.",
    "texts": {
        "revive": "You water the {plant} again and again. Slowly, the "
                  "grey vine stirs and darkens.",
        "harvest": "You cut the open flowers and catch the nectar. The "
                   "vine sags and starts again from the root.",
        "seed": "A seed drops from one of the flowers.",
        "feed": (
            "You slip your cock into a warm, slick blossom. The petals "
            "fold tight around your shaft and the inside ripples, "
            "sucking you deeper. The vine milks you in slow, hungry "
            "pulls, until you spill into it with a groan. The flower "
            "drinks every drop and shivers, and your sweat soaks into "
            "its leaves.",
            "A fat vine uncurls and winds around your cock, slick and "
            "warm. It squeezes in a steady rhythm from the base to the "
            "tip, while a second tendril cups your balls and rolls them "
            "gently. You come hard into its mouth. The vine swallows "
            "everything, pulses once, and drinks your sweat as well.",
            "You push yourself into the heart of the blossom. Soft, wet "
            "petals close around your shaft and suck at it, while thin "
            "tendrils tease your balls and the underside of your cock. "
            "It does not hurry. It holds you right at the edge until "
            "you beg, and then it drains you completely, sweat and all.",
        ),
        "held": "The petals clamp shut around you and the vines coil "
                "around your hips. The plant is far too big to let go "
                "now. You will have to pull free.",
        "held_block": "The vines still hold you. Pull free first.",
        "pull": (
            "You pull back. The petals cling and suck at you, and the "
            "vine drags you in again.",
            "You brace your feet and heave. The blossom gives a little "
            "with a wet sound, and a tendril slips around your thigh.",
            "You twist and pull. The vine loosens, then squeezes once "
            "more, as if it wanted one more taste.",
            "You wrench yourself back, gasping, while the vines slide "
            "greedily over your skin.",
        ),
        "offer_ask": "Offering yourself to the Seductress is final. If "
                     "nobody pulls you out within three days, you die. "
                     "Confirm only if you mean it.",
        "offer": "You step into the blossom. The petals close over you, "
                 "soft and wet. The vine sighs and starts to digest.",
        "seduce": "The scent hits you and your knees give way. The "
                  "petals are so soft, and the vine so warm. You do not "
                  "even try to fight it.",
        "warn_take": "The Seductress sways toward you, vines creeping "
                     "across the floor, petals dripping. She is starving, "
                     "and the next thing you do in this house, she will "
                     "take you. Calm her first, or leave.",
        "take": "The vines have waited long enough. They coil around you "
                "and pull you into the blossom, which seals over you "
                "with a wet sound.",
        "victim_look": "{name} is sealed inside the blossom, a shadow "
                       "behind the red petals. The vine pulses slowly. "
                       "{left} days are left.",
        "pod_look": "A hardened pod in the shape of {name} hangs on the "
                    "vine, ridged and warm.",
        "rescue": "{rescuer} tears the vines apart and drags {name} out "
                  "of the blossom, gasping and slick.",
        "rescued": "{rescuer} tears the vines apart and drags you out of "
                   "the blossom. You gasp for air.",
        "dead": "You are dead – digested by the Seductress in the "
                "garden. You sit out until the new day begins.",
        "pod_harvest": "You cut the pod from the vine. It is still "
                       "faintly warm.",
        "freed": "With a last wet pop you tear yourself out of the "
                 "blossom. The vines slide away, and the plant sways "
                 "contentedly while your legs shake.",
        "feed_store": "Somewhere deep in the vine, nectar starts to "
                      "gather.",
        "feed_wilted": "The vine is too limp to drink. Water it first.",
        "feed_done": "The vine has drunk from you already this run.",
        "feed_small": "You are not big enough for the vine to take hold "
                      "of.",
        "feed_dry": "You are too dry. The vine wants sweat.",
        "drained": "The starving Seductress drains you as you walk in. "
                   "Feed it, or harvest it.",
        "drained_off": "The vine has had its fill. The weakness fades.",
        "bloom_buff": "The scent of the blooming Seductress clings to "
                      "you.",
    },
}

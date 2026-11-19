GORM_NAME = "Gorm"
GORM_ID = "npc-gorm"


FISH_BY_RARITY = {
    "common": ("fish_pike", "fish_perch", "fish_eel"),
    "rare": ("fish_goldcarp", "fish_blindcat", "fish_moortrout"),
    "epic": ("fish_sturgeon", "fish_siren"),
}


FISHER_BUFFS = {
    "fish_survivor": {
        "label": "Hooked and released", "bonus": {"vitality": 4},
        "text": "",
    },
}


VENUE_TEXTS = {
    "fisher": {
        "intro": "🎣 A narrow plank jetty runs out over black, still water "
                 "to a tiny island with a crooked hut. On the planks sits "
                 "an ogre the size of a barn door, a fishing rod as long "
                 "as a mast across his knees. A bucket beside him carries "
                 "a plaque: 'GORM'S – RODS 30 G. BAIT NEGOTIABLE.'",
        "door": "'Mind the planks,' he rumbles without turning around. "
                "'Fish bite better when it's quiet.'",
        "enter": "🎣 The party crosses the jetty and ducks into the "
                 "hut. Nets hang from the beams, hooks as big as "
                 "hands line the wall, and Old <<npc.old_gorm_first>> <<npc.old_gorm_last>> lowers his "
                 "head under the rafters to nod hello.",
        "look_outside": "🔎 A jetty on black water, an island with a "
                        "crooked hut, and an ogre who has not moved in "
                        "an hour. Something large circles under the "
                        "planks.",
        "look_inside": "🔎 A one-room hut that smells of tar and kelp. "
                       "Nets, barrels of salt, a bunk made for something "
                       "twice human size, and a wall of iron hooks.",
        "hooks": "On the beam hang the hooks of earlier bait, each with "
                 "a name scratched into the wood: {names}.",
        "no_hooks": "The hooks on the beam are all clean. Nobody has been "
                    "used as bait here yet.",
        "options": "Actions: {options} ({seconds} s)",
        "cast_poor": "{name} can't pay <<npc.old_gorm_first>>'s rod fee ({price} gold, has "
                     "{gold}).",
        "cast_limit": "<<npc.old_gorm_first>> shakes his head. '{name}, the pond has seen "
                      "enough of you for today.'",
        "cast_full": "{name}'s bag is full – the fish flops back into the "
                     "water.",
        "cast_start": "{name} pays {price} gold, takes the huge rod and "
                      "casts it into the dark water. The float sinks "
                      "slowly.",
        "boot": "{name} hauls in an old boot, black with water. <<npc.old_gorm_first>> "
                "nods gravely. 'A good start.'",
        "bite": "Something heavy takes the line and drags {name} to the "
                "jetty edge, snapping, before it lets go. (-{hp} HP)",
        "bait_confirm": "<<npc.old_gorm_first>> lifts a hook the length of a forearm and "
                        "looks at {name} thoughtfully. 'Bait, then?' "
                        "Press Bait again to confirm. Whatever bites "
                        "decides what happens next.",
        "bait_gone": "<<npc.old_gorm_first>> already has a line in the water. 'One at a "
                     "time. Patience.'",
        "bait_unknown": "<<npc.old_gorm_first>> looks around. 'Who?'",
        "bait_start": "<<npc.old_gorm_first>> hooks {name} through the harness and swings "
                      "{them} out over the black water. The float "
                      "sinks.",
        "bait_survive": "The line goes taut, then slack. <<npc.old_gorm_first>> reels in "
                        "{name}, soaked, stinking and alive. Something "
                        "huge simply let go. <<npc.old_gorm_first>> raises an eyebrow. "
                        "'Never seen that. Lucky bait.'",
        "bait_survive_line": "✨ {name}: {bonus} until the end of the run.",
        "bait_caught": "The line sings. After a long struggle <<npc.old_gorm_first>> "
                       "heaves the giant fish onto the planks. He pats its "
                       "flank. 'Take it. Pays for the bait.'",
        "bait_catch_line": "The catch is worth a feast. <<npc.old_gorm_first>> cuts "
                           "it up for the party.",
        "lie_limit": "{name} has already spent time with <<npc.old_gorm_first>>.",
        "lie_intro": [
            "<<npc.old_gorm_first>> sets the rod aside and looks at {name} for a long time. "
            "'I want a child,' he says plainly. 'Stay, and I will make "
            "one with you.'",
            "<<npc.old_gorm_first>> gestures at the wide bunk without a word. {name} "
            "follows the look.",
            "<<npc.old_gorm_first>> sets the rod down for the first time. 'Rest, if you "
            "like. Not just for sleep.'",
        ],
        "lie_dom": "{name} pushes the ogre onto the bunk, and <<npc.old_gorm_first>> lets "
                   "{them}, slow and amused.",
        "lie_gorm": "<<npc.old_gorm_first>> takes {name} by the hip and lifts {them} onto "
                    "the bunk without effort.",
        "lie_taste": {
            0: "<<npc.old_gorm_first>> nods politely. 'Not my kind of catch, but welcome.'",
            1: "<<npc.old_gorm_first>> hums. 'Fair. Not what I came here for, but fair.'",
            2: "<<npc.old_gorm_first>>'s eyes narrow with interest. 'Good size. Good "
               "weight. I like what I see.'",
            3: "<<npc.old_gorm_first>> sits up straight, beard bones rattling. 'A real "
               "one. Every inch honest. Stay a while.'",
        },
        "fake": {
            "bust": "<<npc.old_gorm_first>> flicks a finger against {name}'s chest. "
                    "'Bladders. Fish float better.'",
            "butt": "<<npc.old_gorm_first>> squeezes {name}'s behind and frowns. 'Filler. "
                    "Honest fat has weight.'",
            "endowment": "<<npc.old_gorm_first>> looks at {name}'s crotch. 'Silicone. A "
                         "lure, not a catch.'",
            "balls": "<<npc.old_gorm_first>> weighs {name}'s balls in one palm. 'Stuffed. "
                     "Real ones hang lower.'",
        },
        "depart": "<<npc.old_gorm_first>> raises a hand without looking away from the "
                  "water. 'Come back when it's calm.'",
    },
}


LIE_SCENE_GORM = [
    "He settles {name} across his lap and the bunk groans. His hands are "
    "broad as shovels and astonishingly patient. He explores slowly, "
    "unhurried as a man watching a float, and every touch takes its time "
    "to arrive. By the time his thick, heavy length presses against "
    "{name}, {name} is begging for the bite.",
    "<<npc.old_gorm_first>> lays {name} on the bunk on {their} stomach and strokes a "
    "palm the width of a plate down {their} back. He is gentle, "
    "enormous and tireless. {name} gasps as he lowers himself and "
    "starts a slow, deep rhythm that rocks the whole hut like a "
    "boat on a swell.",
    "'Easy,' he rumbles, and holds {name} in the crook of one arm while "
    "the other hand does slow, expert work. He waits for the exact "
    "moment, as he waits for a fish, then takes {name} with a long "
    "steady thrust that makes the nets sway.",
    "The ogre pulls {name} onto the bunk against his chest, big hands "
    "spreading {them} wide. He does not hurry. He takes one long, deep "
    "stroke after another, patient as the tide, until {name} is "
    "shaking and soaked and clinging to his beard.",
]


LIE_SCENE_DOM = [
    "{name} climbs on top and takes the reins. <<npc.old_gorm_first>> lies back, hands "
    "folded behind his head, grinning in his beard. 'Do as you like. I "
    "have all day.' {name} sinks onto him and sets the pace, "
    "and he lets {them}, big chest heaving.",
    "{name} pins <<npc.old_gorm_first>>'s wrists to the bunk, which he allows, "
    "amused. 'Go on, then.' {name} takes what {they} want, "
    "grinding hard against him, while <<npc.old_gorm_first>> watches with half-closed "
    "eyes and a low, pleased rumble.",
    "{name} shoves the ogre down onto the planks and straddles him. "
    "<<npc.old_gorm_first>> chuckles and does nothing at all, which "
    "makes it worse, because every move {name} makes meets "
    "enormous, patient resistance, warm as stone in the sun.",
    "'Calm water,' <<npc.old_gorm_first>> murmurs, as {name} rides him hard and "
    "greedy. 'But you make waves.' He holds {name}'s hips and lets "
    "{them} do the work, a smile hidden somewhere in the beard.",
]


LIE_CLIMAX_GORM = [
    "{name} breaks first, arching, crying out into his neck. <<npc.old_gorm_first>> "
    "follows with a deep, shuddering groan that rattles the hooks on "
    "the wall, and the hut goes still. 'Good bite,' he murmurs.",
    "The hut shakes on its stilts as <<npc.old_gorm_first>> finishes inside {name} with a "
    "low roar. He holds {them} close afterwards, breathing like a "
    "slow tide, and says nothing at all.",
    "{name} comes undone, shuddering and spent, and <<npc.old_gorm_first>> gives a "
    "long, satisfied sound, like a net being hauled in full. He wipes "
    "{their} hair back with one huge thumb. 'Caught,' he says.",
]


LIE_CLIMAX_DOM = [
    "{name} takes the last stroke hard and shudders over him. <<npc.old_gorm_first>> "
    "grips the bunk, the wood cracks, and he lets out a long, helpless "
    "rumble. 'You can come back,' he says. 'I mean it.'",
    "{name} finishes with a cry, and <<npc.old_gorm_first>> follows with a heave "
    "that lifts the bunk off the floor. He lies there afterwards, "
    "dazed, smiling at the rafters. 'That was no calm water.'",
    "<<npc.old_gorm_first>> comes with a groan that shakes the hooks on the wall, then "
    "laughs, big and warm. 'Takes a lot to move me. Well done.'",
]


LIE_AFTER = [
    "<<npc.old_gorm_first>> lays a huge hand on {name}'s belly and smiles into his "
    "beard. 'If it takes, I will teach it the water. If not, "
    "come back.'",
    "<<npc.old_gorm_first>> cuts a slab of smoked fish and hands it over. 'Eat. You "
    "worked up an appetite.'",
    "<<npc.old_gorm_first>> tucks a blanket over {name} and turns back to his rod. "
    "'Rest a moment. The pond will wait.'",
    "<<npc.old_gorm_first>> walks {name} to the jetty and presses a fish "
    "into {their} hands. 'For the road.'",
]

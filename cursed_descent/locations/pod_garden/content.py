VENUE_TEXTS = {
    "pod_garden": {
        "intro": "🌺 The path ends at a living curtain of heart-shaped "
                 "leaves, each as wide as a door and glossy with dew. "
                 "Beyond it the swamp opens into a terraced garden, warm "
                 "as a bathhouse and heavy with the smell of honey and "
                 "sweat. Pods hang from thick vines or rest in the black "
                 "mud in neat rows, ripe and swollen, every one shaped "
                 "by the body it holds. A few of them are still "
                 "trembling.",
        "intros": [
            "🌺 The path ends at a living curtain of heart-shaped leaves, "
            "each as wide as a door and glossy with dew. Beyond it the "
            "swamp opens into a terraced garden, warm as a bathhouse and "
            "heavy with the smell of honey and sweat. Pods hang from "
            "thick vines or rest in the black mud in neat rows, ripe and "
            "swollen, every one shaped by the body it holds. A few of "
            "them are still trembling.",
            "🌺 Night-blooming flowers the size of cartwheels open as the "
            "party passes, one after another, breathing out a sweet "
            "pink mist. Behind them lies a garden that somebody, or "
            "something, has tended with great patience. Terraces of "
            "dark soil, trellises of braided vines, and between them "
            "pods in every size, warm to the eye even from here, as if "
            "each one had a pulse.",
            "🌺 The air thickens until it is hard to tell breath from "
            "perfume. Ahead, the vines have woven themselves into "
            "arches and the arches into a long green hall. Down both "
            "sides, pods hang like lanterns, glistening and ripe, "
            "swaying gently though there is no wind. Somewhere inside "
            "one of them, something sighs.",
        ],
        "options": "Actions: {options} ({seconds} s)",
        "look_outside": "🔎 A hidden garden of pods.",
        "look": "🔎 The garden is laid out in terraces, watered by a "
                "slow black stream that smells of nectar. Heart-shaped "
                "leaves turn to follow you, and the vines that hold the "
                "pods flex and loosen with a soft creak whenever you "
                "step close. Every pod has a name written in the shape "
                "of it. The ones that are ready can be cut free:",
        "look_pod": "  [{nr}] {kind} – {name}, stage {stage}\n"
                    "      {look}",
        "look_none": "🔎 The beds are empty. Rows of bare trellis wait "
                     "in the humid dark, and the vines hang slack and "
                     "patient. Nothing here is ripe yet.",
        "none": "The garden is quiet. There is nothing ready to harvest.",
        "depart": "The party leaves the garden. The leaves close behind "
                  "them with a soft, wet rustle, and for a long while "
                  "the scent clings to everyone's skin.",
        "gone": "That pod is already taken.",
        "harvest": "{scene}",
        "own": "🌺 {name} stops in front of the pod and does not move "
               "for a long time. The outline is unmistakable: {their} "
               "own shoulders, {their} own curve, {their} own folded "
               "hands. The vines hold very still, as if waiting to see "
               "what {name} will do. Then {name} takes out a knife and "
               "cuts it free anyway.",
        "bloom": "💧 The rind gives with a wet crack, and warm, thick goo "
                 "slides out over {name}'s hands, sweet as honey and "
                 "faintly shivering: {item}.",
        "seed": "🌱 Tangled in the roots under the pod {name} finds a "
                "small hard seed that smells of sweat and flowers: "
                "{item}.",
        "gear": "🎁 Something hard is still folded inside the pod, "
                "preserved in the pale resin: {item}.",
        "full": "{name}'s bag is full.",
    },
}
KIND_NAMES = {
    "classic": "Classic Pod", "pumpkin": "Pumpkin Pod",
    "tuber": "Tuber Pod", "cocoon": "Vine Cocoon",
    "nectar": "Nectar Pod", "burrow": "Root Burrow Pod",
    "flytrap": "Flytrap Pod",
}
POD_LOOKS = {
    "classic": "A long, glossy pod, stretched over the outline of "
               "{name}. Folded tight, back arched, held in place by "
               "pale vines. The skin is faintly warm and slick, and "
               "somewhere in it a heartbeat slows.",
    "pumpkin": "A small, ridged, orange pod, hard as seasoned wood. "
               "{name} was folded into it so tightly that every curve "
               "shows through the rind like a relief carving. It is "
               "very heavy for its size.",
    "tuber": "A fat, knobbled root sac, half buried in the mud. The "
             "earth around it is warm and damp, and the shape under "
             "the thin skin is unmistakably {name}, curled up and "
             "wrapped in fine pink rootlets.",
    "cocoon": "A tall cocoon of braided vines, hanging upright from a "
              "trellis. {name} is wrapped from throat to ankle, arms "
              "pinned to the hips. The vines still flex slowly, as "
              "if keeping time to something.",
    "flytrap": "A great green flytrap, its two lobes folded shut over "
               "{name} and locked together by a row of stiff teeth. "
               "A little syrup beads along the seam, and the shape "
               "inside shifts every time the trap breathes.",
    "nectar": "A heavy, flower-like sac full of golden syrup, petals "
              "folded shut over it. {name} hangs inside, weightless "
              "and relaxed, the sweet fluid moving in slow, gentle "
              "waves around the figure.",
    "burrow": "A mound of soft earth, tangled with barbed roots. The "
              "roots are knotted around a hollow in the shape of "
              "{name}, and the dirt still carries the imprint of every "
              "limb that was pulled tight.",
}
HARVEST_SCENES = {
    "classic": "🌺 {name} slides a blade along the seam of the pod and "
               "the vines give way with a sigh. Warm air rolls out, "
               "thick and sweet, and the pod comes free in one heavy, "
               "slippery piece. It smells of someone you almost know. "
               "You are carrying a {kind}.",
    "pumpkin": "🌺 {name} takes the pumpkin pod in both hands and twists "
               "it from its stalk. It is hard and ridged and surprisingly "
               "light for how heavy it looks, and every curve of "
               "the shape beneath the rind presses back against {name}'s "
               "palms. It is a very good {kind}.",
    "tuber": "🌺 {name} digs around the root with both hands, finding "
             "the soft, warm dirt, until the whole sac comes loose with "
             "a wet pop. It trembles once and goes still. A fine {kind}, "
             "still faintly warm.",
    "cocoon": "🌺 {name} cuts the braided vines at the top and the cocoon "
              "slumps into {name}'s arms with all its weight, the vines "
              "twitching as they die. What is left is a hard, "
              "pale-green {kind}, shaped like a standing figure.",
    "flytrap": "🌺 {name} slips a blade between the teeth and pries the "
               "lobes apart. The trap gives up its catch with a wet, "
               "reluctant sound, trailing strings of syrup, and folds "
               "down into a heavy green bundle. A glossy {kind}, "
               "dripping and warm.",
    "nectar": "🌺 {name} peels the petals apart. The nectar runs thick "
              "and gold over {name}'s wrists, and the sac sinks "
              "slowly into a bundle that fits the crook of an arm. "
              "{name} holds a {kind}, warm and sticky and very sweet.",
    "burrow": "🌺 {name} loosens the barbed roots one by one until the "
              "whole mound lifts out of the mud in a single knot. It is "
              "heavier than it should be and covered in tiny scratches. "
              "A rare {kind}.",
}
MARKERS = (("pumpkin", "pumpkin"), ("tuber", "tuber"),
           ("cocoon", "cocoon"), ("flytrap", "flytrap"),
           ("nectar", "nectar"),
           ("burrow", "burrow"))

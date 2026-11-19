REMAINS_TEXTS = {
    "statue": "🪦 A statue stands in the corridor – {dead}, frozen "
              "mid-swing, still wearing {their} gear. A plaque reads: "
              "'Petrified by {killer}.'",
    "wall": "🪦 A relief juts from the wall: {dead}'s startled face, one "
            "hand still reaching out of the stone.",
    "door": "🪦 The next door has {dead}'s face. It sighs softly as the "
            "party approaches.",
    "eaten": "🪦 Gnawed bones lie around a cold fire pit. A torn bag with "
             "{dead}'s name stitched into it lies beside them.",
    "roasted": "🪦 An old spit over a burnt-out fire. Next to it, a helmet "
               "with {dead}'s initials serves as a soup bowl.",
    "swallowed": "🪦 Before a temple altar lies a pile of gear, licked "
                 "clean. {dead}'s belongings are among it – amazons don't "
                 "eat armor.",
    "breeding": "🪦 From a side tunnel comes a familiar voice – {dead}'s. "
                "The {tribe} guarding the pens look far too pleased. "
                "{Their} old bag lies at the entrance.",
    "dissolved": "🪦 A puddle of dried slime holds a clean skeleton and "
                 "{dead}'s polished weapon.",
    "encased": "🪦 A gelatinous cube drifts past in the distance – inside, "
               "perfectly preserved, floats {dead}.",
    "ice_statue": "🪦 Frost creeps across the floor. In an alcove stands "
                  "{dead}, carved in clear blue ice, still wearing {their} "
                  "gear. {Their} breath hangs frozen in front of {their} "
                  "lips.",
    "entombed": "🪦 A sarcophagus with a brass plate: '{dead}'. The lid "
                "is slightly ajar.",
    "soulbound": "🪦 A blade stuck in the floor whispers in {dead}'s voice. "
                 "It won't come out.",
    "own": "{name} recognizes {their} own remains. The curse has a cruel "
           "sense of humor.",
    "item": "Something of {dead}'s still lies here: {item}.",
    "no_item": "Whatever {dead} once carried is long gone.",
    "commands": "Actions: [loot] | [pray] | [pass]{extra} ({seconds} s)",
    "stew": "The pot is still half full of {dead}. [taste] it or [pack] "
            "a jar for later.",
    "stew_gone": "The pot has been scraped clean – someone got here first.",
    "taste": "{name} dips a ladle into the pot. Tastes like {dead} – a "
             "little gamey, but filling. The party heals {percent}% HP.",
    "taste_own": "{name} tastes the stew made of {their} former self. "
                 "Honestly? Could use more salt. The party heals {percent}% "
                 "HP.",
    "taste_spoiled": "{name} takes a big spoonful – and regrets it at once. "
                     "{dead} has gone off. Everyone loses {percent}% HP.",
    "pack": "{name} fills a jar with what is left of {dead}. Waste not, "
            "want not.",
    "pack_own": "{name} packs a jar of {their} own stew for the road. "
                "Self-reliance at its finest.",
    "no_stew": "There is nothing here to eat. Thankfully.",
    "dairy_bucket": "Something sloshes in a bucket next to the stall. "
                    "([loot] takes it along.)",
    "dairy_gone": "The buckets are empty – someone milked this stall dry "
                  "before you.",
    "dairy_found": "{name} finds a {item} in the stall, neatly labeled "
                   "'{dead}'.",
    "dairy_found_own": "{name} finds a {item} in the stall – with {their} "
                       "own name on the label. Awkward.",
    "dairy_full": "There is a {item} too, but {name}'s bag is full.",
    "loot": "{name} takes {dead}'s {item}. {dead} won't need it anymore.",
    "loot_own": "{name} takes back {their} {item}. It still smells of "
                "{their} last fight.",
    "loot_none": "{name} searches the remains but finds nothing of value.",
    "pray": "{name} kneels and says a few words for {dead}. A warm glow "
            "flows through the party (+{percent}% HP).",
    "pass": "The party leaves {dead} to the dungeon.",
}

SKELETON_TEXTS = {
    "appear": "🦴 Bones rattle in the dark. A skeleton shambles closer, "
              "still wearing scraps of {dead}'s gear. What's left of {dead} "
              "still wants a fight.",
    "crypt": "🦴 The crypt is restless – the skeleton of {dead} climbs out of "
             "an open grave.",
    "own": "🦴 {name} stares at {their} own skeleton. It stares back with "
           "empty sockets – and takes up {their} old fighting stance.",
    "rest": "🦴 The bones of {dead} clatter to the floor and finally lie "
            "still. Rest well.",
    "item": "Among the bones lies something {dead} once carried: {item}.",
}

EXAMINE_TEXTS = {
    "remains": "🔍 {name} crouches down and takes a closer look:",
    "killer": "The marks point to {killer} – one of {tribe}.",
    "first": "As far as anyone can tell, this was {dead}'s first time down "
             "here.",
    "history": "Not {dead}'s first trip, either: {count} {deaths}, "
               "most often {fate}.",
    "item": "Something is still here: {item}",
    "no_item": "Nothing of value is left – someone was here first.",
    "neighbours": "Others fell on stage {stage} too: {names}.",
    "nothing": "🔍 There is nothing here worth a closer look.",
    "more": "  … and {count} more.",
    "soul": "{dead}'s eyes are empty – the soul was swallowed by a "
            "soul-hungry {weapon}.",
    "venue": "🔍 A closer look at everyone here:",
    "boutique": "🔍 You read the little tags sewn into each piece:",
    "statues": "🔍 You read the little plaques on the statues:",
}

SOUL_HUNGER_TEXTS = [
    "🗡 Whatever happens to the body – the {weapon} has already taken its "
    "share. {name}'s soul is pulled screaming into the blade, where it will "
    "whisper to every future owner.",
    "🗡 The {weapon} was hungry all along: it drinks {name}'s soul before "
    "the body even hits the floor. Somewhere far away, <<npc.morgrin_first>> the Ashen "
    "Smith smiles into his forge.",
]

CONSORT_TEXTS = {
    "appear": "❄ The air turns bitter cold. Among the enemies walks {dead} "
              "– once an adventurer, now the Lich Queen's consort, eyes "
              "burning blue.",
    "own": "❄ {name} stares into {their} own frozen face. The consort "
           "doesn't recognize {them}.",
    "freed": "❄ The frost cracks off {dead}. For a heartbeat {they} "
             "{look} grateful – then {they} {crumble} into fresh snow. The "
             "Queen has one husband less.",
    "item": "Something of {dead}'s clatters out of the snow: {item}.",
}

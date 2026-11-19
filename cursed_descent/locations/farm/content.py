EVENT_TEXTS = {
    "farmer": {
        "intro": "🐖 A pigman in dungarees leans on a pitchfork, a "
                 "branding iron glowing in a brazier behind him. 'Fine "
                 "strong backs! The farm could use a few more hands.' – "
                 "<<npc.old_trotter_first>> attacks!",
        "win": "<<npc.old_trotter_first>> tumbles into a hay bale and stays there. {name} "
               "raids his tool shed.",
    },
}


FARM_JOBS = {
    "milk": "the prize milk cow, bell ringing at every step",
    "plough": "hitched to the plough, turning the fields",
    "field": "hoeing turnips under the pigman foreman's eye",
    "mule": "hauling feed sacks as the farm's pack mule",
    "cum": "the farm's cum cow, bucket under the stall rail",
    "hen": "brooding eggs in the coop, feathered harness and red comb",
    "carriage": "pulling <<npc.old_trotter_first>>'s carriage to market, ribbons in the "
                "mane",
}


FARM_PRODUCTS = {
    "milk": {"base": "milk_bottle", "name": "{name}'s Fresh Milk"},
    "cum": {"base": "cum_flask", "name": "{name}'s Stud Cream"},
    "hen": {"base": "farm_eggs", "name": "Eggs from {name}'s Nest"},
    "plough": {"base": "farm_bread", "name": "Bread from {name}'s Furrows"},
    "mule": {"base": "farm_bread", "name": "Oat Loaf hauled by {name}"},
    "field": {"base": "farm_bread",
              "name": "Turnip Bread from {name}'s Field"},
    "carriage": {"base": "farm_bread",
                 "name": "Market Loaf fetched by {name}"},
    "stallion": {"base": "farm_bread",
                 "name": "{name}'s Stallion-Ploughed Bread"},
}


FARM_PRODUCT_NOTES = {
    "kept": "<<npc.old_trotter_short>> Farm's finest – {name} works here for good",
    "shift": "from <<npc.old_trotter_short>> Farm – {name} worked a shift for this batch",
}


FARM_SHIFT_TEXTS = {
    "start": "🐖 <<npc.old_trotter_first>> spits in his palm and shakes {name}'s hand. "
             "'A shift of {turns} turns as my {role}. {pay} gold a turn, "
             "paid when you're done – if you're still… available.'",
    "start_plough": "{name} is hitched to the plough. The field is long.",
    "start_milk": "{name} gets a cowbell and a cow-print collar and is led "
                  "to the milking stall.",
    "start_cum": "{name} gets a cowbell, a cow-print collar and a polished "
                 "steel bucket and is led to the milking stall. A strap "
                 "goes round {their} hips, a rubber sleeve goes on and a "
                 "pigman farmhand clicks the pump on. 'Nice and steady, "
                 "now.'",
    "start_hen": "{name} is fitted with a feathered harness and a little "
                 "red comb and led into the coop. The other hens stare.",
    "start_mule": "{name} gets saddle bags, a lead rope and a very heavy "
                  "first sack.",
    "start_carriage": "{name} is fitted with a polished harness, a bridle "
                      "and ribbons in the mane, then backed between the "
                      "shafts of <<npc.old_trotter_first>>'s market carriage. <<npc.old_trotter_short>> "
                      "climbs onto the box seat and picks up the reins.",
    "stallion": {"base": "farm_bread",
                 "name": "{name}'s Stallion-Ploughed Bread"},
}


FARM_PRODUCT_NOTES = {
    "kept": "<<npc.old_trotter_short>> Farm's finest – {name} works here for good",
    "shift": "from <<npc.old_trotter_short>> Farm – {name} worked a shift for this batch",
}


FARM_SHIFT_TEXTS = {
    "start": "🐖 <<npc.old_trotter_first>> spits in his palm and shakes {name}'s hand. "
             "'A shift of {turns} turns as my {role}. {pay} gold a turn, "
             "paid when you're done – if you're still… available.'",
    "start_plough": "{name} is hitched to the plough. The field is long.",
    "start_milk": "{name} gets a cowbell and a cow-print collar and is led "
                  "to the milking stall.",
    "start_cum": "{name} gets a cowbell, a cow-print collar and a polished "
                 "steel bucket and is led to the milking stall. A strap "
                 "goes round {their} hips, a rubber sleeve goes on and a "
                 "pigman farmhand clicks the pump on. 'Nice and steady, "
                 "now.'",
    "start_hen": "{name} is fitted with a feathered harness and a little "
                 "red comb and led into the coop. The other hens stare.",
    "start_mule": "{name} gets saddle bags, a lead rope and a very heavy "
                  "first sack.",
    "start_carriage": "{name} is fitted with a polished harness, a bridle "
                      "and ribbons in the mane, then backed between the "
                      "shafts of <<npc.old_trotter_first>>'s market carriage. <<npc.old_trotter_short>> "
                      "climbs onto the box seat and picks up the reins.",
    "laid": "🥚 The nest under {name} holds {count} eggs by the end of the "
            "shift. <<npc.old_trotter_short>> adds them to the batch.",
    "stallion": "<<npc.old_trotter_first>> looks {name} over and whistles. 'Now THAT's a "
                "proper workhorse. Extra pay for you.'",
    "no_cum": "<<npc.old_trotter_first>> squints at {name}'s hips. 'Nothing to pump "
              "there, love. Try the milking stall.'",
    "start_burden_plough": "{name} is stripped to the harness. <<npc.old_trotter_short>> "
                           "buckles a wide leather strap round {their} "
                           "heavy sack, runs the trace chains through "
                           "it and hooks them to the plough. 'Lean into "
                           "it, beast. The field won't turn itself.'",
    "start_burden_carriage": "{name} is backed between the shafts, and "
                             "<<npc.old_trotter_short>> fastens a padded strap round "
                             "{their} heavy sack, the carriage traces "
                             "clipped to it. 'Beast of burden, "
                             "that's you now. Don't stop till the "
                             "market.'",
    "burden_status": "  Stamina {stamina}/{maximum} – every step pulls "
                     "at the strap.",
    "burden_collapse": "{name}'s legs give out under the strain. The "
                       "traces go slack, the strap drags {them} down "
                       "into the mud, and the load rolls back. Old "
                       "<<npc.old_trotter_short>> sighs, unbuckles {them} and ties "
                       "{them} to the stall. From now on: {job}.",
    "no_carriage": "<<npc.old_trotter_first>> shakes his head. 'The carriage needs a real "
                   "stallion, love. Try the plough.'",
    "turn": "🐖 {name} – shift turn {turn}/{turns}:",
    "status": "  Earned so far: {earned} gold · <<npc.old_trotter_short>>'s interest: "
              "{chance}%  ([work] or [quit])",
    "done": "🐖 The shift is over. <<npc.old_trotter_first>> counts out {gold} gold for "
            "{name}. 'Come back any time.' {name} rejoins the party – a bit "
            "smellier, a lot richer.",
    "batch": "🐖 <<npc.old_trotter_short>> labels a fresh batch: {count}× {item}. 'Sells "
             "better with a name on it.' It'll be on his shelf next time.",
    "quit": "{name} slips out of the harness and walks off the job. <<npc.old_trotter_short>> "
            "grumbles and pays half: {gold} gold.",
    "kept": "<<npc.old_trotter_first>> has made up his mind. 'Too good to let go.' The "
            "branding iron is already hot – {name} stays on <<npc.old_trotter_short>> Farm "
            "for good, {job}.",
    "collapse": "{name} collapses in the mud, completely spent. Old "
                "<<npc.old_trotter_short>> tuts, heats the branding iron… and keeps {them}. "
                "From now on: {job}.",
    "no_cow": "<<npc.old_trotter_first>> squints at {name}'s chest. 'Nothing to milk "
              "there, love. Try the plough.'",
    "again": "<<npc.old_trotter_first>> shakes his head. '{name}, you already had your "
             "shift today.'",
    "idle": "{name} isn't working a shift. "
            "([work horse|cow|cumcow|hen|mule|carriage])",
    "busy": "Not while {names} is still on shift. ([work] or [quit])",
    "quiet": "A quiet stretch. {name} works on in silence, sweat running "
             "down {their} back.",
}


FARM_BAD_ENDS = {
    ("cum", "kept"): ["stud", "tapped", "sold_brew"],
    ("cum", "collapse"): ["drained"],
    ("hen", "kept"): ["brooding"],
    ("hen", "collapse"): ["roast"],
}


BURDEN_ENDS = {
    "kept": ["circus", "farmed"],
    "collapse": ["torn"],
    "burden_collapse": ["hauled", "farmed"],
}


END_BATCHES = {
    "stud": ("cum", 8),
    "tapped": ("cum", 10),
    "sold_brew": ("cum", 6),
    "brooding": ("hen", 8),
}


END_KILLERS = {
    "sold_brew": "Astrid Creamworth",
    "circus": "the travelling circus",
}


HEN_AIDS = {
    "pill": [
        "<<npc.old_trotter_short>> fishes a greasy pill out of his overall pocket. 'Swallow, "
        "love. That gets the eggs going.' {name} gulps it down, feels a "
        "warm tug low in the belly and a strange urge to cluck.",
        "<<npc.old_trotter_short>> holds the pill up between two fingers like an egg. 'Down "
        "with it, dry. Hens don't drink on the job.' {name} chokes it "
        "down, and {their} belly starts to gurgle.",
    ],
    "suppository": [
        "<<npc.old_trotter_short>> tosses a finger-thick waxy suppository in the air and "
        "catches it. 'Bend over the hay bale.' {name} feels it slide in "
        "cold, and soon it turns very warm and very full.",
        "'Don't move until it melts,' <<npc.old_trotter_short>> grunts, holding {name} by "
        "the hip. The tug turns into a pressure, and {name} nearly "
        "clucks without being asked.",
    ],
}


HEN_LAYING = [
    "{name} squats in the straw, face flushed, and strains. A warm egg "
    "slides out with a wet little pop. The other hens cluck approval.",
    "A tight shudder runs through {name} and an egg drops into the "
    "nest, still steaming. <<npc.old_trotter_short>> picks it up with two fingers and "
    "holds it to the light. 'Beautiful.'",
    "{name} clucks, because the harness demands it, and pushes. One more "
    "egg, bigger than the last. {Their} thighs tremble.",
    "The foreman taps {name}'s belly like a melon. 'Another one's "
    "coming.' {name} groans, and it does.",
    "{name} lays an egg while the rooster watches. {name} would like to "
    "say something about that, but all that comes out is a cluck.",
]


BURDEN_TURNS = {
    "plough": [
        "The strap bites into {name}'s sack with every pull. The plough "
        "bites into the soil. Neither gives way. (-{hp} HP)",
        "{name} heaves, the chains snap taut and a deep furrow opens "
        "behind {them}. The whole weight hangs from {their} balls. "
        "(-{hp} HP)",
        "Every stone the plough meets yanks at the strap. {name} bites "
        "down a groan and keeps walking. (-{hp} HP)",
        "<<npc.old_trotter_short>> walks alongside, slapping {their} flank. 'Pull, "
        "beast! Heavy balls make heavy work!' (-{hp} HP)",
    ],
    "carriage": [
        "The carriage lurches over a rut and the traces jerk tight. "
        "{name} cries out, but the pull never stops. (-{hp} HP)",
        "Uphill, loaded with cabbages and the foreman's wife. {name}'s "
        "sack stretches against the strap with every step. (-{hp} HP)",
        "The market crowd claps along to {their} gait. {name} keeps the "
        "rhythm because stopping would hurt more. (-{hp} HP)",
        "<<npc.old_trotter_short>> flicks the reins. 'Faster! The strap holds, I "
        "checked it myself.' (-{hp} HP)",
    ],
}


BURDEN_TIRED = {
    "plough": "The ground ahead swims. {name} drags the plough on "
              "regardless.",
    "carriage": "{name}'s breath rattles. The carriage feels twice as "
                "heavy now.",
}


CUM_SCENTS = {
    "Equine": [
        "The stall smells of hay and hot stud, and the bucket under {name} "
        "is already filling.",
        "{name}'s musk is heavy in the stall now, rank and horsey. The "
        "pigman farmhand breathes through his mouth.",
        "The air in the stall has turned thick. {name} reeks of stallion – "
        "sweat, leather and the sharp tang of a stud in full flow. The "
        "mares next door whinny.",
        "{name} stinks like a whole stable in rut, so strongly that <<npc.old_trotter_short>> "
        "ties a cloth over his snout. The flavour in the bucket is "
        "just as brutal: salt, sweat and horse. 'That'll sell by the "
        "barrel.'",
    ],
    "": [
        "The stall smells of hay, leather and {name}.",
        "{name}'s sweat gives the cream a salty edge, and the farmhand "
        "sniffs the bucket with approval.",
        "{name} is dripping into the bucket as much as the pump is. <<npc.old_trotter_short>> "
        "dips a finger and tastes: 'Salty. Musky. Sells itself.'",
        "{name} is drenched from head to toe, and the whole stall smells "
        "of {them}. <<npc.old_trotter_short>> tastes the bucket and goes quiet. 'That's "
        "going on the good shelf.'",
    ],
}


FARM_SHIFT_EVENTS = {
    "plough": [
        ("gold", "{name} pulls a perfectly straight furrow. <<npc.old_trotter_first>> "
                 "whistles and adds {gold} gold to the pay."),
        ("hurt", "The plough catches on a buried rock and yanks {name} off "
                 "{their} feet. (-{hp} HP)"),
        ("sweat", "Noon sun, heavy soil. {name} strains against the "
                  "harness, sweat running in streams."),
        ("keep", "<<npc.old_trotter_first>> runs a hand along {name}'s harness. 'Strong "
                 "back. Shame to waste it on adventuring…'"),
    ],
    "milk": [
        ("item", "Milking time. {name}'s cowbell jingles while the buckets "
                 "fill. <<npc.old_trotter_short>> is delighted and bottles some for "
                 "{them}: {item}."),
        ("keep", "<<npc.old_trotter_first>> weighs today's buckets twice and starts "
                 "measuring {name} for a brand. 'Prize cow, this one…'"),
        ("gold", "A travelling merchant buys the morning milk at a premium. "
                 "<<npc.old_trotter_short>> shares {gold} gold."),
        ("hurt", "The farm's bull takes exception to the new cow and "
                 "charges. (-{hp} HP)"),
        ("sweat", "{name} grazes in the hot meadow with the other cows. "
                  "Peaceful. Suspiciously peaceful."),
    ],
    "cum": [
        ("item", "The pump hums, the bucket fills and {name}'s knees "
                 "tremble. <<npc.old_trotter_short>> pours a flask for {them}: {item}."),
        ("keep", "<<npc.old_trotter_first>> reads the bucket's level against the line "
                 "on the wall and writes something down. 'A natural. "
                 "Prize stud…'"),
        ("gold", "<<npc.astrid_first>>'s cart driver pays a premium for a fresh churn. "
                 "<<npc.old_trotter_short>> shares {gold} gold."),
        ("hurt", "The pump gets stuck on full. {name} yelps, the farmhand "
                 "swears and the sleeve burns. (-{hp} HP)"),
        ("sweat", "The stall is airless. {name} pants, flushed and "
                  "slick with sweat, while the pump keeps its rhythm."),
        ("sweat", "'Again,' says the farmhand, and flicks the pump back "
                  "on. {name} is already shaking."),
    ],
    "hen": [
        ("item", "{name} sits in the coop, feathers fluffed, keeping the "
                 "clutch warm. <<npc.old_trotter_short>> collects the eggs and hands {them} a "
                 "share: {item}."),
        ("hurt", "A fox slips into the coop! {name} drives it off but gets "
                 "bitten. (-{hp} HP)"),
        ("keep", "<<npc.old_trotter_short>> admires {name}'s fluffy harness. 'You look right "
                 "at home in there…'"),
        ("gold", "{name} clucks so convincingly that the foreman laughs and "
                 "tosses {them} {gold} gold."),
        ("hurt", "The rooster – a very proud pigman – disputes {name}'s "
                 "perch. Loudly, with his elbows. (-{hp} HP)"),
    ],
    "carriage": [
        ("gold", "Market day! The crowd cheers as {name} trots past, ribbons "
                 "flying. A merchant tosses {gold} gold into the cart."),
        ("hurt", "A pothole! The wheel jolts, the shafts jerk and {name} "
                 "stumbles to {their} knees. (-{hp} HP)"),
        ("sweat", "Uphill to the market town, the cart heavy with cabbages. "
                  "{name} is lathered in sweat."),
        ("keep", "<<npc.old_trotter_first>> pats {name}'s flank from the box seat. 'Best "
                 "carriage horse I ever had. Shame you're only renting.'"),
        ("hurt", "A horse thief tries to unhitch {name} at the market and "
                 "gets kicked into a fruit stand – but not before landing a "
                 "punch. (-{hp} HP)"),
        ("gold", "{name} wins an impromptu race against the miller's cart. "
                 "<<npc.old_trotter_short>> collects the bet: {gold} gold."),
    ],
    "mule": [
        ("hurt", "A sack of feed slips off the pile and lands on {name}. "
                 "(-{hp} HP)"),
        ("gold", "{name} hauls twice the load. <<npc.old_trotter_short>> adds {gold} gold."),
        ("sweat", "Up the hill, down the hill, up the hill. {name} is "
                  "soaked."),
        ("keep", "<<npc.old_trotter_first>> pats {name}'s saddle bags. 'Never had a mule "
                 "this obedient.'"),
    ],
    "any": [
        ("heal", "Lunch break: fresh bread, cheese and a mug of cream. "
                 "{name} feels better. (+{hp} HP)"),
        ("worker", "{worker}, branded with the farm's crest, works next to "
                   "{name} and whispers: 'Don't let him like you too much. "
                   "That's how it started for me.'"),
        ("keep", "The pigman foreman makes a note in his ledger next to "
                 "{name}'s name: 'Reliable.'"),
        ("hurt", "A goat headbutts {name} into the water trough. (-{hp} HP)"),
        ("gold", "{name} finds a coin purse in the hay – {gold} gold."),
        ("sweat", "The pigman foreman cracks his whip at the air. {name} "
                  "works faster."),
    ],
}


VENUE_TEXTS = {
    "farm": {
        "intro": "🐖 A wooden gate, a muddy yard, a red barn: 'TROTTER "
                 "FARM'. <<npc.old_trotter_first>> leans on the fence, chewing a straw.",
        "door": "The gate is open. Beyond it: mud, pens and a barn.",
        "enter": "🐖 The party crosses the muddy yard and steps through "
                 "the barn door.",
        "worker": "  • {dead} – {job}, branded with the farm's crest",
        "more": "  … and {count} more farmhands out in the far fields.",
        "astrid": "🍺 A cart rattles into the yard and a very tall woman "
                  "in a brewer's apron climbs down. <<npc.astrid_first>> <<npc.astrid_last>> "
                  "shakes <<npc.old_trotter_short>>'s hand and checks the shelf: 'I'll "
                  "take {count} flasks of {names} for my taproom.' She "
                  "pays {gold} gold to {name}'s party and drives off "
                  "with a clinking cart.",
        "nobody": "The fields are tended by ordinary pigs today.",
        "own": "{name} spots {their} own branded likeness out in the field. "
               "<<npc.old_trotter_first>> chuckles. 'Good worker, that one.'",
        "stock": "  [{nr}] {item} – {price} gold",
        "buy": "{name} buys {item} for {price} gold. Fresh from the farm.",
        "poor": "{name} can't afford {item} ({price} gold, has {gold}).",
        "full": "{name}'s bag is full.",
        "sellself": "{name} hands {their} gear over at the gate. <<npc.old_trotter_first>> "
                    "counts out {gold} gold, heats the branding iron and "
                    "leads {name} to the barn.",
        "known": "<<npc.old_trotter_first>> flips through his ledger and squints. "
                 "'{name}? Already branded, already working here. Well – "
                 "double shifts, then.' The gold is paid all the same.",
        "options": "Actions: {options} ({seconds} s)",
        "depart": "<<npc.old_trotter_first>> tips his hat. 'Come back any time – we're "
                  "always hiring.'",
    },
}

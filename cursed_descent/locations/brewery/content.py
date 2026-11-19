BREWERY_STYLES = {"yogurt": "Yogurt Drink", "kefir": "Kefir",
                  "lassi": "Lassi", "skyr": "Skyr Shake",
                  "curd": "Curd Smoothie"}


BREWERY_TEXTS = {
    "cum_delivery": "🐖 A farm cart is parked at the back door. Old "
                    "<<npc.old_trotter_short>>'s pigmen carry in steaming churns, and "
                    "<<npc.old_trotter_short>> himself haggles with <<npc.astrid_first>> over the price: "
                    "'Fresh from my stud stall – {names}.' <<npc.astrid_first>> sniffs "
                    "a churn and grins. 'Sell it on, I'll put a name on "
                    "the label.'",
    "cum_tag": "  delivered by <<npc.old_trotter_first>>, fresh from the stud stall",
    "intro": "🍺 Lantern light and a heavy, musky warmth spill from a low "
             "stone doorway under a hand-painted sign: 'CREAMWORTH'S – "
             "Creamy Brews, Yogurt Drinks & Special Arrangements'. Through "
             "the open shutters a very tall figure moves behind the bar.",
    "outside": "The door stands open. 'Customers!' booms a warm voice from "
               "inside. 'Don't just stand there, dears!'",
    "options": "Actions: {options} ({seconds} s)",
    "look_outside": "The party looks the taproom over. Copper kettles gleam "
                    "through the shutters, kegs are stacked to the rafters, "
                    "and a beaded curtain at the back hangs perfectly "
                    "still. The air smells of cream, musk and warm salt.",
    "look_hint": "Whatever is brewed in there, the sign promises 'Special "
                 "Arrangements'. Step inside with [enter], or move on with "
                 "[pass].",
    "board_out": "A chalkboard by the door, headed 'Backroom Regulars', "
                 "lists: {names}.",
    "board_out_empty": "The chalkboard by the door, headed 'Backroom "
                       "Regulars', is blank.",
    "pass": "The party walks past the taproom. <<npc.astrid_first>>'s voice follows them "
            "down the corridor: 'Come back thirsty!'",
    "enter": "🍺 The party ducks under the lintel into warm, lantern-lit "
             "air thick with cream and musk. <<npc.astrid_first>> <<npc.astrid_last>> looks up "
             "from her kettle and spreads her huge arms. 'Customers! Sit. "
             "Drink. Stay a while.'",
    "board_in": "Chalked on the board behind the bar under 'Backroom "
                "Regulars': {names}.",
    "board_in_empty": "The 'Backroom Regulars' board is blank. 'Slow "
                      "week,' <<npc.astrid_first>> sighs, looking the party up and down a "
                      "little too long.",
    "own": "{name} spots {their} own name on the 'Backroom Regulars' "
           "board, with a tally mark beside it. <<npc.astrid_first>> winks. 'Best "
           "customer I ever had.'",
    "look_shop": "🍺 The taproom: low black beams, copper kettles that "
                 "bubble day and night, and kegs stacked to the rafters, "
                 "each chalked with a name. A long, dark bar with a spoon "
                 "rack, a battered cash box and a beaded curtain behind it "
                 "that leads to the backroom. <<npc.astrid_first>> buys and sells "
                 "whatever you carry – and for the right price, she buys "
                 "you.",
    "look_keeper": "🧑‍🍳 <<npc.astrid_first>> <<npc.astrid_last>>, the Brew Master. A head taller "
                   "than the doorframe, fifty-odd years old, all broad "
                   "shoulders and corded forearms under a leather apron "
                   "that has clearly been let out more than once. Her skin "
                   "shines with the sweat of the kettles, her laugh rattles "
                   "the tankards and her smile is warm and motherly – "
                   "right up until she starts sizing you up like a fresh "
                   "batch.",
    "look_buys": "She also buys items from your bag: [sell <nr>], and "
                 "pours a fresh mug on request: [fresh].",
    "stock": "  {nr}. {item} – {price} gold{note}",
    "menu_sale": "For sale – [buy <nr>]:",
    "menu_bag": "Your bag – [sell <nr>]:",
    "offer": [
        "<<npc.astrid_first>> circles {name} slowly, nostrils flaring. 'Oh, you're "
        "dripping, dear. Such a lovely, musky sweat. You know... I'd love "
        "to churn one like you into something thick and creamy. {gold} "
        "gold, and I'll be gentle. [sellself] – just say the word.'",
        "<<npc.astrid_first>> leans over the bar and sniffs deeply. 'Mmm, {name}. If "
        "you ever want to be more than a customer, I'd make you one of my "
        "specials. {gold} gold, and I promise to savour every drop.'",
    ],
    "offer_drenched": [
        "'Look at you, {name}, soaked through,' <<npc.astrid_first>> purrs, eyes half "
        "closed, her apron swaying. 'You're the best-smelling thing to "
        "walk in here all year. I'd pay a premium – {gold} gold – to turn "
        "you into my finest batch yet. Thick, creamy, musky. Think about "
        "it, dear.'",
        "<<npc.astrid_first>>'s breath catches as {name} steps up to the bar. 'Oh, "
        "heavens. You're dripping. Let me make you into something "
        "wonderful – {gold} gold, and the best keg I've ever tapped. "
        "[sellself], whenever you're ready.'",
    ],
    "menu_fresh": "Fresh from the tap – [fresh]: {price} gold, the "
                  "strength is a surprise ({left} left – <<npc.astrid_first>> has to rest "
                  "and refill in between).",
    "menu_fresh_dry": "Fresh from the tap: <<npc.astrid_first>> is spent and needs to "
                      "rest and refill – no more fresh mugs here.",
    "talk_warn": (
        "🍺 <<npc.astrid_first>>'s smile thins a little as she drums her fingers on the "
        "bar. 'Are you going to order something, dear? Talking is free, "
        "but kegs aren't.'",
        "🍺 <<npc.astrid_first>> licks her lips, her eyes drifting slowly over {name}. "
        "'Last chance, dear. Buy something – or I'll help myself to a "
        "refreshment.'",
    ),
    "forced": [
        "'You've talked enough, dear,' <<npc.astrid_first>> says sweetly, and one big "
        "hand closes gently but firmly around {name}'s arm. No coins "
        "change hands. The beaded curtain falls shut behind them. A wet, "
        "hungry slurping starts up, a long gulp, a muffled 'wait–' cut off "
        "mid-word. <<npc.astrid_first>> returns alone, flushed and glistening, a hand "
        "cradling the heavy sway beneath her apron. 'Ah. Fresh keg's "
        "tapped. Now, who's thirsty?'",
        "<<npc.astrid_first>>'s patience runs out with a sigh. 'I do love a chatty "
        "customer – so easy to carry.' She scoops {name} up with one arm "
        "and sweeps through the curtain, deaf to every protest. Gobbling "
        "and gulping, one squeal that gets quieter and quieter, then a "
        "deep, contented sigh. She steps out alone, dabbing her brow. 'No "
        "charge, dears. That one was on the house.'",
        "'Time is money, dear,' <<npc.astrid_first>> says, and the lock on the front "
        "door clicks. Before {name} can answer, {name} is lifted off the "
        "floor and carried through the curtain. Slurping, greedy gulping, "
        "a last muffled whimper lost in the clatter of the kettles. "
        "<<npc.astrid_first>> returns alone, wiping her chin with her apron. 'Don't "
        "look so shocked, dears. You did say you were only here to "
        "talk.'",
    ],
    "fresh_tired": "<<npc.astrid_first>> is panting now, flushed and glistening, and "
                   "the heavy sway beneath her apron is visibly lighter. "
                   "'One more, dear – then I need a break.'",
    "fresh_dry": "<<npc.astrid_first>> sags against the bar, fanning her face, her "
                 "apron hanging slack. 'That's all I have for now, loves. "
                 "A girl needs time to rest and refill.'",
    "fresh_empty": "<<npc.astrid_first>> shakes her head, wiping her brow. 'The tap's "
                   "run dry, dear. Even I have to rest and refill "
                   "sometimes. Come back next time.'",
    "ad": "🪧 A sandwich board by the door, in <<npc.astrid_first>>'s tidy chalk: "
          "'TODAY'S SPECIAL – {item}! {quality}. {stock}.'",
    "ad_in": "🪧 Chalked above the bar: 'TODAY'S SPECIAL – {item}! "
             "{quality}. {stock}.'",
    "ad_none": "🪧 A sandwich board by the door, in <<npc.astrid_first>>'s tidy chalk: "
               "'SOLD OUT of house specials – fresh batches wanted! Ask "
               "inside about our Special Arrangements.'",
    "ad_quality": {"common": "Honest, thick and cold",
                   "rare": "Rich, thick and creamy",
                   "epic": "The finest batch in the house"},
    "ad_stock_one": "1 batch in stock",
    "ad_stock_many": "{count} batches in stock",
    "ad_own": "<<npc.astrid_first>> winks at {name}: 'Recognize the flavour, dear? "
              "{item} – one of our best sellers. I kept the best part of "
              "you.'",
    "special_tag": "  ★ today's special",
    "gear_tag": " (left behind by {name} – {smell})",
    "gear_tag_feet": " (left behind by {name} – {size}, {smell})",
    "gear_size_words": {"tiny": "tiny", "short": "small",
                        "average": "medium", "tall": "big",
                        "huge": "enormous"},
    "gear_smell_words": ("neutral", "faintly musky", "smelly", "reeking"),
    "gear_feet": "<<npc.astrid_first>> comes back out carrying {name}'s {item} between "
                 "two fingers and holds them up to the lantern. {size_line} "
                 "{smell_line} She hangs them on the hook behind the bar. "
                 "'Those go in the shop.'",
    "gear_size_lines": {
        "tiny": "They are tiny, hardly bigger than her palm.",
        "short": "They are small and dainty, easily lost in her big hand.",
        "average": "They are a perfectly ordinary size.",
        "tall": "They are big and broad, a good handful each.",
        "huge": "They are enormous, each one the size of a small bucket.",
    },
    "gear_smell_lines": (
        "She sniffs them: neutral, nothing but leather and dust.",
        "She sniffs them and hums: faintly musky, a warm, pleasant hint of "
        "foot.",
        "She sniffs them and her eyes half close: properly smelly, thick, "
        "warm and very personal.",
        "She sniffs them and sways on her feet: ripe and reeking, a heavy, "
        "eye-watering musk that fills the whole taproom.",
    ),
    "gear_other": "On her way out <<npc.astrid_first>> drapes {name}'s {item} over the "
                  "hook behind the bar. {smell_line} 'Can't swallow "
                  "everything, dear. That goes in the shop.'",
    "gear_other_smell": (
        "It smells of nothing at all.",
        "It carries a faint, warm musk.",
        "It is damp and heavily musky.",
        "It reeks of sweat, a heavy, drenching musk.",
    ),
    "gear_eaten": "{name}'s {item} didn't come out again. <<npc.astrid_first>> burps "
                  "politely behind her hand. 'Pardon me.'",
    "fresh_pay": [
        "{name} slides {price} gold across the bar. <<npc.astrid_first>> sweeps the "
        "coins into her cash box with a wink and takes the biggest mug "
        "from the shelf. 'Fresh one, coming up, dear. Watch closely.' She "
        "ducks it below the counter, right in front of the party.",
        "'A fresh one? My favourite order.' <<npc.astrid_first>> pockets {price} gold "
        "from {name}, takes a heavy mug from the rack and lowers it out "
        "of sight beneath the bar, never taking her eyes off the party.",
    ],
    "fresh_work": [
        "Her shoulders begin to move, slow at first, then in a steady, "
        "rhythmic pull, her thick forearms working under the counter. The "
        "bar creaks in time. A low moan rumbles out of her and her face "
        "flushes. Somewhere beneath the wood there is a wet sloshing, "
        "then more of it.",
        "Both arms start to pump beneath the counter, a steady rhythm "
        "that shakes the tankards on the shelf. <<npc.astrid_first>> bites her lip, her "
        "breath comes heavy, and a deep, shuddering moan fills the "
        "taproom. The sloshing grows louder, thicker, faster.",
        "Her big arms move in long, slow strokes, her whole body swaying "
        "with them. 'Mmm... hold on, dear...' she groans, eyes half "
        "closed. The sloshing builds, a thick, heavy sound, until a last "
        "long, shaking groan ends it and something fills the mug.",
    ],
    "fresh_serve": [
        "<<npc.astrid_first>> straightens up, flushed and glistening, a little out of "
        "breath, and sets the mug in front of {name}. It is thick, pale "
        "and creamy, still warm, with a heavy musk that rises off it like "
        "a wall. 'Fresh,' she says. 'Drink up.'",
        "With a satisfied sigh <<npc.astrid_first>> slides the mug across the bar to "
        "{name}. It steams gently, thick and creamy and nearly "
        "overflowing, its musk so heavy it makes the lantern flames lean. "
        "'Straight from the tap. Careful – it's strong.'",
    ],
    "fresh_hair": [
        "Something curls on the creamy surface: a coarse, dark pubic hair, "
        "floating dead centre. <<npc.astrid_first>> glances at it, shrugs and grins. "
        "'House special, dear. Don't fish it out, it's good luck.'",
        "{name} spots a single wiry pubic hair stuck to the rim, still "
        "damp. 'Oh, that's mine,' <<npc.astrid_first>> says without a trace of shame, "
        "'I do work up close. Drink around it or don't.'",
        "A pubic hair twirls in the foam. 'Ah, bit of me in every mug,' "
        "<<npc.astrid_first>> laughs, wiping her hands on her apron. 'That's how you "
        "know it's fresh.'",
    ],
    "tap_hint": "🚰 <<npc.astrid_first>> pats her enormous balls, still churning and "
                "gurgling as they work the fresh batch. 'Still warm, loves. {victim} is on tap – [tap] if "
                "you want it straight from the source.'",
    "tap_drink": [
        "{name} kneels in front of <<npc.astrid_first>>, who lifts her apron. A wave of "
        "sweat and heavy musk rolls over {name}: her thick cock is hot, "
        "slick with sweat and smells like a day at the kettles. {name} "
        "takes it between {their} lips, and <<npc.astrid_first>> groans, cupping her "
        "enormous balls, still churning and gurgling at their work. A long, warm stream floods {name}'s mouth – "
        "{victim}, fresh and creamy – and {name} swallows every gulp "
        "while <<npc.astrid_first>> strokes {their} hair. 'Good {name}. Straight from "
        "the tap.'",
        "'Open wide, dear,' <<npc.astrid_first>> rumbles, and {name} does, tongue out, "
        "eyes up. Her cock is warm and damp with sweat, its musk so "
        "strong it makes {name}'s head swim. She works herself over "
        "{name}'s face until she shudders, her huge balls still working and "
        "clenching, and the first thick spurt hits {their} tongue. {victim} pours out in heavy, steaming ropes, "
        "salty-sweet, and {name} drinks it down, moaning around her "
        "sweaty shaft.",
        "{name} wraps both hands around <<npc.astrid_first>>'s shaft – hot, sticky "
        "with sweat, reeking of her work – and gets it into {their} "
        "mouth. Her giant balls churn and slosh with {victim}'s batch, "
        "still hard at work; with a deep sigh she lets go, and warm cream pumps down {name}'s throat, "
        "load after load, the smell of her sweat filling {their} nose. "
        "'Don't spill, dear. Fresh is best.'",
    ],
    "tap_done": "<<npc.astrid_first>> pats her balls and laughs. 'Not again so soon, "
                "{name}. Let them fill up first.'",
    "tap_none": "<<npc.astrid_first>> cups her balls and shrugs. 'Nothing fresh yet, "
                "dear. Bring me someone and I'll be heavy again.'",
    "fresh_item": "🍶 {name} receives {item}.",
    "fresh_poor": "<<npc.astrid_first>> shakes her head. 'A fresh one is {price} gold, "
                  "dear. You have {gold}.'",
    "fresh_full": "{name}'s bag is full. <<npc.astrid_first>> holds the mug just out of "
                  "reach. 'Make some room first, dear.'",
    "menu_self": "Or sell yourself – [sellself]: <<npc.astrid_first>> offers {gold} "
                 "gold{extra}.",
    "menu_self_gear": " ({base} for you + {value} for your {item}, which "
                      "she hangs in her shop at that price)",
    "discount": "<<npc.astrid_first>>'s eyes linger on you. 'For you, dear, {percent}% "
                "off.'",
    "greet": [
        "<<npc.astrid_first>> wipes her hands on her apron. 'What'll it be, {name}? "
        "Something cold and thick?'",
        "'Sit, {name}, sit! You look like you could use a drink.'",
        "'Ah, {name}! The new keg has just been tapped.'",
    ],
    "greet_sweaty": [
        "<<npc.astrid_first>> sniffs the air. 'Mmm, {name}. You've been working hard. "
        "Sit down before you fall over, dear.'",
        "<<npc.astrid_first>>'s eyes half close. 'Oh, {name}, you smell like a proper "
        "adventurer. Come here, let me pour you something.'",
    ],
    "buy_what": "'Which one, dear? [buy <nr>] – [shop] shows the menu.'",
    "buy": "{name} buys {item} for {price} gold. <<npc.astrid_first>> slides it across "
           "the bar. 'Drink up, dear – thick and cold.'",
    "poor": "{name} can't afford {item} ({price} gold, has {gold}).",
    "full": "{name}'s bag is full.",
    "sell_what": "'Sell what, dear? [sell <nr>] – your bag number.'",
    "sell": "{name} slides {item} across the bar. <<npc.astrid_first>> weighs it in one "
            "huge hand and counts out {price} gold. 'Fair enough.' "
            "(Gold: {gold})",
    "fresh": "🍶 A fresh keg is chalked up for the next customers: {item}.",
    "sweaty": "<<npc.astrid_first>> sniffs the air and her eyes half close. 'Mmm. "
              "You've been working up a proper sweat. I pay extra for "
              "that.'",
    "sellself": "{name} sets the tankard down and names a price. <<npc.astrid_first>> "
                "counts out {gold} gold, bolts the front door and holds "
                "the beaded curtain aside. 'Backroom's this way.' The "
                "curtain falls shut.",
    "sellself_gear": "That is {base} gold for {name} and {value} gold for "
                     "{their} {item}.",
    "known": "<<npc.astrid_first>> runs a finger down the board and grins. '{name}? "
             "Back again? Same terms, then.' The gold is paid all the "
             "same.",
    "not_inside": "<<npc.astrid_first>> calls through the door: 'Come in first, dear!' "
                  "([enter])",
    "invalid": "<<npc.astrid_first>> tilts her head. 'Can't do that here, dear.' "
               "Actions: {options}",
    "depart": "<<npc.astrid_first>> raises a tankard. 'Mind the stairs on the way out. "
              "And come back thirsty.'",
}


ASTRID_GROWTH = (
    (12, "Under her apron her balls have grown absurd, each the size of a "
         "small keg and sloshing audibly with every step. She turns "
         "sideways to get through the kitchen door.",
     "<<npc.astrid_first>> returns alone, and her balls are fuller than ever, absurd, "
     "keg-sized and glistening, sloshing so loudly that the whole taproom "
     "falls silent to listen. She has to turn sideways to get through the "
     "beaded curtain."),
    (6, "Under her apron her balls hang enormous and brimming, swaying and "
        "churning audibly with every step.",
     "<<npc.astrid_first>> returns alone, and her balls are even fuller than before, "
     "enormous, swollen and swaying, sloshing and churning loudly enough "
     "to be heard across the taproom. She cradles them with one hand as "
     "she walks."),
    (3, "Under her apron her balls hang swollen and tight, sloshing a "
        "little whenever she moves.",
     "<<npc.astrid_first>> returns alone, and her balls are visibly fuller than before, "
     "tight and heavy and straining the apron, churning audibly. "
     "Something inside gives a muffled thump."),
    (1, "Under her apron her balls hang full and heavy, and a faint "
        "gurgling can be heard when she moves.",
     "<<npc.astrid_first>> returns alone, and her balls hang fuller than before, heavy "
     "and swaying, with a faint gurgle inside them at every step."),
)


FRESH_TIERS = ((450, "Overflowing", "epic"), (360, "Heavy", "epic"),
               (260, "Thick", "rare"), (170, "Warm", "common"),
               (0, "Thin", "common"))


BREW_GRADE_LABELS = {"common": "", "rare": "Rich", "epic": "Double-Cream"}

EVENT_TEXTS = {
    "hunter": {
        "intro": "🎩 A man in a pith helmet and monocle steps out from "
                 "behind a pillar, rifle raised. 'Splendid! Simply "
                 "splendid! You'll look magnificent above my fireplace.' – "
                 "<<npc.reginald_first>> <<npc.reginald_last>>, big game hunter, attacks!",
        "win": "<<npc.reginald_first>> topples over, monocle shattering. 'Bad… "
               "form…' {name} goes through his hunting bag.",
    },
}


HUNTER_HUTS = {
    "lodge": {
        "name": "<<npc.reginald_last>> Hunting Lodge",
        "intro": "🎩 Antlers over the door, a brass plaque – '<<npc.reginald_last>> "
                 "Hunting Lodge, members only'. The door is unlocked. "
                 "Inside, a fire crackles for nobody.",
    },
    "cabin": {
        "name": "the Trapper's Cabin",
        "intro": "🎩 A log cabin wedged into a side cave, smelling of "
                 "pipe tobacco and taxidermy glue: one of <<npc.reginald_first>>'s "
                 "many hunting cabins.",
    },
    "manor": {
        "name": "the Trophy Wing of <<npc.reginald_last>> Manor",
        "intro": "🎩 A grand corridor of polished wood and gilded frames – "
                 "the trophy wing of <<npc.reginald_last>> Manor, somehow built right "
                 "into the dungeon.",
    },
}


LODGE_DISPLAYS = (
    ("rug", "a rug by the fireplace"),
    ("armchair", "an armchair"),
    ("chaise", "a chaise longue"),
    ("sofa", "the sofa"),
    ("coat stand", "a coat stand in the hall"),
    ("desk", "a little trophy on the desk"),
    ("bar", "a trophy above the bar"),
    ("wall", "a trophy on the wall"),
    ("mounted", "a trophy on the wall"),
)


VENUE_TEXTS = {
    "hut": {
        "outside": "Nobody answers the knock. Muddy boot prints lead away "
                   "from the door – <<npc.reginald_first>> seems to be out hunting.",
        "enter": "🎩 The party slips inside. Glass eyes stare down from "
                 "every wall.",
        "search_gold": "{name} rifles through <<npc.reginald_short>>'s writing desk and "
                       "pockets {gold} gold from a cigar box.",
        "search_item": "{name} pries open the gun cabinet. Something of "
                       "<<npc.reginald_short>>'s is still in there.",
        "search_journal": "{name} finds <<npc.reginald_short>>'s hunting journal. A page "
                          "lists his lodges:",
        "journal_line": "  • {hut} – near stage {stage}",
        "return_search": "🎩 'And what, pray tell, are you doing in MY "
                         "desk?' <<npc.reginald_first>> stands in the doorway, rifle "
                         "already raised. 'Burglars make the finest "
                         "trophies.'",
        "eat": "{name} raids <<npc.reginald_short>>'s larder: cold game pie, smoked "
               "haunch, a decanter of port. The party eats like kings and "
               "heals {percent}% HP. Everything is neatly put back.",
        "cook": "{name} builds up the fire in the lodge's great stone "
                "hearth, hangs a spit over the flames and roasts {food}. "
                "The smell fills the trophy hall; the glass eyes seem to "
                "watch. Everything is eaten before the coals cool.",
        "return_cook": "🎩 Smoke from HIS chimney, a spit over HIS fire. "
                       "<<npc.reginald_first>> <<npc.reginald_last>> stands in the doorway, "
                       "rifle level. 'Cooking in my hearth, {name}? Bold. "
                       "I shall mount you above it.'",
        "return_eat": "🎩 A fork halfway to {name}'s mouth, a key in the "
                      "lock. <<npc.reginald_first>> <<npc.reginald_last>> stands in the doorway, "
                      "rifle level. 'My pie! My PORT! Oh, you shall make a "
                      "splendid centrepiece.'",
        "display": "  • {dead} – {display} (fell on stage {stage})",
        "empty": "The walls are bare, the plaques blank – <<npc.reginald_first>> "
                 "has not filled this place yet. He is still hunting.",
        "more": "  … and {count} more trophies in the back rooms.",
        "own": "{name} finds {their} own glass-eyed likeness among the "
               "trophies. The plaque underneath says 'Magnificent "
               "specimen'.",
        "rest": "{name} sinks into one of the lodge's 'armchairs'. It is "
                "very comfortable and does not complain. The party rests "
                "and heals {percent}% HP.",
        "sleep": "The party beds down among the trophies – {name} gets the "
                 "bearskin rug, which is definitely just a bearskin rug. A "
                 "hot bath in <<npc.reginald_short>>'s copper tub, a full night's sleep: "
                 "HP and mana restored, all the sweat washed off.",
        "scent": "🎩 Somewhere outside, a monocle glints. <<npc.reginald_first>> "
                 "lowers his nose from the wind. 'Fresh spoor. Very fresh.'",
        "return_rest": "🎩 Boots on the porch. A key in the lock. Sir "
                       "<<npc.reginald_short>> <<npc.reginald_last>> steps in, sees {name} sprawled in "
                       "his armchair – the living kind – and reaches for "
                       "his rifle. 'Trespassers! How… convenient. I have an "
                       "empty spot on the wall.'",
        "return_sleep": "🎩 {name} wakes to the click of a rifle hammer. Sir "
                        "<<npc.reginald_short>> stands over the sleeping party in his "
                        "dressing gown, monocle gleaming. 'Don't get up. I "
                        "prefer my specimens relaxed.' He fires before "
                        "anyone is fully awake!",
        "options": "Actions: {options} ({seconds} s)",
        "depart": "The party closes the lodge door quietly behind them.",
    },
}

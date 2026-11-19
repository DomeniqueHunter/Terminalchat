PRIVY_BUFFS = {
    "privy_relieved": {
        "label": "Relieved", "bonus": {"vitality": 2}, "text": "",
    },
    "privy_fresh": {
        "label": "Freshly washed", "bonus": {"agility": 1}, "allure": 3,
        "text": "",
    },
}


GRAFFITI = [
    "'HERE SAT HAROLD. HAROLD IS NO LONGER WITH US.' Someone added: 'He "
    "knew what he ate.'",
    "'Stage 31 is a lie.' Underneath, in different handwriting: 'Stage "
    "31 is just very long.'",
    "'For a good time ask for Brunhild.' Crossed out and corrected: "
    "'For a good education ask for Brunhild.'",
    "'The paddle maid takes volunteers. I did not volunteer.' The rest of "
    "the line is smeared.",
    "A neat little poem: 'Roses are red, the walls are damp, the curse "
    "is long, and I have a cramp.'",
    "'Do not trust the cheese.' An arrow points toward the east wall, "
    "where someone scratched: 'Cheese is fine. It is the cow.'",
    "'Wash your hands.' Next to it, a faded cross-stitch sampler says the "
    "same in prettier letters.",
    "A tally of 117 marks, then in red: 'I am still here.' Then another "
    "tally, shorter, in a different hand.",
    "'Whoever finds this: the third stall has a loose tile and under it "
    "there are two coins.' The tile is already gone.",
    "'The goblins pay in nuggets, the dwarves in lectures.'",
]


STALL_SCENES = [
    "{name} locks the door of the middle stall. Behind the thin boards "
    "someone hums an old marching song, badly. After a moment {name} "
    "hums the second verse, and the stranger next door falls silent in "
    "respect.",
    "{name} sits down and the whole booth creaks like a ship. From the "
    "next stall a hoarse voice says: 'Take your time, friend. Nobody "
    "here is going anywhere.' It is the most true thing {name} has heard "
    "all day.",
    "A small, pale hand slides a sheet of paper under the partition. "
    "'You looked like you could use it,' whispers a voice that is "
    "already gone by the time {name} says thank you.",
    "{name} finds a carved line in the wood: 'Breathe. Then go back "
    "out.' It helps more than {name} would like to admit.",
    "Somewhere beyond the wall a bard is rehearsing a love song to the "
    "echo in the pipes. {name} applauds. The bard applauds back. Both "
    "are quite moved.",
]


KNOCK_SCENES = [
    "{name} knocks on the last stall. 'Occupied!' squeals a goblin. 'In "
    "a minute!' A minute later nothing has happened. Two minutes later "
    "nothing has happened. {name} gives up.",
    "{name} knocks. The latch flies up and a lady in a velvet cloak "
    "peeks out, very red in the face. 'Please. Do not look. And do not "
    "tell anyone the high priestess uses this door.' She presses a coin "
    "into {name}'s hand and vanishes.",
    "{name} knocks and a cultist hisses: 'We are in the middle of a "
    "ritual!' From inside comes the sound of a chain being pulled and "
    "an enthusiastic: 'It worked!' {name} decides not to ask.",
    "{name} knocks, and the door swings open on its own. The stall is "
    "empty, but the seat is still warm and the walls whisper: 'Next.'",
]


GOSSIP = [
    "'Everyone passes through here sooner or later,' says Hedwig, "
    "counting her coins. 'Kings, cutthroats, even the paddle maid. They "
    "all sit the same.'",
    "'The gnomes want a stall with a lock they can reach. The dwarves "
    "want it deeper. The goblins want it free. I want it quiet.'",
    "'A girl came in here crying last week, and left laughing. I put a "
    "clean towel on her tab. Some days that is all a person needs.'",
    "'Do not step in the corner. I mean it. It is not what it looks "
    "like, it is worse.'",
    "'I knit one sock per customer. By now I have enough socks to equip "
    "a battalion.' She holds up a tiny, striped sock.",
]


SECRETS = [
    "She lowers her voice. 'The tiles under the sink are loose. Bring a "
    "chisel on your next visit, if you ever return.'",
    "She leans over the counter. 'There is a goblin who comes here "
    "every day and speaks to the third stall. The third stall answers.'",
    "'Do you know why the walls are so thick?' She smiles. 'So nobody "
    "hears what the corridor is saying.'",
]


URINAL_SCENES = [
    "{name} steps up to the long trough. A row of strangers stares "
    "straight ahead, and no one says a word. After a while someone "
    "mutters about the weather on stage 40. Everyone agrees it is bad.",
    "{name} takes the free place at the wall. The man on the left hums, "
    "the goblin on the right looks very hard at the ceiling. Hedwig calls "
    "from the counter: 'Eyes front, gentlemen!'",
    "{name} finds the urinal cold, tiled and unexpectedly clean. A little "
    "brass plate above it reads: 'AIM WITH CARE.' Somebody has added: "
    "'AND WITH HOPE.'",
]


ATTEND_SCENES = [
    "{name} takes over the counter, a stack of towels and a tin of "
    "lavender water. A goblin tries to pay with a button, an old knight "
    "with a speech about honour, and a bard with a song. {name} accepts "
    "the coins and throws the rest out.",
    "{name} spends an hour at the counter, handing out towels, taking "
    "tolls and reminding everyone to wash their hands. Hedwig watches "
    "with half an eye and knits half a sock.",
]


FIXTURE_SCENES = [
    "{name} is stood in the last bracket for a shift, a brass plate over "
    "{their} head and a sign that reads 'FIXTURE – PLEASE BE GENTLE'. "
    "Hedwig counts the line with her needles and is pleased with the "
    "takings.",
    "{name} spends the shift bolted to the wall at the end of the row, "
    "unable to move away. The queue pays Hedwig and the plate over "
    "{their} head collects fewer and fewer comments, and then none.",
]


VENUE_TEXTS = {
    "privy": {
        "intro": "🚽 A low stone hut with a moon cut into the door. A "
                 "sign in elegant, trembling letters reads: PUBLIC PRIVY "
                 "– 5 GOLD – PLEASE WASH YOUR HANDS. A faint smell of "
                 "lavender fights a faint smell of something else.",
        "door": "A queue of three people waits patiently in front of "
                "the door: a goblin shifting from foot to foot, a bard "
                "with a lute and a very serious face, and a figure in a "
                "heavy hood who does not look at anyone.",
        "options": "Actions: {options} ({seconds} s)",
        "look_outside": "The hut is clean and well-kept for a place "
                        "this deep. A chalkboard by the door lists the "
                        "rules: no spells, no singing, no lingering. "
                        "Someone has scratched out 'no singing'.",
        "depart": "Hedwig looks up from the sock. 'Mind the step, dear. "
                  "And do come again.' The door swings shut behind you "
                  "on a breath of lavender.",
        "enter": "You step inside. A narrow tiled passage, a row of "
                 "wooden stalls, a stone basin with a cracked mirror. "
                 "Behind a small counter sits Hedwig, an old woman with "
                 "knitting needles, a coin dish and an unreadable smile. "
                 "'Five gold for a stall, dear. The basin is free.'",
        "look": "Six stalls, a long urinal trough on the left, one stall marked OUT OF ORDER with a drawing of "
                "an unhappy face. The basin gleams. Lavender hangs "
                "from the ceiling in bundles. On the counter lie a "
                "coin dish, a tower of folded towels and a half-"
                "finished striped sock.",
        "stall": "{name} pays {price} gold and receives a small wooden "
                 "token.",
        "stall_poor": "'Five gold,' says Hedwig gently. {name} has {gold}. "
                      "She offers a sympathetic nod and a towel instead "
                      "of a stall.",
        "stall_used": "'One stall per customer, dear,' says Hedwig "
                      "without looking up.",
        "relieved": "{name} walks out of the stall lighter. {bonus}",
        "wash": "{name} scrubs hands and face in the cold basin. The "
                "cracked mirror shows someone who looks a little more "
                "like a person. {bonus}",
        "wash_used": "{name} has scrubbed enough for one day. The mirror "
                     "seems relieved.",
        "knock_used": "The stalls have heard enough from {name} for one "
                      "visit.",
        "knock_coin": "(+{gold} gold)",
        "read_used": "{name} has read every wall, door and tile twice. "
                     "Wait. There is a new line on the ceiling.",
        "ask_used": "'We have talked enough, dear,' says Hedwig, and "
                    "turns the sock.",
        "tip_poor": "{name} cannot afford a {price} gold tip (has "
                    "{gold}).",
        "tip_used": "'You already tipped, dear. Do not spoil me.'",
        "urinal": "{name} pays {price} gold and takes a place at the "
                  "trough.",
        "urinal_no": "'That one is not for you, dear,' says Hedwig, "
                     "pointing {name} toward the stalls.",
        "urinal_used": "'You have done that, dear,' says Hedwig without "
                       "looking up.",
        "urinal_poor": "{name} has {gold} gold. The trough costs {price}.",
        "stint_used": "'One shift each, dear,' says Hedwig. 'There are "
                      "others waiting.'",
        "stint_attend": "{name} works the counter and earns {gold} gold.",
        "stint_fixture": "{name} stands the shift and earns {gold} gold. "
                         "{warning}",
        "stint_warn": "Hedwig looks at the bracket at the end of the row, "
                      "then at {name}, and smiles very slightly.",
        "grumble_warn": "{name} grumbles about the smell. Hedwig stops "
                        "knitting. 'Careful, dear. The pipes could use "
                        "another fixture.'",
        "look_fixtures": "Along the wall hang brass plates, and behind "
                         "them the pipework hums:",
        "look_fixture": "  {nr}. {name} – a plate, a bracket, a quiet "
                        "face behind the pipes.",
        "look_no_fixtures": "The brackets at the end of the row are "
                            "empty. For now.",
        "tip": "{name} drops {price} gold into the dish. Hedwig "
               "bows by a fraction of a degree.",
    },
}

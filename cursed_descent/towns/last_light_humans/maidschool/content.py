GREETING = ("🎀 The Maid School – a huge old building smelling of starch "
            "and lavender. Headmistress Brunhild, broad, grey and "
            "frighteningly muscular, inspects you over her glasses. "
            "'Strict but fair, dear. Mostly strict.'")

SCOLDS = ("'Back straight! Do you want to be a maid or a sack of "
          "potatoes?' *crack*",
          "'Again. And this time with grace.' The whip sings past your ear.",
          "'Chin up, hands folded, eyes down. Tragic. Once more.'")

COURSES = {
    "fagsquat": {"title": "Fagsquat", "stat": "strength",
                 "blurb": "Low squatting that trains the glutes: +3 "
                          "strength and a visibly bigger backside.",
                 "butt": 4},
    "girlwalk": {"title": "Girl Walk", "stat": "agility",
                 "blurb": "Elegant gliding steps: +3 agility."},
    "manners": {"title": "Manners", "stat": "intelligence",
                "blurb": "Etiquette, tea and silent disapproval: +3 "
                         "intelligence."},
    "corset": {"title": "Corset Drill", "stat": "vitality",
               "blurb": "Marching, laced to the limit: +3 vitality."},
}

ENROLL_WARNING = ("⚠ Enrolling turns {name} into a maid NPC for good: the "
                  "character can no longer be played, loses ALL equipment "
                  "and bag, and keeps only the school uniform. A "
                  "graduate can be bought back for {price} gold per "
                  "level. Use [maidschool enroll confirm] within 30 seconds to "
                  "proceed.")

LESSONS = {
    "fagsquat": (
        "Day 1: Brunhild makes you hold a deep squat for an hour. "
        "'Lower! Lower! Your backside is a throne, not a hammock.' "
        "*crack* Your thighs scream.",
        "Day 2: Duck-walks around the courtyard with a bucket of "
        "water on each shoulder. 'Do not spill. Do not whimper.' "
        "You do both. The whip hums.",
        "Day 3: Slow squats with the headmistress sitting on your "
        "shoulders as weight. 'Good. Again.' Your whole lower body "
        "burns, and it looks wonderful."),
    "girlwalk": (
        "Day 1: Books on your head, heels on your feet, one long "
        "line of chalk across the hall. 'Step. Glide. Do NOT wobble.' "
        "*crack*",
        "Day 2: The line becomes a rope. Brunhild taps your hips "
        "with the whip to teach you where they belong. 'Sway, dear, "
        "don't stumble.'",
        "Day 3: You walk the length of the hall without a single "
        "book falling. 'Passable,' says Brunhild – the highest "
        "praise she has ever given."),
    "manners": (
        "Day 1: Forks, knives and the seven kinds of silence. "
        "'You hold a teacup like a weapon!' She is right.",
        "Day 2: Curtsies for an hour, then conversation without "
        "using the word 'actually'. Every slip earns a tap on the "
        "wrist.",
        "Day 3: A full formal tea with imaginary guests. 'Smile "
        "through the poison, dear. That is manners.'"),
    "corset": (
        "Day 1: Brunhild laces you with a knee in your back. "
        "'Breathe out!' You do. 'Again!' You cannot.",
        "Day 2: Marching drills in the corset, up and down the "
        "stairs with trays. 'Posture is a muscle. Use it.' *crack*",
        "Day 3: A full day laced to the limit while scrubbing "
        "floors. By evening you can breathe in exactly three ways "
        "and all of them are beautiful."),
}

GRADUATION = ("🎓 Brunhild pins a small silver brooch on you. 'You may "
              "go now.' She turns her back, but you see her smile. "
              "{title} is learned: +3 {stat}.")

LOCKED = ("🔒 You are in training at the Maid School (day {day}/{total}). "
          "Brunhild blocks the door: 'Not until I say so.' Only "
          "[maidschool day] and [maidschool quit] work now.")

QUIT = ("You throw down the broom and walk out. Brunhild does not shout: "
        "she simply notes the name. The fee is gone and the course "
        "forgotten.")


OFFER = "Enrol with [maidschool enroll] and learn some manners."

HELP = """🎀 Maid School
Headmistress Brunhild – strict but fair.
  maidschool                – courses, maids and graduates
  maidschool learn <course> – fagsquat, girlwalk, manners, corset
                              (150 gold, 3 days, +3 stat)
  maidschool day            – attend today's lesson (one day per call); while
                              training you cannot leave the school: no runs,
                              shops, bank or jobs
  maidschool quit           – drop out (fee lost)
  maidschool enroll         – become a maid for good (asks to confirm):
                              the character turns into an NPC, loses all
                              gear and keeps the uniform
  maidschool buyback <name> – buy a graduate back (300 gold per level)
  maidschool handover       – hand Connie, the paddle maid in your waiting
                              run, over to the school (she teaches there)
  maidschool look           – look for a maid; next (each further maid costs
                              a fee, five at most), prev, recruit (double
                              price) – hired maids join a party free via [hire]
Down in the dungeon <<npc.starch_first>> <<npc.starch_last>>, the school recruiter (stage {recruiter_stage}+), may
beat you down. Then [accept] makes you a maid (buy back for 300 gold per level)
or [decline] ends the run for you."""


HANDOVER = [
    "Brunhild looks Connie up and down, then nods once. {name} curtsies, "
    "tucks The Butt Buster under her arm and follows the headmistress "
    "into the school. Through the door you hear sisters squeal. 'I shall "
    "teach them how a paddle is held, ma'am,' {name} calls back.",
    "{name} smooths her apron and bows to {giver}. 'It was an honour. My "
    "sisters will want to hear of every lady.' Brunhild offers her tea, "
    "and the door closes behind them.",
]

CLIENTS = (
    "a shy tailor", "a laughing sailor", "a widowed blacksmith",
    "a travelling bard", "a young lord in disguise", "a stern magistrate",
    "a baker with flour on his sleeves", "a sleepy lantern-lighter",
    "a veiled foreign envoy", "an off-duty mimic hunter",
    "a nervous clerk", "a drunken sellsword", "a quiet baroness",
    "a guild accountant", "a broad-shouldered dockhand",
    "a masked stranger", "a bored town guard",
    "a giggling pair of students", "a retired captain",
    "a sweet-talking merchant",
)

ROSE_CHANCE = 0.3
ROSE_ACTIVE = ("Madame <<npc.rose_first>> looks you over and decides to try you "
               "herself tonight – she leads, you follow. 'Consider it a "
               "staff benefit,' she purrs.")
ROSE_PASSIVE = ("Madame <<npc.rose_first>> smiles, unlaces her gown and lets you take "
                "charge for a while. 'Don't make me regret the invitation.'")

ROSE_MID_CHANCE = 0.12
ROSE_MID_SUB_CHANCE = 0.22
ROSE_MID_BONUS = 15
ROSE_MID_WORKING = (
    "Madame <<npc.rose_first>> drifts through the room, ledger under one arm, and stops "
    "beside you. 'Good work, darling. A little more of that.' She slides "
    "a tip into your garter.",
    "Madame <<npc.rose_first>> watches from the doorway until the client is done, then "
    "walks over and pats your cheek. 'You are my best earner tonight. "
    "Don't tell the others.'",
    "Madame <<npc.rose_first>> steps in mid-scene, takes the client's chin in two "
    "fingers and smiles. 'Be kind to my girl.' Then she looks at you, "
    "approving, and presses a coin into your hand.",
)
ROSE_MID_SUB = (
    "Madame <<npc.rose_first>> slips in without knocking, locks the door behind her "
    "and looks you over. 'You are mine for a moment.' She takes what "
    "she wants and leaves you breathless.",
    "Madame <<npc.rose_first>> snaps her fingers and the client is sent out. 'My turn.' "
    "She takes charge of you, slowly and thoroughly, and pays well for "
    "it.",
)

ESCORT_INTRO = "You are collected in a carriage with curtains drawn."
ESCORT_RESULTS = (
    (3, "great", "The evening is magical. Your client pays far more than "
                 "agreed and kisses your hand at the door.", 2.0),
    (4, "fine", "A pleasant night of wine and quiet company.", 1.0),
    (2, "dull", "Your client talks about taxes all night. Paid, barely.",
     0.6),
    (1, "trouble", "Your client turns out to be a jealous duke's cousin. "
                   "You leave through a window, but with some coin.", 0.4),
)

NO_SHIFT = ("You are not on a shift. [job brothel whore] at the brothel "
            "starts one.")

FEMININE_CLIENTS = (
    "a shy seamstress", "a laughing sailor-woman", "a widowed innkeeper",
    "a travelling minstrel", "a young lady in disguise",
    "a stern magistrate's wife", "a baker with flour on her sleeves",
    "a sleepy lamp-seller", "a veiled foreign envoy", "an off-duty "
    "mimic huntress", "a nervous clerkess", "a tipsy sellsword woman",
    "a quiet duchess", "a guild accountant's daughter",
    "a broad-shouldered dockworker",
)


OWNER = "Madame <<npc.rose_first>>"
PLACE = ("🌹 The <<npc.rose_first>> Chamber – Madame <<npc.rose_first>> runs the house with a "
         "velvet smile and a very sharp ledger.")
CLOSED = "The <<npc.rose_first>> Chamber is shut while you are in the dungeon."
OFFER = ("Looking for work? [job brothel whore], [job brothel "
         "dancer], [job brothel waiter], [job brothel milk] or an "
         "[job brothel escort] for the lucky few.")
HELP = """🌹 Brothel
The <<npc.rose_first>> Chamber, owner Madame <<npc.rose_first>> (keeps 30% of your pay).
  brothel                   – list the jobs
  job brothel <job>         – whore, waiter, milk, dancer, escort
  serve <act> give|receive [tone]
                            – during a whore shift (6 clients): titfuck,
                              oral, anal, vaginal, facesitting, bdsm,
                              trampling, foot, watersports (a shower for
                              big bodies; with a cock also piss nursing),
                              scat, ballbusting, footjob,
                              pegging, spanking. Titfuck, oral,
                              anal, vaginal, ballbusting and footjob
                              (receive) depend on your body. Some clients want to be
                              dominated; matching their taste pays more.
                              Ballbusting give is a kick into the balls, add
                              'front' or 'back' (else random). Facesitting
                              and trampling (give) carry a ~4 % risk of
                              killing the client (more if you are heavier
                              than he is): you take his whole purse, the
                              shift goes on. Anal give with a cock: you come
                              inside him and his belly swells by your ball
                              size (it stays, regulars keep it).
  practices [act]           – what is possible for you, with descriptions
  Tone (sweet | teasing | stern): you and the client talk in every
  scene; the right tone for their mood pays +25%. Default follows your
  personality.
  book classic|fetish       – book a worker for yourself, relieves arousal
Madame <<npc.rose_first>> sometimes tries the staff herself."""


HOUSE_GUEST_HELLOS = (
    "'Do not mind me. I only came to see how this house treats its "
    "guests.'",
    "'Quality control, darling. Please do not take it personally.'",
    "'I heard good things about the staff. I wanted to see for myself.'",
)

OPERATOR_GUEST_HELLOS = (
    "'My house, my rules, my turn. Let us see what I am paying for.'",
    "'I only sell what I have tested. Today it is your turn.'",
    "'Do not look so nervous. The owner is simply checking the ware.'",
)

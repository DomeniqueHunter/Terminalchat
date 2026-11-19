from .spawns import min_stage
from .config import (
    ALLURE_DISCOUNT, ALLURE_DISTRACT, BIOME_SEGMENT, BOSS_INTERVAL,
    CHEST_CHANCE, CYCLE_LENGTH,
    BREWERY_FRESH_LIMIT, BREWERY_SWEAT_PRICE,
    BREWERY_TALK_LIMIT,
    CONSORT_MIN_STAGE,
    CITY_STOP_EVERY, CITY_STOP_FIRST, LOCATION_EVERY, PASS_BRIBE_COST,
    PASS_FEE, SMOKERY_CYCLES, SWEATERY_CYCLES, HUT_REST_HEAL, HUT_REST_RISK,
    HUT_SEARCH_RISK,
    HUT_SLEEP_RISK, HUT_STAGES,
    CURSE_ITEM_LOSS_CHANCE, EVENT_CHANCE,
    GENDERS,
    INVENTORY_SIZE, MAX_DISCOUNT, MAX_DISTRACT, MAX_PARTY_SIZE,
    MEAT_KG_PER_CUT, MEAT_MAX_CUTS,
    MIMIC_BASE_CHANCE, MIMIC_MAX_CHANCE, POINTS_PER_LEVEL,
    ROUND_TIMEOUT_SECONDS, SELL_RATIO, START_FREE_POINTS, START_STAT_VALUE,
    STRAY_CHANCE, STRAY_MIN_STAGE,
)
from .content import (
    BIOMES, COMBO_TITLES, ENEMIES, RARITY_LABELS, SPELLS, TITLES,
)


OVERVIEW = f"""📖 The Cursed Descent – Help
1-{MAX_PARTY_SIZE} adventurers descend into an endless dungeon. Every stage \
is harder than the last. Nobody survives – the curse revives everyone at the \
entrance. The goal: get deeper than anyone before you.

Quick start:
  1. [create] makes your character – answer the questions step by step
  2. [lobby] opens a party, others [join] or you [hire] a companion (one of your own characters)
  3. [start] begins the descent

Every action is a button in the window. You can also type it into the input
field with a leading '!' – e.g. '!hit' or '!buy 2'. Below, actions are written
without the '!'.
Short forms: !h hit, !c cast, !f force, !d dodge, !g guard, !p potion, !e enter,
!i inv, !s status. In the web window the keys h c f d g p e also press the
matching button while the input field is not focused.

Help topics:
  create   – creating your character
  stats    – what STR, AGI, VIT and INT do, levelling up
  party    – lobby, joining, starting
  combat   – how rounds work and all combat actions
  spells   – spells and how to unlock them
  items    – bag, equipment, loot, rarities
  chests   – treasure chests and mimics
  events   – strange people you meet between stages
  shop     – <<npc.velvet_first>>'s shop, gold, buying and selling
  clinic   – Dr. <<npc.vane_first>>'s body modifications
  smith    – <<npc.morgrin_first>>'s soul-hungry weapons
  town     – Last Light and its buildings
  bank     – safe storage for gold and items
  tavern   – jobs at the Gilded Tankard
  brothel  – Madame <<npc.rose_first>>'s house, jobs and bookings
  station  – trains between towns (buy a ticket for a line)
  rune_forge, mine_guild (Ironhold) | workshop, lab (Cogsworth) |
  black_market, arena (Mudgate) | blood_bank, salon, castle, tailor
  (Dusk Hollow) | ember_cask (Brandholm) – unique buildings: each
  lists its offers as buttons.
  Castle: sign a 24 h Contract of Keeping, serve, or buy out; the
  tailor sells clothes and bindings; [serve bondage] in Dusk Hollow
  cafe     – Madame Bertha's Fat Ass Café: stools, cakes, cushions
  maidschool – Brunhild's courses, maids and enrolling
  post_office – the post office of every town; [mail] works from anywhere
  tuning_room – The Tuning Room (Last Light): orientation training
  body     – height, weight, build, bust, muscle and more
  allure   – sexy gear and what it does
  remains  – finding what is left of earlier adventurers
  biomes   – the regions of the dungeon and their monsters
  classes  – titles you earn by how you fight
  death    – fates, the curse and the leaderboard
  commands – list of all actions"""

CREATE = f"""📖 Help – Creating a character
[create] guides you through 5 steps:
  1. Name – first and last name, e.g. 'Lyra Dawn'
  2. Gender – answer with a number or the name
     ({', '.join(GENDERS)})
  3. Body – one question per value: height, weight, build, bust (and how
     much of it is implants), muscle, butt – and for characters with a cock
     its length, girth, balls and shape. Send a value, 'ok' keeps the
     current one, 'back' goes one question back, 'rest' keeps everything
     that is left. Several values at once also work: 'height 180 bust 400'.
  4. Stats – distribute {START_FREE_POINTS} points across STR AGI VIT INT,
     answered as 4 numbers in that order, e.g. '4 1 3 2'.
     Every stat starts at {START_STAT_VALUE}.
  5. Summary – answer 'yes' to save or 'no' to start over

'cancel' aborts at any time, nothing is saved until you confirm. Every
character gets an ID that stays the same when it dies or is recreated.
Later the body can only be changed at Dr. <<npc.vane_first>>'s clinic, for gold."""

STATS = f"""📖 Help – Stats
STR – melee damage
AGI – chance to dodge, critical hit chance
VIT – hit points and armor
INT – spell damage, healing, mana, a little more loot

Each stage cleared gives EXP to every living party member, boss stages
(every {BOSS_INTERVAL}th) give double EXP.
Each level-up gives {POINTS_PER_LEVEL} free points:
[add <str|agi|vit|int> [amount]].
Level, stats and EXP are kept forever – the curse does not take them."""

PARTY = f"""📖 Help – Party
lobby  – open a party
join   – join the open party (max {MAX_PARTY_SIZE})
leave  – leave the party (only before the start)
hire <name> – recruit one of your other characters (free) or hire a
          mercenary for gold (without a name: the list). Companions
          fight on autopilot, level up and keep their gear
dismiss <name> – send a companion away (lobby only)
auto <name> [on|off] – switch a party member's autopilot (any hero, so you
                      don't have to set every fight action; off: you steer
          them yourself; without a name: show the state)
start  – begin the descent (any party member)
status – show the current stage, enemies and party
surrender – give up: the whole party falls to whatever is in front of
          it and the run ends"""

COMBAT = f"""📖 Help – Combat
Each round works like this:
  1. The game shows what every enemy is about to do
     (e.g. 'Ogre winds up for a crushing blow against Lyra!')
  2. Everyone picks one action – you have {int(ROUND_TIMEOUT_SECONDS)}s,
     whoever stays silent attacks automatically
  3. Everything happens at the same time, in this order:
     defense (dodge/guard) → healing and items → all attacks → deaths

Actions:
  hit [nr]               – melee, enemy number optional (default: weakest)
  cast <spell> [target]  – cast a spell (see [help spells])
  dodge                  – much higher chance to dodge this round
  guard [name]           – reduce damage to yourself or a party member
  use <nr|item> [name]   – use a potion from your bag

Tips: react to the announced enemy moves. Two players hitting the same
enemy can waste a hit (overkill). Someone who dies this round still acts.
Slimes resist melee but take extra damage from spells."""

ITEMS = f"""📖 Help – Items
Clearing a stage can drop loot (boss stages always do). INT raises the
chance a bit. Rarities: {', '.join(RARITY_LABELS.values())} – cursed items
are strong but come with a penalty.

inv                – show your bag (gear first, then consumables; {INVENTORY_SIZE}+ slots)
item <nr|slot|name> – examine an item: price, set, maker, former owner, gent/lady restriction, smell and sweat traces
examine <name|nr> – look at a character, NPC, local or enemy (bare examine still looks at the place)
equip <nr|name>    – put on an item (it knows its slot)
unequip <slot>     – take it off again; slots: weapon, head, chest,
                      gloves, feet, accessory, lingerie, crotch
use <nr|item>      – drink a potion during combat
drop <nr|item>     – throw an item away (works any time)
consume <nr|item>  – eat, drink or take a tonic outside of combat
needs              – hunger, thirst, sleep and arousal (0-100, higher is
                      worse); they rise every cleared stage. Hunger and
                      thirst hurt at the extreme, sleep is reset by resting,
                      arousal by relief. Provisions are sold in the shop.
give <nr|item> <player> – hand an item over; worn gear keeps the smell of
                      whoever wore it
home – one house per town (hut, row house, townhouse, manor); the Home
                      tab has everything as buttons: sleep in a real bed,
                      invite friends and any hero, let family (your son, ...)
                      or close friends move in (beds = 2 per room); residents
                      sleep there too. Parent and child are never intimate.
                      Shared activities and practices with a partner (their
                      gender and body are mentioned), small talk about work,
                      town or yourself, a title for you (Mistress, Master,
                      Queen, ...; used in later dialogues), a chest for gold
                      and items, and inviting a guest as domina, sub, seat or
                      throne ('throne' = you sit on the guest, never lethal).
                      A guest or resident can be sent away at any time.
                      Residents and guests who work in the café, brothel or
                      tavern are not home. Pregnant residents give birth
                      after 3 nights.
gift <npc> <item> | barter <npc> <item> | coach <npc> | romance <npc> – town
                      neighbours: presents raise friendship, barter sells an
                      item (50%), coaching trains one stat (needs
                      acquaintance, costs gold, 3 lessons per teacher),
                      romance needs a close friend
intimate <name> [position] [top|bottom] [little|some|much] [in|on] –
                      choose how: position (face, behind, rider, spoon, wall,
                      seated), who takes whom, how much and where it ends
                      (only 'in' can lead to pregnancy; same options for
                      romance and home romance)
intimate <name> | consent <name> | refuse <name> – a private moment between
                      party members (town or lit campfire only, adults, both
                      must agree); may lead to pregnancy
banter <name> [work|town|self] – talk to a party member; bonds grow, family
                      members get their own lines (GUI: Party tab)

Sets: some items belong to a set (e.g. Domina, a melee set with whip,
cap, corset, gloves, boots and riding crop). Wearing 2, 4 or 6 pieces
unlocks extra bonuses – [profile] shows which ones are active.

Items are kept between runs, but when the party falls the curse takes a
random item from your bag with a {int(CURSE_ITEM_LOSS_CHANCE * 100)}% \
chance. Equipped items are safe."""

CLASSES = """📖 Help – Classes
There are no fixed classes. Every action you take raises an affinity
(Melee, Magic, Dodge, Guard, Heal), and each affinity makes that action a
little stronger. Your title follows your two strongest affinities.

Single titles: {singles}
Combined titles: {combos}"""

DEATH = """📖 Help – Death
When you die you are out for the rest of the run. What happens to you
depends on who killed you: petrified into a statue, turned into wall
decor, made into a Door of Defeat, devoured raw by beasts, roasted on a
spit, dissolved or encased by slimes, worn as a giant's trophy,
swallowed whole by an amazon, kept as a dairy cow, or – by goblins,
orcs and amazons – taken as breeding stock. [profile] keeps count.

Not everything stays put. If you were eaten, roasted or dissolved, your
bones may rise as a skeleton and roam the dungeon – most of all the
Crypt. Lich consorts roam the deep halls. Beat them to lay them to rest
and get back whatever the curse took from them.

When the whole party has fallen the curse awakens: everyone wakes up at the
entrance. Your deepest stage is recorded, the best runs land on the
leaderboard – [top]."""

COMMANDS = """📖 Help – All actions
Profile:           create | gender <gender> | age <n> | personality <text>
                   profile [name] | sheet [name]
                  add <str|agi|vit|int> [n] | inv | drop <nr>
                  equip <nr>
                  unequip <slot> | give <nr|name> <player> | spells | top
                  consume <nr|name> | needs
Party:            lobby | join | leave | start | status | surrender
Combat:           hit [nr] | cast <spell> [target] | dodge
                  guard [name] | use <nr|item> [name]
Chest:            open | inspect | skip
Events:           accept | decline | charm | eat | talk | sit
                  give | sleep | depart
Shop:              shop | buy <nr> | sell <bag nr>
Remains:          loot | pray | pass | examine | taste | pack |
                  graveyard
Body:             body
Help:             help | help <topic>"""

CHESTS = f"""📖 Help – Chests
After a cleared stage a chest may appear \
({int(CHEST_CHANCE * 100)}% chance).
Choose before the next stage:
  inspect – INT check, once per player: reveals whether it's a Mimic
  open    – loot with better rarity than usual … or a Mimic
  skip    – leave it and move on \
(also happens after {int(ROUND_TIMEOUT_SECONDS)}s)

The deeper you go, the more chests are Mimics \
({int(MIMIC_BASE_CHANCE * 100)}% up to {int(MIMIC_MAX_CHANCE * 100)}%).
An unrevealed Mimic bites whoever opens it before the fight starts. Kill it
and you get its hoard."""


def spells_text() -> str:
    lines = ["📖 Help – Spells",
             "Cast with [cast <id> [target]]. Damage spells target an enemy "
             "number, healing spells a party member's name.",
             "[spells] shows which ones you know.", ""]
    for spell_id, spell in SPELLS.items():
        target = {"single": "one enemy", "all": "all enemies",
                  "ally": "one ally", "allies": "whole party"}[spell["target"]]
        if spell["req_affinity"] == 0:
            unlock = "known from the start"
        else:
            unlock = (f"unlock: {spell['affinity']} affinity "
                      f"{spell['req_affinity']} or INT "
                      f"{spell['req_intelligence']}")
        lines.append(f"  {spell_id} – {spell['name']}, {target}, "
                     f"{spell['mana']} mana, {unlock}")
    return "\n".join(lines)


EVENTS = f"""📖 Help – Events
Between stages ({int(EVENT_CHANCE * 100)}% chance, if no chest or remains \
turn up) you may run into
someone. Not everyone wants to kill you – some want worse.
  <<npc.reginald_first>> <<npc.reginald_last>> (stage {min_stage('hunter')}+) – a mad big game
      hunter. Lose and you end up in his lodge: mounted, a rug, an armchair.
  <<boutique.owner>> (stage {min_stage('couture')}+) – a futa couturière \
with
      enchanted scissors. Lose and you become this season's fashion.
      <<npc.starch_first>> <<npc.starch_last>> (stage {min_stage('recruiter')}+) – Brunhild's school recruiter. Lose and
      you may [accept] a maid's contract or [decline] it.
      Beat any of them for gold and their unique gear.
  The Null Master (stage {min_stage('null_master')}+) – no fight: three riddles, answer with
      [answer <word>]. A wrong answer turns the answerer into a silent drone
      (an NPC; buy back with [ransom <name>]). All three right: a reward.
  The Caravaneer (any stage, at most twice between two city stops) – a merchant with
      a wagon drawn by pony girls. He gives one unique legendary item for one lady
      (female, herm, shemale, male-herm or transgender) of your party. Every member votes with
      offer and a name, depart votes against; the majority decides. The
      chosen character is traded away, leaves the party and starts anew,
      and a copy with the same name joins his team. At most six ponies:
      the oldest is sent off. Examine shows which ponies were adventurers.
  The Drainer (stage {min_stage('drainer')}+, very rare, once per run) – a hollow-eyed
      figure with a belt of bottles. Either one member steps forward with
      sacrifice and a name (every member votes, majority decides) and is drained
      for good, or you fight him with challenge: very strong. A sacrifice loses
      the first part still left: chest, curves, manhood, balls (balls become
      silicone). The part goes into a bottle on his belt; examine shows whose.
      Win and one random bottle returns as an item: the party votes with give
      and a name who gets it (dice if tied). Drink it with consume to get the part
      back, or sell it. The bottle is named after the real values.
      If the party falls, he drains one member at random.
  <<boutique.shop>> – her boutique turns up as an event (even with
      empty racks – then she just wants fresh material), and whenever you
      pass the shop window of a fashion victim, the door opens too.
      [shop] lists the stock again, [sell <bag nr>] sells to her,
      [sellself] sells YOU – you get gold, fall, and she makes a fresh
      piece out of you on the spot. Pieces from heroes she beat in a
      fight are marked ★ – stronger (+1 stats, +20% armor, +2 damage,
      +2 allure) and 30% pricier.
      [buy <nr>] buys
      whatever she made of fallen heroes – boots, bras, ball bras,
      gloves, corsets,
      gowns, handbags … maybe even made from yourself. Very muscular
      heroes become tough leather (more armor), average ones velvet, soft
      ones sheer silk (more allure). Equine, canine or draconic heroes
      become stallion leather, wolfhide or wyrmhide, and well-endowed
      ones may end up as a tailored codpiece (+1 allure per 10 cm).
      Couture is
      strong: two stat bonuses, armor and allure, and the higher the level
      of whoever it was made from, the better (and pricier) it gets.
      All pieces made from the same hero form a set, e.g. 'Kai
      Collection': bonuses at 2, 3 and 4 pieces – and wearing your own
      collection gives an extra bonus on top.
      [depart] leaves.
  A full ogre – only shows up if he once ate someone in your party. He
      invites you to dinner: accept or decline, then charm (allure
      helps, gift), eat (leftovers of your friend – or yourself),
      talk (EXP), sleep (stay the night, full rest – and a small
      chance you leave with a little souvenir in your belly that is born
      after the curse revives you; every child gives +5 max HP), depart.
  <<npc.isolde_first>> <<npc.isolde_last>> (stage {min_stage('lich')}+) – very \
rare, very hard.
      Women become ice statues in her garden. Anyone with a cock becomes
      her consort and roams the deep halls as an enemy (stage \
{CONSORT_MIN_STAGE}+),
      sometimes at her side. Defeat a consort to free them (and get back
      the item the curse took). Beat the Queen for cursed unique gear.
  A young mage adept wants to practice a buff: [volunteer] and you get a
      random one – more strength, or something enormous (breasts, balls,
      butt or an endowment): less AGI, sometimes a lot of allure. It
      lasts until you fall. Sometimes the spell goes very wrong and you
      end up as a marble statue – enormously endowed, forever. The adept
      is very sorry. Sweat distracts him (+5% failure per sweat level),
      sweaty leather boots even more (+5%). [depart] moves on.
  A wanderer by a campfire: sit (heal, EXP), give (gold for a gift),
      or [give <bag nr|item>] / [give <slot>] to hand over an item –
      even what you are wearing. Every wanderer has their own taste; hit
      it and the gift in return gets much better. The item is gone.
      Some wanderers are thirsty: with a Large bust or bigger – or if
      you are very well hung – you can [milk] (gold and a bottle: milk
      for the busty, moonshine for the hung) or [nurse] (gold, party
      heals).
      Give gloves, boots, lingerie, clothes or crotch gear and the
      wanderer may want to thank you personally: accept or decline.
      sleep (share the bedroll – full rest, but check your purse in
      the morning), cook (grill raw meat in your bag), depart.
  <<npc.reginald_first>>'s huts – every hero he stuffed is on display in one of
      his huts. The deeper you are, the grander the hut: the Lodge
      near stage {HUT_STAGES['lodge']}, the Cabin near \
{HUT_STAGES['cabin']}, the Manor near {HUT_STAGES['manor']} \
(the death message tells you which).
      <<npc.reginald_short>> is out hunting – but he may come home:
      [enter] – go inside and see the trophies ([examine] for details)
      [search] – rifle through his things: gold, his gear or his
                 journal listing all lodges \
({round(HUT_SEARCH_RISK * 100)}% he catches you)
      [rest]  – heal {round(HUT_REST_HEAL * 100)}% HP in an 'armchair' \
({round(HUT_REST_RISK * 100)}% he walks in)
      [sleep] – full HP and mana ({round(HUT_SLEEP_RISK * 100)}% he \
finds you asleep and
                 gets a free shot before the fight), [depart].
      Lose to him and you join the collection.
  <<npc.hamhock_first>> the Pigman Butcher (stage {min_stage('butcher')}+) – \
fight him, or lose
      and end up as sausages. His shop sells meat made from fallen
      heroes: [buy <nr>], cook it at a wanderer's fire. [sellself] if
      you're desperate for gold. Meat quality depends on the hero:
      level, VIT and build (Toned/Curvy +1, Muscular/Chubby +2, Heavy
      +3, Thin -1) and sweat (+1 per sweat level) – Common, Prime
      (rare) or Marbled Choice (epic). Grilling raises it one grade.
      The more there is to cut, the more he makes: one piece per
      {MEAT_KG_PER_CUT} kg of body weight (up to {MEAT_MAX_CUTS}), each a different cut. Heroes with a
      penis also yield one extra sausage, worth more, and its kind
      follows the shape (Human, Equine, Canine, Draconic).
      Real body parts add prime cuts (worth 1.5x): breast fillets from a
      real bust of 150 cc, prairie oysters from balls, rump roast from a
      real butt of 105 cm. Implants are not edible: <<npc.hamhock_first>> cleans them and
      sells them as curiosities.
  Sweat: every combat round makes you sweat (hit/dodge/guard more than
      cast/use; muscular heroes (high STR, Toned/Muscular) and
      Chubby/Heavy ones faster): glistening → dripping → drenched.
      Tight or heavy gear adds up to +4 per round: lingerie and crotch
      pieces, armor 5+, leather/latex/steel/fur.
      Each level: +1 allure, +2% dodge (slippery), better meat – but
      monsters smell you: sweaty heroes get attacked more often.
      <<boutique.owner_short>> salt-cures garments from drenched victims (+1 armor).
      A full night's sleep (lodge, camp, ogre) washes it all off, an
      armchair rest halves it. Resets every run.
  Scent: orcs go for sweaty women/herms, amazons and the Lich Queen for
      sweaty heroes with a cock, gorgons for men – they target them twice
      as often and their fates (breeding, consort, statue) get likelier.
      Ogres roast, giants eat and slimes dissolve sweaty heroes more
      often. <<npc.reginald_short>> tracks the scent (+5% per sweat level in his
      lodges), <<npc.old_trotter_short>> grows fonder of sweaty workers. <<boutique.owner_short>> hits
      harder, goes for sweaty muscular heroes first, pays +15% per sweat
      level for [sellself] and turns drenched victims into 'Musk'
      pieces (+1 allure). A sweat-struck wanderer may offer [indulge] to the
      sweatiest hero – a tip, and the sweat is gone.
  <<npc.old_trotter_first>> the Pigman Farmer (stage {min_stage('farmer')}+) – \
lose and you're
      branded and put to work on his farm. Visiting <<npc.old_trotter_short>> Farm shows
      every hero working there; he sells milk, cream, eggs and bread.
      [work horse|cow|cumcow|hen|mule|carriage] hires you out for a shift of
      3–5 turns. Equine heroes earn 30% more as horse and may pull
      <<npc.old_trotter_short>>'s market carriage (best pay, riskiest).
      ([work] each turn, [quit] leaves with half pay). Things happen:
      tips, injuries, sweat, lunch breaks – and <<npc.old_trotter_short>>'s interest grows.
      If he decides to keep you, or you collapse, you stay as farm
      animal for good. Survive the shift and you get paid. Cows need a
      Large+ bust; big, muscular, hung heroes (balls 8 cm+) are hitched
      to the plough or carriage by the balls: more pay, pain every turn and
      a stamina count that ends the shift in a collapse; the cum cow needs a penis – the bigger the balls
      (and Equine), the bigger the batch, and sweat makes it stronger. Small heroes who are taken may end up in the hen coop.
      Your work stays on his shelf: a finished shift leaves a named
      batch (one per turn, half if you quit), and every hero kept on the
      farm supplies a better named product for good (milk, eggs, bread).
  Old <<npc.old_gorm_first>>'s jetty (stage {min_stage('fisher')}+) – a 3.1 m ogre fisher. [cast] rents a
      rod (30 gold, three casts each): fish, an old boot or a bite. [bait <name>]
      (press twice) hooks a hero as bait: 50% lost, 45% caught inside a giant
      fish (the rest eat Giant Catch), 5% survives with a buff. [lie] spends
      time with <<npc.old_gorm_first>>; he likes big, real bodies (180 cm+, wide hips, heavy
      balls) and scoffs at implants.
  <<npc.gul_first>>'s Grill (stage {min_stage('grill')}+) – a cart with a
      kebab spit: [buy <nr>] chicken and kebab, [special] (250 gold) carves
      today's special (stronger buff when a hero is on the spit), [ask] about
      the meat, [grumble] twice and you turn on the spit yourself.
  Public Privy (stage {min_stage('privy')}+) – a clean stone hut run by old
      Hedwig: [enter|examine|pass] first. Inside [stall] (5 gold, once each,
      a Relieved buff and an overheard scene), [wash] (free, clears sweat,
      Freshly washed), [read] the graffiti, [knock] on an occupied stall,
      [ask] Hedwig for gossip, [tip] her 10 gold for a secret. [urinal] (3 gold,
      only heroes with a penis) is the trough. [stint attend] (12 gold, once)
      works the counter. [stint fixture] pays 45 gold per shift, but after two
      shifts the wall may keep you for good: you become a fixture and stay
      there (no buyback). [grumble] twice has the same result. Later heroes
      see the names on the plates when they [examine]. [depart].
  Crone Creamery (stage {min_stage('dairy')}+) – a dairy run by <<npc.odile_first>> Marsh: [enter|examine|pass] first, inside [buy <nr>]
      milk, cream, cheese, butter, bull tonic, plus named products of past
      heroes. [stint milk|feed|cow|bull] runs a shift (cow: breasts needed,
      the farm ages you to 45+; bull: needs a penis; stamina decides). After
      three shifts a cow or bull may be culled. [tour] is <<npc.odile_first>>'s
      guided talk, [sellself] puts you on the books for good.
  <<npc.constance_first>> <<npc.constance_last>>, the paddle maid (stage {min_stage('buster_maid')}+) – a wandering
      head maid with The Butt Buster (legendary, 3000 damage) who wants a position. Needs a free party slot;
      a woman or futa [volunteer]s for 100 smacks, ten per [smack] press (the
      chat screams along; 1% death per smack:
      splattered, pancaked, launched, folded, bounced or flat-packed). Whoever
      survives gets Red cheeks, and Connie joins as a companion.
      Every volunteer is written into buster_ledger.json (shared by all
      players). [history] lets Connie recite the paddle's history: totals,
      best and worst seats, the latest victim and a handful of names. She
      remembers returning ladies and their best hit.
      Locations (huts, farms, shops, the taproom) turn up every
      {LOCATION_EVERY}th stage, and nobody knows which one comes next.
      [examine] looks at them from outside, [enter] steps in. Each shows
      only the heroes who were taken to that very place on that stage.
  <<npc.astrid_first>> <<npc.astrid_last>>, the Brew Master (from \
stage {min_stage('brewery')}) – her taproom.
      In front of the door: [examine], [enter] or [pass].
      Inside: [examine] shows the shop and the shopkeeper, [shop] the
      menu, [buy <nr>] her creamy yogurt drinks (heal and mana), [fresh]
      for a mug poured on the spot (random strength, {BREWERY_FRESH_LIMIT}
      per visit – she has to rest and refill), [sell <nr>] items
      from your bag, [depart] to leave. [sellself] and she
      pays well (+{round(BREWERY_SWEAT_PRICE * 100)}% per sweat level), \
then takes you into the
      backroom and comes back alone. You become a named drink on her
      menu, one batch, sold from the next run on. Quality follows level,
      VIT, build and sweat, like <<npc.hamhock_first>>'s meat. <<npc.astrid_first>> grows a little
      with every hero she takes, and she hangs one piece of the hero's
      gear (shoes first) in her shop – with a note on its size and smell.
      She pays the plain price plus that piece's shop price, so buying
      it back leaves you at the plain price.
      Careful: talk to her ([shop] or [talk]) {BREWERY_TALK_LIMIT} times without
      buying anything and she loses patience – she processes the talker
      for free.
      Her sign advertises the best hero drink in stock ('today's
      special'), and it is listed first in her shop.
      Heroes who are soaked in sweat get a
      personal offer from her.
  Special locations: every 10 stages (at stage 5, 15, 25 …) the party
      always walks into one of them – a butcher's, a hut or a farm.
  A very comfortable couch (stage {min_stage('couch')}+) – \
[inspect] it first.
      Half of them are mimics: sit down and you may simply be eaten.
  A town platform (stage {CITY_STOP_FIRST}, then every {CITY_STOP_EVERY} stages) –
      a random town with its stationmaster. [talk] (free, may fail),
      [pay] ({PASS_FEE} gold), [bribe] ({PASS_BRIBE_COST} gold, may fail)
      or [sleep] with the stationmaster open that town's rail line.
      In town: [ticket talk|pay|bribe|sleep] at the station does the same.
      [enter] takes the whole party to the town and pauses the run: back
      on the train, [resume] goes on with the next stage, [retire] ends
      the run for good. [depart] skips the town; the platform stage has
      no fight.
  A camp site (stage {min_stage('bivouac')}+) – [gather] firewood (once per
      member, small risk of injury) or buy a bundle in any shop, then
      [light] it (AGI and INT help). With the fire: [cook] raw meat,
      [talk] (party banter, bonds grow), and [rest] heals 60% and clears
      sleep. A cold rest heals only 20% and may be ambushed.
  The Sweatery (stage {min_stage('sweatery')}+, run by goblins or gnomes) – \
[examine], [enter] or [pass].
      Inside: [sweat run|lift|heat|grill|labour] starts a shift of
      {SWEATERY_CYCLES} cycles (the first cycle runs at once, then [work] \
for each further one,
      [quit] leaves with half pay). Everything you wear (weapon, armour,
      clothes) is really taken off into a locker and returned after the
      shift; only the boots stay on, and afterwards the operators wring
      them out into a jar of boot sweat on the shelf. Running gives +1 AGI, workout +1 STR, hard
      labour a little EXP. Muscular heroes and heroes who sweat a lot
      produce more litres. The heater pays well but burns HP, makes the
      heroes squeal and can roast them – a roasted hero is sold as meat
      on the Sweatery's menu. Goblins pay more and roast more often,
      gnomes extract more per litre and are safer. On the grill you are
      clamped between two iron grates over the fire: the most sweat, the
      most damage and the highest risk of being roasted.
      Every finished shift leaves bottles labelled with your name, the
      station and the volume, with your own smell and taste (it follows what you embody most:
      equine, canine or draconic genitals first, then real bust, balls,
      size, muscle, butt), on the
      shelf. [buy <nr>] heals or restores mana. [depart] only works when
      nobody is on a shift.
  The Northern Smokery (stage {min_stage('smokery')}+) – run by <<npc.jorveig_first>>, a stocky 2.9 m Nord, with a goblin
      accountant, a dwarf technician and an orc butcher. [examine], [enter]
      or [pass].
      Inside: [smoke] pays you danger pay up front (rises with the stage; survivors get
      a bonus of twice that on top) and puts you in
      a box for {SMOKERY_CYCLES} cycles (no fire: you are smoked by her foot sweat and aroma alone): the first runs at once, then [endure] for each
      further one. [beg] asks to be let out (about one in three works).
      Each cycle you survive with the same chance; over all cycles only
      about 1 in 10 heroes comes out alive (VIT helps a little). A
      survivor gets +2 VIT and a smoky trait. The others hang on the racks
      and are sold as foot-smoked meat ([buy <nr>], ready to eat, better
      than the butcher's). [depart] works when nobody is in a box.
  The sated ogre now invites any party – too full to fight."""

TOWN = """🏘️ Town
Between runs you are in Last Light. It is safe, you may stay as long as you like.
  town               – look around: what is happening, the buildings
  meet [name]        – talk to the locals (full character sheet)
  chat <name> [work|town|self] – small talk; regulars warm up to you over time
  talk <name> [work|town|self] – the same with ANY NPC who is around: locals,
                     maids, mercenaries, your companions, and whoever runs the
                     place you are standing in (<<npc.astrid_first>>, <<boutique.figure_first>>, <<npc.hamhock_first>>,
                     <<npc.old_trotter_first>>, <<npc.isolde_first>>); foes in a fight only taunt
  rumors             – listen to the talk of the town
  backpack [buy]     – extra bag slots at the pack-maker (price rises per slot)
  ransom [name]      – buy a Null Master drone (400 gold per level) or a café
                     stool (45 gold per level) back; [ransom <name> home]
                     keeps a stool as home furniture
  salvage            – buy the stool you just ruined as an NPC stool
  home stool|sit|free|yield – own men as permanent home seats
  cafe, hold, quit, sit <name>, rise – the Fat Ass Café (see [help cafe])
  order <tavern|cafe> <dish> – eat and drink in town
  consume <nr|name>  – use any consumable at any time, even in a fight (free)
  shop, smith, clinic, bank – the services you can visit\n  visit <name> – walk to a regular's or friend's house, then [house look|talk <name>|eat|sleep|rest|relax|bathe|sex <name>|back|leave]"""

def registry_help(key:str) -> str:
    from .town_buildings import registry
    return registry.get(key).help


def maidschool_text() -> str:
    from .town_buildings import registry
    return registry.get("maidschool").help.format(
        recruiter_stage=min_stage("recruiter"))


def tavern_text() -> str:
    from .town_buildings import registry
    return ("🍺 Tavern\nThe Gilded Tankard, owner <<npc.hilda_first>> <<npc.hilda_last>> (keeps 20% of your pay).\n"
            + registry.get("tavern").help
            + "\nOnly in town, not while you are in the dungeon.")

SHOP = f"""📖 Help – Shop
<<npc.velvet_first>> runs her shop at the dungeon entrance – open whenever you are not
on a run.
  shop              – <<npc.velvet_first>> greets you; shows what she sells
  shop examine      – look at the shop
  shop talk         – talk to <<npc.velvet_first>>
  shop armor        – armour, split into [ladies] and [gents]
  shop weapons      – weapons by class (whips, daggers, fists, ...)
  shop consumables  – potions and supplies
  buy <nr>          – buy an item from the list
  sell <bag nr>     – sell an item from your bag ({int(SELL_RATIO * 100)}% \
of its value)
After a visit the words armor, weapons and consumables work on their own.
Lady-only gear fits ladies, gents-only gear fits gents; everything else
fits everyone. Each shop sells only some categories.

Gold: every cleared stage pays each surviving member, boss stages double.
Chests and Mimic hoards hold extra gold. Potions are always in stock, the
shelves change after every run. What you sell, <<npc.velvet_first>> resells."""


BODY = """📖 Help – Body
Height, weight, build, bust, muscle, butt (and cock, girth, balls) are set
when the character is created. [body] shows them and their effects. After
that they only change at Dr. <<npc.vane_first>>'s clinic – for gold, and without a
fixed upper limit. Implants are cheap, magic is expensive and can fail.
  Height: tiny (<140 cm) and short dodge better but hit weaker,
          tall and huge (200 cm+) hit harder and have more HP
  Build:  Thin/Slim dodge better, Muscular/Toned hit harder,
          Chubby/Heavy have more HP and armor but dodge worse,
          Curvy gets a little more HP and a discount at <<npc.velvet_first>>'s
  Bust:   milk, allure and <<npc.velvet_first>>'s opinions
Your body also changes what monsters do with you: giants love small
trophies, cooks love heavy adventurers, breeders love curves – and
goblins, orcs, ogres, giants and amazons keep a large bust as livestock."""

ALLURE = f"""📖 Help – Allure
Some gear is less about protection and more about presentation: bikini
armor, latex catsuits, high heel boots, fishnets, gimp masks, collars,
kitty ears, cock sleeves … Each piece adds allure, and so do curves.
  Combat: thinking monsters may get distracted and miss you entirely
          ({int(ALLURE_DISTRACT * 100)}% per allure point, max \
{int(MAX_DISTRACT * 100)}%). Slimes, walls and doors don't care.
  <<npc.velvet_first>>: {int(ALLURE_DISCOUNT * 100)}% discount per allure point \
(max {int(MAX_DISCOUNT * 100)}% total)
  Fates:  breeders find alluring adventurers even harder to resist
Some pieces only fit certain bodies – the item says what it fits.
[profile] shows your total allure."""

REMAINS = """📖 Help – Remains
The dungeon remembers every death. After a cleared stage you may stumble
upon what is left of an earlier adventurer – a statue, a door with their
face, bones by a fire. Whatever the curse took from them lies there too.
  loot – take the item left at the remains (if any)
  pray – honor the fallen, the party heals a little
  pass – move on
  examine – a closer look: who it was, their level, who did it, earlier
             deaths, what is still lying there and who else fell nearby.
             Also works in the hunting huts, the farm, the butcher's,
             the boutique and the adept's statue garden.
If someone ended up as stew, the pot may still be there:
  taste – the party eats, heals 25% HP (unless it has gone off …)
  pack  – take a Jar of Adventurer Stew along (heals 70 HP, +10 mana)
If someone was kept as a dairy cow, [loot] also takes what is left in
the bucket: a Bottle of Fresh Milk (heals 50, +20 mana) or, if you are
lucky, a Jar of Thick Cream (heals 90, +30 mana).
Finding your own remains gets you your lost item back – and yes, you can
taste yourself.
[graveyard] shows the Wall of the Fallen."""


def biomes_text() -> str:
    lines = ["📖 Help – Biomes",
             f"Stages 1-{BIOME_SEGMENT} are always the Goblin Warrens. After "
             f"that the region changes every {BIOME_SEGMENT} stages – picked "
             f"at random, repeats allowed, deeper regions only once you are "
             f"deep enough. Every {BOSS_INTERVAL}th stage is a boss of the "
             f"current region. After {CYCLE_LENGTH} stages the cycle starts "
             f"again – much stronger.",
             f"From stage {STRAY_MIN_STAGE} on, strays from other regions "
             f"wander in ({int(STRAY_CHANCE * 100)}% per enemy) – even from "
             f"regions far deeper down, toned down to fit.", ""]
    for biome in BIOMES:
        names = sorted({ENEMIES[enemy]["name"] for enemy in biome["enemies"]})
        lines.append(f"  from {biome['min_stage']}: {biome['name']} – "
                     f"{', '.join(names)} | Boss: {biome['boss']['name']}")
    return "\n".join(lines)


def classes_text() -> str:
    singles = ", ".join(TITLES.values())
    combos = ", ".join(COMBO_TITLES.values())
    return CLASSES.format(singles=singles, combos=combos)


TOPICS = {
    "create": lambda: CREATE,
    "stats": lambda: STATS,
    "party": lambda: PARTY,
    "combat": lambda: COMBAT,
    "spells": spells_text,
    "items": lambda: ITEMS,
    "classes": classes_text,
    "chests": lambda: CHESTS,
    "events": lambda: EVENTS,
    "shop": lambda: SHOP,
    "clinic": lambda: registry_help("clinic"),
    "smith": lambda: registry_help("smith"),
    "town": lambda: TOWN,
    "bank": lambda: registry_help("bank"),
    "tavern": tavern_text,
    "brothel": lambda: registry_help("brothel"),
    "cafe": lambda: registry_help("cafe"),
    "maidschool": maidschool_text,
    "body": lambda: BODY,
    "allure": lambda: ALLURE,
    "remains": lambda: REMAINS,
    "biomes": biomes_text,
    "death": lambda: DEATH,
    "commands": lambda: COMMANDS,
}


def help_text(topic:str="") -> str:
    key = topic.strip().lower()
    if not key:
        return OVERVIEW
    if key in TOPICS:
        return TOPICS[key]()
    return f"Unknown help topic '{topic}'. Topics: {', '.join(TOPICS)}"

# The Caravaneer (event)

A travelling merchant with a wagon drawn by pony girls. Code: `events/caravaneer/`.

## Rules
- Spawn rule `caravaneer` (any stage, weight 3, `per_segment=2`: at most twice between two city stops).
- He appears only if the party has a candidate: alive, adult, gender Female, Herm, Shemale, Male-Herm or Transgender (`GENDERS` in `config.py`). A forced `!trigger caravaneer` shows him anyway.
- Every living member votes: `offer <name>` for a candidate, `depart` against any trade.
  NPC companions vote at once, never for themselves unless they are the only candidate.
- A strict majority decides at once. If everybody has voted without a majority, the top options are drawn by lot.
- After the idle safety net (PAUSED_IDLE_SECONDS, event is paused like other stops) ends it: no human voted -> he drives on; otherwise the votes cast count.
- The chosen character dies with the fate `caravaned` (the normal death flow: leaves the group, starts anew). A copy with the same name
  (NPC kind `pony`, handle `Name (pony)`) joins the team. A human member with room in the bag gets the ware: a unique legendary from `items.py` (items with `caravan: True`, never loot, never in a shop; weapons 80-100 damage, chest plate 60 armor, a bell with +10 to three stats). Without such items he falls back to rare/epic loot.
- The wagon starts with 2 random ponies and keeps at most `CAP` (6). The oldest leaves when a new one is harnessed.
- The ware (one unique legendary) is fixed when he appears and shown in the location tab (`web/run_panels.py: caravan_panel`) with one "Offer <name>" button per candidate, "No trade", the votes so far and who still has to vote. Votes can be changed until the decision.
- Examine lists the team and marks ponies that used to be adventurers.

## Files
- `config.py` constants (CAP, START, PER_SEGMENT, genders, random names)
- `npc.py` roster, random ponies, the copy of a player, trimming
- `event.py` offer, vote, resolve (`CaravaneerMixin`)
- `content.py`, `fates.py` texts; `spawn.py` the spawn rule
- `SpawnRule.per_segment` (in `spawn_rule.py`) is a general limit per stretch between two city stops; other events can use it.

## Debugging
`!trigger caravaneer` starts the event.

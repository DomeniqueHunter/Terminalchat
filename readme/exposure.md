# Undressed visitors: how NPCs react

Code: `exposure.py` (logic), `exposure_texts.py` (words and reaction texts). The reaction is shown in the greeting when a character enters a town building.

## What counts as exposed
Three body areas: `breasts`, `butt`, `groin`. What an equipped item covers:
- by slot: `chest` covers breasts, `crotch` covers groin and butt, `lingerie` covers groin (and breasts if the name has one of `BRA_WORDS`, e.g. "bustier", "corset"). Chest items whose name has one of `FULL_BODY_WORDS` ("dress", "gown", "robe", ...) cover everything.
- an item can say it exactly: `covers: ("breasts", "groin")` replaces the default.
- `reveals: ("breasts", "butt")` takes areas away again (open-bodice and backless dresses, nipple chains).
Level: nothing exposed = no reaction, all three exposed = `bare`, anything in between = `partial`.

## Decency: 0 (shameless) to 4 (strict)
- Every town has `decency` in its `town.py` (Last Light 4, Ironhold 3, Cogsworth 2, Mudgate 1, Dusk Hollow 0).
- Every building may set `decency = N` in its class and overrides the town. `-1` means no reaction at all (clinic).
  Tavern 2 (Cogsworth, Mudgate 1, Dusk Hollow 0), café 0, tuning room 1, arena 0, black market 0, bank and post office in Dusk Hollow 2, castle 2, brothel 0.
- The keeper's `personality` moves the value by one: words in `PRUDE_WORDS` +1, in `LOOSE_WORDS` -1 (clamped to 0-4).
- A building may also set `reaction = "name"` to use its own text pool (`brothel`, `cafe`) instead of the decency pool `d0`-`d4`.

## Texts
`REACTIONS[pool][level]` is a list of lines (at least three), placeholders `{name}` (the visitor) and `{keeper}` (first name of the building's resident). Add a pool, then give a building `reaction = "pool"`.

## Hook for effects
`exposure.on_exposed(player, level, parts, place, decency)` is called every time a reaction is chosen. It is empty on purpose: discounts, refused entry or favour can go there later without touching anything else.

## Not covered yet
Only the greeting reacts. Chat, `look`, dungeon events and private places (home, sweatery) do not.

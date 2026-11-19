# House furnishing

Every house has fixed rooms with typed slots (bed, seat, rug, shelf, table,
lamp, decor, bath, stove, plant) and a garden. Layouts live in
`furnishing/layout.py` (one `room(...)` line per room, grid position for
the floor plan). Furniture are normal items (`slot: "furniture"`,
`furniture: <kind>`, optional `comfort` and `storage`) in
`furnishing/items.py`; `catalogue: True` pieces can be ordered from the
carpenter, epic pieces only drop as loot.

- Only the owner places and removes furniture; lodgers and guests can view.
- Comfort (sum) gives a buff when sleeping at home (`COMFORT_TIERS`).
- Storage adds slots to the house chest.
- Houses without a `furniture` entry get a starter set on first use.
- Commands: `!home place <spot> <bag nr>`, `!home clear <spot>`,
  `!home carpenter <item id>`; the overlay opens with `!house open`.

## Interactive pieces

- `!home use <slot>` uses a piece you own; the overlay shows buttons for the selected spot. Only the owner uses the furniture.
- Bath (tubs): resets sweat and gives the buff "Freshly bathed" (allure).
- Bed: `!home use <slot> <name>` runs the normal intimate scene with a guest.
- Kinky category (slot kind `kinky`, in bedrooms, the tower and the manor playroom): Foot Smothering Box, Leather Bench, Spanking Horse (carpenter) and Facesitting Throne, Bondage Frame, Cage Bed (loot only).
- `!home use <slot> <name> [top|bottom]` runs the scene. `top` (default by roles) means you lead, `bottom` means you lie, kneel or are bound on the piece.
- Adults only. Hero guests must confirm first (`home accept`) and the command is then repeated. NPC guests need enough friendship and must like the act according to their kinks.
- Negotiation: dom with sub (or switch with the opposite) is settled by the roles. Two doms or two subs get a hint to choose `top` or `bottom`. An NPC who would have to take a role against their nature yields half the time, otherwise they refuse.
- Scenes live in `furnishing/scenes.py` (texts) and `house_kinky.py` (logic). A new piece needs an item with `"use": "<key>"` and an entry in `SCENES` and `ACTS`.
- After a kinky scene the host gets the buff "Playroom afterglow" (allure). No combat stats.

## Garden plants

- Garden spots (kind `plant`) can hold a plant next to the furniture: `!home plant <spot> <bag nr>` (seed items carry `"seed": "<plant key>"`), `!home water <spot>`, `!home harvest <spot>`, `!home uproot <spot>`. Only the owner. The overlay shows the same as buttons. A garden spot is labelled "Garden Bed (empty)" until planted, then with the plant name and stage (`rules.slot_label`). The `seat` spot next to the beds takes furniture only, no seeds.
- Stages: Seedling, Vine, Bud, Bloom, Overgrown (`need` 0/2/4/6/9). Harvest works from Bloom; an Overgrown plant gives `nectar_overgrown` (2-3) instead of 1-2.
- Special interaction "feed" (`!home feed <spot>`, overlay button "Feed the plant"): defined per plant in `PLANTS[key]["feed"]` (`min_endowment` cm, `min_balls`, `min_sweat_tier`, `store_from` stage, `store_cap`). Needs a gender in `HUNG_GENDERS`, enough endowment and balls (`player.body`) and sweat. Everyone in the house (owner, residents, guests) can do it, once per person per run. Effect: sweat to 0, the plant counts as watered, +1 extra growth per feeder (max 2) at the next run, from Bud on +1 stored nectar (paid out at harvest), afterglow buff for the feeder. Women just use `water`.
- Hold: a plant with `"hold": {stage: pulls}` (Seductress: Bloom 2, Overgrown 4) holds whoever feeds it. The state is `player.profile["vine_held"]`. While held, all `!home` commands except `pull` and `status` and starting a dungeon run are blocked (`town.held_text`); `!home pull` (overlay button "Pull free") counts down and frees the player. Texts `feed` and `pull` may be lists, one is picked at random (`furnishing/plants.py` `say`).
- The overlay shows a growth bar for a planted spot (`garden.progress_text`): stage, growth to the next stage, watered/thirsty, feeders, dry runs, hunger, stored nectar.
- Neglect: an Overgrown plant that is not fed in a run gets `hungry` +1. From `HUNGRY_AFTER` (2) the owner gets the buff "Drained" (-1 strength, -1 vitality) when sleeping at home (`rules.comfort_buff`). Feeding, harvesting or uprooting removes it from the person who did it. No binding, no scenes without consent.
- Irrigation: every garden has a `utility` spot. An Irrigation System there (carpenter, item flag `irrigates`) keeps unwatered plants from drying out and wilting. It gives no growth: plants only grow when watered or fed. Wilted plants still need water.
- Every plant lives in its own folder `plants/<key>/` (see `readme/plants.md`); the engine is `furnishing/garden.py` and `furnishing/rules.py`, engine settings and default texts are in `furnishing/plants.py`.
- Growth counts in dungeon runs: when a run ends, every watered plant of the party grows by one, an unwatered plant dries out and wilts after `WILT_AFTER` dry runs (water revives it).
- Seductress Vine: a bloom (or Overgrown plant) gives comfort and the buff "Scent of the Bloom" when you sleep at home. Harvest gives 1–2 Seductress Nectar (heals and restores mana) and sometimes a new seed, then the plant regrows from the vine stage.
- The seed comes from the vines of the Vine Swamp (see `readme/vine_swamp.md`).
- Plant state lives in the house record (`home["plants"]`).

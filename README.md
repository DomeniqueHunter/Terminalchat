# Cursed Descent

Endless descent into a cursed dungeon (1-4 heroes). When the party dies, the
curse revives everyone at the entrance.

## Start

    ./start.sh web        # web server (default), e.g. ./start.sh web --data game_data --debug
    ./start.sh console    # text console
    ./start.sh test       # pytest suite
    ./start.sh reset      # reset the dungeon data

Requires Python 3.10+ (tests: `pip install pytest`).

## Layout

    cursed_descent/
        start.sh                   the only entry point (web | console | test | reset)
        cursed_descent/            source package
            console.py, reset_dungeon.py   console client, world reset
            content/               shared static data (items, monsters, combat);
                                   merges the block data below (content/__init__)
            locations/<name>/      closed blocks: shop, smith, clinic, boutique,
                                   farm, brewery, butcher, lodge, couch, displays
            events/<name>/         closed blocks: ogre, wanderer, sweaty, lich, adept
            npcs/                  companions: generator (maids, mercenaries), autopilot, recruiting
                                   (game_data/accounts/accounts.db = accounts, serial keys, sessions and the character index; characters in accounts/<account_id>/<char_id>.json, NPCs in npcs/<npc_id>.json; the JSON `name` is authoritative, renaming it renames the NPC)
            monster/<group>/       enemy groups (content.py only): goblins, orcs, ...
            monster/biomes.py      biomes; monster/order.py keeps the enemy order
            spawn_rule.py          SpawnRule (kind, weight, min/max stage, interval)
            spawns.py              loads spawn.py of every block, eligible(stage)
            locations/venues.py    dispatcher for the venue blocks
            towns/<town>/<building>/   town buildings: a folder with BUILDING mounts it (readme/buildings.md)
            town_buildings/        building engine: base class, discovery, registry, shared kinds
            routines/              optional NPC day plans (routines.py in a building folder, readme/routines.md)
            events/handler.py      event state machine, mixes the event blocks
            commands.py            Command type (name + args), chat parser
            controller.py          execute(Command); handle(text) = parse + execute
            session.py             run state machine
            combat.py, dungeon.py, formulas.py, models.py, ...
        (game_data/                players, remains, shop, leaderboard – created at runtime, not versioned)
        tests/                     pytest suite, fixtures, golden transcript

### Block layout

Every block folder owns its logic, texts and fates; only the files it needs exist:

    location.py / event.py   the place or encounter itself (mixin or functions)
    npc.py                   named NPC behaviour (keeper, greeter, ...)
    events.py                random incidents inside a location
    content.py               texts and static data of the block
    fates.py                 fate texts, labels, remains texts (pure data)
    spawn.py                 RULES: when the block appears (weight, stages, interval)

`content.py` and `fates.py` contain no imports. `content/__init__.py` merges
the per-block parts back into the global `FATES`, `FATE_LABELS`,
`REMAINS_TEXTS`, `VENUE_TEXTS`, `EVENT_TEXTS` (original key order kept).
`tests/test_layout.py` enforces the structure.

Optional block files: `config.py` (pure data: `NPCS` with the complete initial
record of every NPC of the block, plus `SCOPE`/`DEFAULTS`/`NPC_TOKENS` for
name tokens) and `items.py` (`ITEMS`, optional `ITEM_SETS`; merged generically
by `content/__init__.py`). Towns do not have these two files themselves: their
NPCs and gear live in the building folders (`towns/<town>/<building>/npcs.py`,
`items.py`), see [readme/buildings.md](readme/buildings.md).

## Town buildings

A town building is a folder `towns/<town>/<building>/` with a `BUILDING` object;
the folder alone mounts it, there are no lists. Shared kinds (tavern, bank, ...)
keep engine and base class in `town_buildings/<kind>/` and are derived per town.
How to build one: [readme/buildings.md](readme/buildings.md).

House furnishing (rooms, slots, furniture, floor-plan overlay): [readme/furnishing.md](readme/furnishing.md).

Vine Swamp, Pheromone Bloom and Pod Garden: [readme/vine_swamp.md](readme/vine_swamp.md).

## NPC daily routines

NPCs stay in their building unless a `routines.py` in a building folder gives them a fixed
day plan or a random wander. How to write one: [readme/routines.md](readme/routines.md).
Player held by an NPC (slave, leash): [readme/control.md](readme/control.md).

## Texts and actions

Output texts name actions in brackets (`[hit]`, `[buy <nr>]`); they are
buttons in the web UI. The input field still accepts the same actions with a
leading `!` (`!hit`, `!buy 2`). No text mentions chat, DMs or channels.

## Server (Docker, local, plain http)

    ./console.sh start     build and start (http://127.0.0.1:6969)
    ./console.sh start --public    same, but listen on 0.0.0.0 (LAN/internet, plain http)
    ./console.sh debug     same with the test tools (CURSED_DEBUG=1)
    ./console.sh stop | restart | status | logs | build
    ./console.sh admin serial [count]          create single-use serial keys
    ./console.sh admin serials | accounts      list keys / accounts
    ./console.sh admin password <name>         set a new password
    ./console.sh admin refresh <name> | --npcs | --all
                                               reload characters from disk in the running server
    ./console.sh admin admin <name> [--seconds N | --revoke]
    ./console.sh backup                        write backups/cursed_descent_backup_<date>.tar.gz
    ./console.sh backups | restore <file>      list backups / restore one (stops the server)
                                               temporary admin (ends on server restart)

Registration needs a serial key, an account name and a password (min. 8
characters); every account may have 2 characters (MAX_CHARS_PER_ACCOUNT).
The world clock runs on its own: 1 day = 1 real hour (WORLD_DAY_SECONDS).
The calendar counts day 1-365 per year (YEAR_DAYS) with weekdays (WEEKDAYS, a week = 7 real hours). Stored `world.json` stays unchanged: day 0 = Monday, day 1 of year 1. Seasons are planned for later.
A character that falls (café stool, Null Master drone, school recruit) loses a
quarter of its gold, keeps the rest and is back after one world day.

`docker-compose.yml` mounts `./game_data` as `/data`, so the data stays
outside the container. The container runs with your user id. The port is
bound to 127.0.0.1; `./console.sh start --public` (also for `debug` and `restart`) or `CURSED_BIND=0.0.0.0` makes it reachable from the network. The connection is plain http, so put a TLS proxy in front of it for the internet.
The server code lives in `cursed_descent/web/` (FastAPI + Jinja2 + htmx
with the ws extension, vendored in `web/static/`). One shared session for
everybody who opens the page; each browser picks the character it acts as.
Without Docker: `python3 -m cursed_descent.web --data game_data`.

Web UI structure: a component describes its page as data
(`cursed_descent/view.py`: `Panel`, `Button`); `Building.ui` (e.g.
`town_buildings/bank/ui.py`) returns it, counter buildings get theirs from
their offers (`counter_ui`). `web/views.py` collects the panels, `web/hub.py`
holds the controller, the clients and the tick loop, the templates in
`web/templates/` render the panels.

## Tests

`tests/test_golden.py` replays a seeded 1500-step scenario (all four fixture
heroes, combat, chests, events, deaths) and compares it to
`tests/golden/scenario.json`. Any change in game behaviour fails this test.
After an intended behaviour change regenerate the file:

    python3 -c "import json; from tests.scenario import *; \
    open('tests/golden/scenario.json','w').write(json.dumps(\
    fingerprint(run_scenario()), indent=1))"

## Characters, body, gear, needs

- Every character has `first_name`/`last_name` and a stable `id` (kept on
  death, revival and recreation); `name` stays the unique chat handle.
- Body values are numeric (cm/ml/kg), set at creation (`body_creation.py`)
  and afterwards only changeable via the clinic (`!clinic`, `!mod`).
  Implants are cheap (tracked in `fake`), magic costs more and can fail.
  Growth beyond the old limits is permanent (diminishing returns).
- Items are `Item(str)` objects carrying smell/sweat (`smell.py`); worn gear
  keeps the scent when taken off or given away (`!give`).
- Needs (`needs.py`, `needs_runtime.py`): hunger, thirst, sleep, arousal
  (0-100, higher is worse). They tick once per cleared stage, apply stat
  penalties, starvation costs HP. Satisfy via `!consume`, `!use`, resting
  and relief events; `!needs` shows them. Rates and effects live in `config.py`.
- Companions: `!hire <name>` in a lobby recruits one of your own characters
  (free, by handle or ID), one of your recruited maids (free) or a mercenary
  from `game_data/merc` (40 gold x level; there is no mercenary hub yet, so
  the folder starts empty). Maids are generated on demand in the Maid School
  (Look for maids; every further maid costs a fee, five at most; recruiting
  pays double price and writes the file to `game_data/maids`). Nothing is
  preset. Companions act on autopilot (`npcs/autopilot.py`); `!dismiss <name>`;
  `!auto <name> [on|off]` switches the autopilot.
- Visiting NPCs: location NPCs (Astrid, Jorveig, Vesper, Reginald, ... and the
  adept Pip Primrose) visit towns at random (`npcs/visiting.py`, config
  `VISIT_*`). While one is in a town its dungeon spawns are blocked
  (`spawns.AWAY_KINDS`), and a location that is active in a run keeps its
  keeper at home. Visitors appear in `!meet`/`!chat` and as guests on café
  seats and as clients in the brothel (`Regulars.visiting`). To make a new
  location NPC visit: add a `VisitProfile` to `VISITS` in the package's
  `npc.py` (kinds = spawn kinds it is absent from, likes = café/brothel
  weights, stance, quirks) and list the module in `SOURCES` of
  `npcs/visiting.py`.
- Names: all NPC names live in the NPC records of the `npcs.py` files of the building folders (blocks: `config.py`) and
  are loaded through `settings.py` (`PROTOTYPES`). Texts use tokens such as
  `<<npc.KEY_first>>`, filled from the NPC json at runtime (`bind_npcs`), so
  renaming an NPC in `story_npcs/<name>.json` changes the name everywhere. The
  file name stays fixed (the prototype name, e.g. `madame_vesper.json`);
  a missing file is created from the prototype at startup.
- NPC gear: every NPC wears items from the `items.py` of its block
  (`equipment` in the record: `{"slot": {"id", "by"}}`, `by` = creator). Unique
  pieces are epic, never sold and never looted (`shops=()`, `no_loot`), have
  detailed descriptions and gent/lady restrictions. Existing NPC files get
  missing gear once per version (`GEAR_VERSION` in `npcs/seed.py`, profile
  `gear`), occupied slots are never overwritten. Gear stats do not count in fights.
- Trophies: defeated NPC enemies (enemy field `npc`) drop with 25% a replica
  (`<item>_replica`, rare, stats x0.8) of one unique piece the NPC wears
  (`npc_trophies.py`); `!examine` of such an enemy shows what it wears.
- Shops: each shelf category holds 10 pieces; when the player sells more, the
  oldest piece is donated (deleted).
- Bars: heat (red) and air (blue) are real progress bars with a hover tooltip
  showing the exact value. Air in
  a house smother scene drains per pulse by the sitter's weight
  (`HOUSE_AIR_DRAIN` at `HOUSE_AIR_REF_KG`, factor `HOUSE_AIR_FACTOR`).
- Home scenes: every act is an overlay (`sex_overlays.py`: `KIND_OF`, `SIDES`,
  `DEFAULT_GIVER`) that continues each pulse until changed; each kind has its
  own action buttons (giver and receiver side). Texts: `sex_overlay_texts.py`
  (act key, kind key, then generic `("any", action)`). Clench can crush: a roll
  per click at full squeeze, a whimper warning first; at home it ends in a long
  knock-out, in the cafe it is deadly. Foot smothering is kind `sole`
  (`sex_sole.py`): own buttons (Rub, Pinch nose, Toes in mouth, Command: Lick),
  a foot sweat bar with smell tiers, half the air drain, no crush. NPC guests
  and residents use the same scenes (they act by autopilot); only regulars
  stay single-shot.
- Items: `?` buttons in bag and equipment (`!item <nr|slot|name>`) show price,
  set, smell and sweat traces.
- Web: combat hotkeys `h` hit, `c` cast, `t` cycle targets, `e` enter, `f` force round; `--debug` enables test tools.

## Layout

    npcs/  towns/  town_buildings/

`towns/<town>/` holds `town.py`, `content.py` (blurb, happenings, rumors) and one
folder per building; `town_buildings/` holds the engine: base class, discovery,
registry and the code of the shared kinds.

## House visits

`visit <name>` walks to a regular's or friend's house (event addresses work
too). Who is there is random (`house_visit.py`): the host, a spouse, a local
visitor, other players. At the house the `Home` tab offers examine, talk,
eat/sleep/rest/relax/bathe, a seat session (cafe ladies) and `Sex with`,
which opens the `Sex` tab. A dominant host decides the act when the player
is sub; a sub host only voices a wish when the player is dom.
- Brothel clients: gender weights in `REGULAR_GENDER_WEIGHTS["brothel"]` (config.py); with `BROTHEL_HOUSE_GUEST_CHANCE` a resident of the town (madames, staff of the houses in `HOUSE_GUEST_BUILDINGS`, the brothel's own madame, not its staff) drops in as a one-shot client (`brothel/clients.py: house_guest`).
- Brothel finishers (`brothel/finish.py`): `[serve swallow]` takes the whole purse of a client (anal vore), `[serve wipe]` wipes a client's memory (foot, better pay); a dominant client can finish the player off in sub mode.
- Town stop: `[enter]` pauses the run (state `paused`, party in town); `[resume]` continues with the next stage, `[retire]` ends it. All venue locations share the 4-stage location slot; wedding once per run.
- Debug: `!goddess [stage]` builds/resets the test character Claudia (level 100, stats sized for the given stage, default 100).

## Café package
- Engulfed: no item, the lady is just full. Only a collapse turns a victim into a stool (personal look, no hood).
- World days: tavern rooms, home sleep and run ends pass a day; the dead return after 2 days; `endrun` waits out one day.
- Stools: NPCs may buy them (message says who and where), `ransom <name> [home]`, `salvage`, `home stool|sit|free|yield`.

## Güls Grill
- Dungeon location (stage 5+, location slot): `buy <nr>`, `special`, `ask`, `grumble`. A second grumble puts the guest on the spit (fate spit_roasted); fallen heroes of earlier runs turn on the spit and can be eaten as the special.

## Butt Buster Maid
- Event (stage 4+): Constance "Connie" Whackshire wants a position. A woman or futa volunteers for 100 smacks (1% death per smack, six paddle fates); survivors get Red cheeks and Connie joins as a companion with her 2.5 m paddle.

### Crone Creamery (locations/dairy)
A dairy in the location slot (stage 7+). Odile Marsh keeps the ledger, her mother Marguerite is the lead cow. Buy dairy goods and named products of fallen heroes, work a shift with `stint milk|feed|cow|bull`, take the `tour`, or `sellself`. Cow shifts need a full bust (a young heroine is aged to 45+), bull shifts need a penis. Collapsing as a cow or bull, or being culled after three shifts, ends the run for that hero; the victim stays on the shelf as a named product.

## Watching others

Characters in the same location see each other's actions and bad ends as observer lines ("You see Nick ..."). Toggle with `!ambient witness` (button "Watching others"). The brothel and private rooms, runs and home visits are exempt. Currently implemented for the café.

## Running as non-root

The container always runs as 1000:1000 (override with `CURSED_UID`/`CURSED_GID`). `game_data` must belong to that user: `sudo chown -R 1000:1000 game_data`.

## Town navigation and paid revival

Inside a building the menu shows only that building and "← Town"; the town overview appears only in town. All buildings are enterable. A dead character can skip the wait with `!endrun pay` for `REVIVE_PRICE` gold (500, config.py).

## Family requests

`!family <name> <role>` (or the Family tab form) only sends a request; the other character confirms with `!family accept <name>` or `!family decline <name>` (buttons in their Family tab). NPC targets are linked directly.

## Short forms, world upkeep, admin

- Short forms: `!h` hit, `!c` cast, `!f` force, `!d` dodge, `!g` guard, `!p` potion, `!e` enter, `!i` inv, `!s` status; web keys h c f d g p e press the matching button (not while typing).
- World upkeep: every real world day (1 h) logged-in characters outside runs get hungrier (`WORLD_NEED_STAGES`) and regenerate (`WORLD_HP_REGEN`, `WORLD_MANA_REGEN`); offline characters are left alone.
- Admin accounts may use the debug commands (`!events`, `!stage`, `!trigger`, `!teleport`, ...) without debug mode.
- Admin teleport: at the station admins (or debug mode) get a section with one button per town (`!teleport <town>`).

## Lobbies and friends

- Up to `MAX_LOBBIES` (10) lobbies/runs run in parallel; `lobbies.py` holds one Session + ReadyCheck per lobby. The first lobby uses the original session; the controller resolves `controller.session` for the acting character (focus) or the ticking lobby.
- Bank and house chest: the building panel only shows `Gold: x 💰` and `Items: y/N 🎒` plus an [Inventory] button (`!stash bank` / `!stash home`). That opens a big window, your bag on the left, the vault or chest on the right; click an item to move it over, gold in steps of 100 / 1000 / all. The bank belongs to one character in every town (account by character id), the house chest to every resident of the house, only in that town and only at home. Code: `web/stash.py`, the window is rendered inside the `lobby-overlay` container of `web/templates/panels.html`, so it also works on a page that was loaded before the update.
- Party menu (top left): outside a lobby only [Create Lobby], [Find Lobby], [Start] (`!solo`: opens a lobby and descends alone); in a lobby or run [Leave], [Retire], [Resume] (the leader of a still-open lobby also gets [Start]); dead players (waiting for the respawn) only get [End run] and [Resume now 500], with a red note showing that they are dead and when they come back.
- `!lobby` opens a lobby, `!lobbies` lists open ones in the log; the button "Find lobby" opens an overlay with all open lobbies (Join / Leave / Start / Kick, live, Esc or click outside closes), `!join <leader|L2>` joins, `!lobby invite <name>` invites (invitee presses Join or Decline), `!kick <name>` (leader), the next member leads when the leader leaves.
- Lobby members who are offline are marked "(offline)" and leave the lobby after `LOBBY_OFFLINE_SECONDS` (300).
- Friends: `!friend <name>` asks, the other confirms with `!friend accept|decline <name>`, `!friend remove <name>`. The Address book tab lists friends with online status, Invite (when you lead a lobby) and Remove.

`!w` Tab completion (web): after `!w ` press Tab to complete names of online friends and characters in the same place; Tab again cycles; the name is followed by `: `.

Private-moment asks (`!intimate`): the asked player sees a Request box with Accept (`!consent`) and Decline (`!refuse`) at the top of the Party tab, and a ● badge on the Party tab; the asker sees a waiting line.

### Witness texts in more places
Besides the café, others in the same building now see short "You see {actor} ..." lines (toggle: `!ambient witness`, result only, no text when the action fails): tavern room, smith purchase, clinic modification, arena bet (win/loss), arrival by train at the station, finished mine guild shift. Table and texts: `town_buildings/observers.py`; the hook sits in `GameController.execute`. Private places, runs and home stay exempt.
More scenes (same table): blood bank, lab, bank (deposit/withdraw), black market, workshop, rune forge (purchase and finished carving), salon, castle (audience/banquet with invitation), brewhouse (finished brewing shift). All texts with place and NPC: `__additional/witness_texts.csv`. Maid school stays without scenes (the actor is gone after enrolling).

### Tabs
Top row: Character, Party, Location (plus Home/Sex when active). Under Character a second row: Sheet, Inventory, Family, Address book, Settings. The Character button returns to the last used sub tab.

### Kick and ban (console)
`./console.sh admin kick <account>` drops the connections and ends the sessions of an account (it may log in again right away). `./console.sh admin ban <account> <30m|2h|7d|perm> [reason]` bans it (login refused with the end time and reason, stored in the account database), `unban <account>` lifts it, `bans` lists the active ones. Admin accounts cannot be kicked or banned. Old account databases get their new columns automatically at startup.

### Biomes per town
A run's biomes follow the town the lobby gathered in (`TOWN_BIOMES` in `config.py`): the first segment uses the town's start biome, later segments draw from all biomes available for the stage, with the town's three favorites weighted x3 (`BIOME_FAVOR_WEIGHT`). Runs without a known town keep the old rules. Running runs keep what they have.

### The Tuning Room (Last Light)
Orientation training with five human coaches (`towns/last_light_humans/tuning_room/`): Madame Seraphine Delacroix (straight), Ilaria Moonwhisper (bi), Coach Taren Blackwood (fag training for men), Mother Ysolde Marrow (lesbian training for women), Camille Moreau "One-Way Ticket" (homo training for Shemale/Transgender/Cunt-boy, an alternative for men). Herm and Male-Herm only get bi training. Price `TUNING_PRICE` (300 gold), one training per game day, sets `profile["orientation"]`. `!tuning_room <first name>` or the buttons in the Location tab; the chat command `!prefs orientation` still works. NPC sheets: `towns/last_light_humans/tuning_room/npcs.py`, texts: `towns/last_light_humans/tuning_room/content.py` (overview in `__additional/tuning_room_texts.csv`), observer line in `observers.py`.

### Backup
`./console.sh backup` streams the whole data directory out of the running container into `./backups/cursed_descent_backup_YYYY-MM-DD_HHMMSS.tar.gz` (SQLite files are copied with the SQLite backup API, so they are consistent while the server runs). The newest 14 are kept (`CURSED_BACKUP_KEEP`, folder `CURSED_BACKUPS`). `./console.sh restore <file>` first backs up the current state, stops the server, replaces the data directory with the archive and starts the server again.

### Biome ribbon
The Location tab shows a narrow ribbon during a run: biome icon and name, the stage range of the current biome segment, a boss mark on boss stages and the biome intro text. Colours and icons live in `web/ribbon.py` (`LOOKS`).

### Post office and mail
Every town has a post office (`post_office`) with its own clerk: Hedda Fenwick (Last Light), Skitter Quillwick (Mudgate), Thorgrim Sealwright (Ironhold), Wimble Gearwright (Cogsworth), Mortimer Ashquill (Dusk Hollow). Letters can be written, read and answered anywhere (also from home) with `!mail` or the Mail sub-tab of the Character tab; parcels (gold and one item) are collected only in a post office (`!mail collect <id>`). Everything is stored in `mail.json` (mailboxes per character id), so the backup covers it.
- `!mail`, `!mail read <id>`, `!mail send <name> | <subject> | <text> [| gold [| item]]`, `!mail reply <id> | <text> [| gold [| item]]`, `!mail delete <id>`, `!mail sent`, `!mail block|unblock <name>`.
- The sender pays `MAIL_FEE` plus `MAIL_GOLD_FEE_PERCENT` of the attached gold; gold and item leave the bag at once and wait in the letter. Letters with a parcel cannot be deleted.
- The recipient list of the letter form shows only people you know (friends, family, earlier correspondents, NPCs you have chatted with); a typed name is looked up as handle, NPC first name or full name (`mail.find_target`).
- Parcels not collected after `MAIL_ATTACH_DAYS` world days go back to the sender (a "Returned" letter); plain letters older than `MAIL_KEEP_DAYS` are removed. `MAIL_BOX_SIZE`, `MAIL_PER_HOUR`, `MAIL_SUBJECT_MAX`, `MAIL_BODY_MAX` limit the traffic (all in `config.py`).
- Letters to NPCs are answered after `MAIL_NPC_REPLY_SECONDS` with a line from their topics; gold and an item are accepted (NPCs keep no mailbox).
- Reset: none. Old NPC files get the clerks' gear through the gear sync (`GEAR_VERSION` 3).
- [Admin and debug commands](readme/admin.md)
- [The Caravaneer event](readme/caravaneer.md)
- [The Drainer event](readme/drainer.md)
- [Rook & Thread, the tailor](readme/tailor.md)
- [Contract of Keeping, bondage and bindings](readme/kept.md)
- [Brandholm, the Nord town](readme/brandholm.md)
- [Reactions to undressed visitors](readme/exposure.md)

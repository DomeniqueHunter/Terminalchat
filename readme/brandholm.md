# Brandholm (Nord town)

A matriarchal town of giant Nords, ruled by Matriarch Sigrunn Brandsdottir (67, 3.3 m, mother of Jorveig from the Northern Smokery). All "women" there are futas; the men are smaller, serve and carry. Boots off at every door.

## What exists now
- Folder `towns/brandholm_nords/`: `town.py` (key `brandholm`, decency 1, line to Cogsworth), `content.py` (blurb, happenings, rumors).
- Race `races/nord.py`: 200-340 cm, 120-380 kg, member 34/26/11 as the base.
- Buildings: `station` (Hallgate Platform, Gudrun), `tavern` (The Longhall, Brynhild and Orm), `hall` (Council Hall, Sigrunn), `shop` (Shoe House, Solveig), `bank` (Hall Vault, Hallvard), `post_office` (Snow Post, Leif), `smith` (Hall Forge, Thyra), `brothel` (Warmhouse, Freydis, Helga, Bjarni), `clinic` (Healing Hearth, Eira), `ember_cask` (The Ember Cask, brewhouse with drinks, Hjordis and Gunnar), `steam_hall` (Ragnhild, Ketil), `sole_hall` (Ingibjorg, Torben), `smoke_hall` (Svanhild, Odd), `snow_ring` (Ulfhild, Sven), `cream_room` (Gudlaug, Eyvind), `carrying_house` (Hallgerd, Eyjolf), `feast_hall` (Gunhild, Thorgrim). 28 residents in total.
- Cogsworth is the hub: its `lines` now list `brandholm`.

## Planned (nothing built yet)
Nothing from the plan is missing any more; changes come from testing. Details are in the brainstorm: feast with wheel (feet 30 % survival, balls 2 %, spit, mercy), futas look at men suggestively, drinks (smoke ale, mead, ice bock, trampled wine, sweat stout, cream and gold), blessing of the Matriarch (overfilled man: pregnancy chance, 24 h at her feet, pays her at the end).

## Add a building
Create a folder `towns/brandholm_nords/<name>/` with `__init__.py` (`BUILDING = ...`), optionally `npcs.py` (`NPCS = {...}` seeded once). See [buildings](buildings.md).

## Reset
Nothing. All NPCs are seeded from the `npcs.py` files the first time the new town is loaded.

## The Ember Cask (drinks)

Folder `towns/brandholm_nords/ember_cask/`. A counter building: work the casks (job), or buy a drink; each drink heals a share of max HP and gives a buff (until death). All drinks are one table, `DRINKS` in `content.py`: `id: (label, price, heal share, buff, tier, pregnancy chance, text)`. Add a drink by adding one line (and a buff to `BREW_BUFFS` if it has one).

Tiers: `common` always available; `hall` limited to 3 per player per day (`HALL_LIMIT`); `feast` only visible while the profile flag `brandholm_feast` is set (the feast building will set it). Matriarch's Cream has a 3 % pregnancy chance (sign on the tap), Herrin's Cream 6 %, both scaled by the drinker's fertility. Herrin's Cream gives the buff "Blessed of the Hall".

## Steam Hall, Sole Hall, Smokehouse, Snow Ring

All four are counter buildings with a job (4 rounds, 25 % cut, except the Sole Hall which has the contract). Everything is plain data at the top of each `content.py`.

- **Steam Hall:** `CHAMBERS` = `id: (label, price, death risk, heal share, buff, text)`. Mask in the young / hall chamber; the Herrin chamber appears only while `brandholm_feast` is set. Death risk 3 % / 12 % / 30 %, fate `sweated`. "Sit in a chamber yourself" pays 40 gold for 25 % HP.
- **Sole Hall:** 24 h real-time contract (like Kept): up to 6 serves for 25-45 gold, +300 gold and the buff "Sole-worshipper" at the end, buy-out 150 gold, blocks lobby/join/start/force meanwhile. Stored in `profile["sole"]`. Foot bath: 35 gold, full heal.
- **Smokehouse:** short smoke (10 % risk, 60 gold) or the full box: the wheel picks feet (70 % death) or balls (98 % death), cured pays 400 gold and the buff "Cured". Fate `hall_smoked`.
- **Snow Ring:** bet 50 gold (45 % to win double) or fight for 20 gold (win chance 30 % + 3 % per strength, max 80 %, win 80 gold, loss costs 30 % HP).

Deaths use `towns/brandholm_nords/death.py` (`fall`), the fate texts are in `fates.py`, the buffs in `buffs.py`. Dead players respawn like everywhere else.

## Cream Room, Carrying House, Feast Hall, gaze, shoes

- **Cream Room:** "Take a fill" (30 gold) raises the fill level (max 4, loses 1 per day). At level 3 the offer "Ask the Matriarch's blessing" appears (flag `brandholm_full`): 24 h real-time contract at Sigrunn's feet (blocks lobby/join/start/force), 35 % x fertility pregnancy chance, at the end the man pays 200 gold (as much as he has) and gets "Blessed of the Hall". Stored in `profile["fill"]` and `profile["blessing"]`. The building `lock` hook settles the contract on the next command.
- **Carrying House:** ride in a basket (20 gold, heal 40 %) or be carried for hire (+35 gold, costs 10 % HP).
- **Feast Hall:** "Join the feast" (60 gold, full heal, buff) sets `brandholm_feast` for the current world day; the Herrin's casks (Ember Cask, Steam Hall) and the wheel are open until the day changes (cleared by the hall's `lock` hook). Wheel: spit (60 %, 35 % death, fate `roasted`, 300 gold if survived) or mercy (40 %, 100 gold).
- **Gaze:** `Town.gaze` (new, optional tuple of lines). In a town that has it, male players get one of these lines after every building greeting. Brandholm's are in `towns/brandholm_nords/content.py` (`GAZE`).
- **Shoe House:** four new boots (`shops: ("velvet",)`) in `shop/items.py`: guest fur boots, hall slippers, snow-walkers and the giantess's hand-me-downs.

## Council Hall
Sigrunn's hall is a counter: audience (free, reacts to your flags), Town Book (rules and building hints), petition (300 gold, buff "Matriarch's favour" until death, once).

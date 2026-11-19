# Town buildings – how to build your own

A town building is a **folder**. Drop it into a town and the town has it:

    cursed_descent/towns/<town>/<building>/

There is no list to edit. The town overview, the buttons in the web UI, the command, the help and the greeting all appear because the folder
exists. Delete the folder and the building is gone.

## The minimal building

One file, one class, one line:

    towns/mudgate_goblins/smokehouse/__init__.py

    from ....town_buildings import Building


    class Smokehouse(Building):
        key = "smokehouse"
        title = "Smokehouse"
        blurb = "Hams hang from every beam. Everything smells wonderful."
        greeting = "Welcome in, welcome in. Mind your head on the sausages."


    BUILDING = Smokehouse()

Requirements:

| Rule | Why |
|------|-----|
| the folder has an `__init__.py` | that is what makes it a building |
| `__init__.py` defines `BUILDING`, an instance of a `Building` subclass | discovery reads exactly this name |
| `key` equals the folder name | one name everywhere (command, address, saved data) |
| `title` and `blurb` | the entry in the town overview |

That is all. `!smokehouse` now walks the player in, shows `greeting` and the
town overview lists `Smokehouse – Hams hang ...`. Folders whose name starts
with `_` are ignored (use them for scratch work).

The town of a building is the folder it lives in. The same key may exist in
several towns (see "Shared kinds"); the command name is the key in every town.

## What a building can add

Everything else is optional. Set the attribute in the class, put the code in
a file next to it (the usual names are below, nothing is enforced).

| Attribute | Meaning |
|-----------|---------|
| `order` | position in the town overview (default 100; lower first) |
| `icon` | emoji for greetings and buttons |
| `greeting` | text shown when the player enters |
| `help` | text of the help topic |
| `commands` | `{"name": handler}`; `handler(services, player, args) -> list[Message]` |
| `place_commands` | commands that put the player inside this building |
| `ui` | `ui(services, player) -> Panel` – the web panel (see `view.py`) |
| `counter` | a `Special` with `Offer`s: a ready-made shop-like counter (see below) |
| `jobs`, `session_lines`, `job_words`, `owner`, `place`, `closed`, `cut` | shift work for the building (see `town_buildings/work/`) |
| `menu`, `menu_title`, `dish_kg` | food and drink offered |
| `items` | `items() -> dict`, extra items created by the building |
| `decency`, `reaction` | how strictly the keeper reacts to undressed visitors (0 shameless - 4 strict, -1 none; overrides the town) and an optional text pool, see [exposure](exposure.md) |
| `setup`, `save` (ledgers: created in `setup`, written in `save`), `idle_hook`, `round_hook`, `finish_hook`, `greeter`, `lock` | engine hooks |

Plain functions assigned in the class body are fine (`ui = ui`); the base class
turns them into static methods for you.

Recommended files (a building is a closed unit, keep everything in its folder):

    towns/<town>/<building>/
        __init__.py   the class and BUILDING
        building.py   COMMANDS = {name: handler}
        content.py    texts, prices, constants (no logic)
        rules.py      game logic
        ui.py         panel(services, player) -> Panel
        npcs.py       the people working here (data only)
        items.py      gear of those people (data only)
        dialogue.py   TOPICS for the residents (data only)

Import heavy modules inside the functions (see `towns/*/post_office`): the
building is imported while the game starts, so top-level imports of `content`
or `models` can create circles.

## A building with a command and a panel

    from ....models import Message
    from ....town_buildings import Building
    from ....view import Button, Panel


    def do_smokehouse(services, player, args):
        return [Message("The smoker hands you a warm ham.", player.name)]


    def ui(services, player):
        return Panel("Smokehouse", ("Hams, sausages, bacon.",),
                     (Button("Ask for a ham", "!smokehouse ham"),))


    class Smokehouse(Building):
        key = "smokehouse"
        title = "Smokehouse"
        blurb = "Hams hang from every beam."
        greeting = "Welcome in, welcome in."
        icon = "🥓"
        commands = {"smokehouse": do_smokehouse}
        place_commands = ("smokehouse",)
        ui = ui


    BUILDING = Smokehouse()

Command names are identical in every town (`!tavern` is the tavern wherever
you are). A player who types the command of a building their town does not
have is told so and nothing happens.

## People: npcs.py, items.py, dialogue.py

The residents of a town are exactly the NPCs of its building folders.

`npcs.py` is pure data (no imports): `NPCS = {key: record}`. A record is the
complete initial NPC record; the NPC json is seeded from it once, later edits
happen in the json. Copy a record from another building and change it. Set
`profile["building"]` to the building key. Residents appear in `!meet`, `!chat`
and the town overview in the order of the building, then the order in the file.
NPC names in texts are tokens (`<<npc.KEY_first>>`), so a blurb may say
`"Madame <<npc.rose_first>> runs the place."`.

`items.py` is pure data: `ITEMS = {id: item}` (optional `ITEM_SETS`); NPC gear
uses the ids `<npc key>_<name>`. `dialogue.py` is pure data:
`TOPICS = {npc key: {"work": [...], "town": [...], "self": [...]}}`.
All three are found automatically; nothing is registered anywhere.

## Shared kinds: derive, do not copy

Tavern, bank, smith, clinic, brothel, station, shop, brewhouse and post office
exist in several towns. Their engine and a base class live in
`town_buildings/<kind>/`. A town folder only derives from it and gives it a
face:

    towns/dusk_hollow_vampires/tavern/__init__.py

    from ....town_buildings.tavern import Tavern


    class TheRedCup(Tavern):
        title = "The Red Cup"
        blurb = "Wine of a very particular vintage."


    BUILDING = TheRedCup()

Override whatever the town should do differently (texts, `order`, `jobs`,
`commands`). A town without the folder has no such building.

## Counter buildings

If the building is a counter with a few offers (like the black market or the
salon), build a `Special` with `Offer`s in `content.py` and set

    counter = content.SPECIAL
    commands = {KEY: counter_command(KEY)}

(`counter_command` comes from `town_buildings.counter`); the web
panel is generated from the offers. See `towns/mudgate_goblins/black_market/`.

## Checklist

1. Folder `towns/<town>/<key>/` with `__init__.py` and `BUILDING`.
2. `key` = folder name, `title`, `blurb` (and `greeting` for a welcome).
3. Optional: commands, panel, people, items, texts.
4. `python -m pytest tests/test_building_framework.py` – every folder of every
   town is checked (class, key, order, residents).
5. Write a small test next to your building (`tests/test_<building>.py`).

Not part of this framework (yet): dungeon places and events under
`cursed_descent/locations/` and `cursed_descent/events/`.

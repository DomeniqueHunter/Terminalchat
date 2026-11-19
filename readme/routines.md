# NPC daily routines

A routine tells one NPC where to be. An NPC **without** a routine stays in its
own building, as before. An NPC **with** a routine moves between buildings
(and towns) while the game runs. The routine only decides *where the NPC is*;
the NPC's jobs (shop keeper, operator) stay the same.

## Add a routine in 2 minutes

Create a file `routines.py` in any building folder under
`towns/<town>/<building>/` and fill `ROUTINES`:

```python
from ....routines import Schedule, Spot, Stop, Wander

ROUTINES = (
    Schedule("camilla", (
        Stop("tavern", 18, 22),
        Stop("brothel", 22, 4),
    )),
    Wander("serafine", spots=(Spot("tavern", weight=3), Spot("shop")),
           stay=(1, 3)),
)
```

That is all. The file is found by its name, nothing has to be registered.
Remove the file (or the entry) and the NPC stays at home again.

## Two kinds

| Kind | Meaning |
|---|---|
| `Schedule(npc, stops)` | fixed day plan, hours on the world clock (0-24) |
| `Wander(npc, spots, towns, stay)` | random: the NPC goes where it likes |

### Schedule
- `Stop(building, start, end, town="")`: from `start` to `end` o'clock. The
  range may wrap past midnight (`Stop("brothel", 22, 4)`).
- Outside every stop the NPC is at home.
- `town` empty = the NPC's own town. Another town key sends the NPC there.
- `building="@home"` means the NPC's own building (to end a trip early).

### Wander
- `spots`: places to choose from, `Spot(building, town="", weight=1)`.
  Without spots the NPC may go to any building of the allowed towns.
- `towns`: empty = own town, `("*",)` = every town, or a list of town keys.
  Only used when `spots` is empty.
- `stay`: hours (min, max) on the world clock before choosing a new place.

## Rules
- One routine per NPC key; a second one raises an error at start.
- `npc` must be the key of a resident (the key used in `npcs.py`).
- Hours are world hours; one world day is `WORLD_DAY_SECONDS` real seconds.

## What changes in the game
- An NPC with a routine is **only where she is**. In every other place she is
  not listed (Locals panel, `meet`) and cannot be addressed (`talk`, `chat`,
  `examine`, romance and house menus that look her up). When she leaves her
  palace, nobody finds her there.
- In her home building she still appears, greyed out, with a note such as
  "away: at the Bank" (Web and GUI); the buttons are disabled.
- In another town she counts as a visitor there.
- NPCs without a routine behave as before.
- Keepers keep working: shops and operators are not tied to the NPC's position.

First user: `towns/last_light_humans/cafe/routines.py` (Madame Bertha goes to
the bank at 10 o'clock and to the tavern in the evening).

## Texts for the places (routines.json)

Next to `routines.py` lies `routines.json`. For every place where the routine
puts the NPC *away from home* it needs an entry with a description and a pool
of lines:

```json
{
  "bertha": {
    "bank":   { "examine": "She stands at the counter ...", "dialogues": ["'Line one.'", "'Line two.'"] },
    "tavern": { "examine": "...", "dialogues": [] }
  }
}
```

- Key: the building (`"bank"`); for another town `"town_key:building"`.
- `examine` replaces nothing, it is shown above the normal description.
- `dialogues` is a pool. At that place `talk` and every `chat` topic draw from
  it instead of the NPC's normal lines.
- **Empty fields grey out the buttons.** No `examine`: the Examine button is
  disabled and the command answers "nothing to see yet". No `dialogues`: Talk
  and the chat topics are disabled and answer "nothing to say here yet".
- At home the NPC keeps her normal texts.

## Using the services of a place (uses + npc_actions.json)

An NPC may use what a building offers, but only at a place where the routine
puts her **away from home**. At home she never uses her own services, and a
`Stop` or `Spot` naming her own building is refused with an error (home is the
default place already).

1. The routine lists what she may do: `Schedule(..., uses=("order_drink",))`.
2. The building lists what can happen in `npc_actions.json`
   (`town_buildings/<kind>/` for every town, or `towns/<town>/<building>/` to
   override it for one town):

```json
{
  "order_drink": { "weight": 4, "needs": "", "text": "{npc} orders a mug." },
  "serve_order": { "weight": 3, "needs": "waiter", "gold": [3, 8],
                   "text": "{npc} waves you over and tips you." }
}
```

- `needs`: the job a player must be working there right now (`waiter`,
  `milk`, `dancer`, ...). Empty = free action, shown as an ambient line to
  everybody standing in the building.
- `gold`: pay for the worker, `satisfy`: needs change of the worker (optional).
- `{npc}` and `{name}` are filled with the NPC's and the worker's name.
- Every 1.5 to 4 minutes (`NPC_ACTION_SECONDS`) each NPC away from home draws one
  action by weight from those she may use and that are possible right now.
  Nothing possible = nothing happens, she simply stands there.
- `uses=("guest",)` additionally makes her a guest/client in buildings that
  take visitors (cafe seats, brothel).

## Home time windows (sleep, eat, rule ...)

A `Schedule` may name times when the NPC is at home but busy with something
else:

```python
Schedule("alexandra", (...), windows=(
    Window("sleep", 4, 6),
    Window("eat", 6, 7),
))
```

In `routines.json` the window gets its own entry with the key `@<window>`
(`"@sleep": {"examine": "...", "dialogues": []}`). Empty dialogues grey out
talk/chat, so a sleeping NPC cannot be spoken to. In `npc_actions.json` an
action with `"when": "sleep"` is only done in that window, `"when": "home"`
at home outside every window (combine with commas: `"home,sleep"`); no `when` (default) = only while away from home.

## Entourage: slaves and other held players

A player held by an NPC (see `readme/control.md`) follows that NPC: put the
NPC key into the control data (`control.start(..., npc="alexandra")`).
The player is moved to the NPC's place every tick and can watch. Actions
may use `"needs": "slave"`: the held player is then the target. Optional
`"text_slave"` is what the held player reads ("You" form, `{npc}` only),
everybody else in the room reads `"text"`.

## Hooks

`"hook": "name"` in an action calls `HOOKS["name"]` from a `hooks.py` in the
building folder (town folder first, then `town_buildings/<kind>/`):

```python
def my_hook(services, npc, worker, place) -> list[Message]:
    return []

HOOKS = {"name": my_hook}
```

The hook runs after the action text, `worker` is the target (or `None`).

## Debugging

`!time` (debug/admin only) shows the world clock and where every routine NPC is right now.
`!time 21` or `!time 15:30` sets the world clock to that hour, so a plan can be checked without waiting.
`!time +2d` lets 2 world days pass at once (respawns, cooldowns, daily events; at most 365).

## For programmers
- `routines.location_of(key)` gives the current `Place(town, building)` or
  `None` if the NPC is at home.
- `routines.people(town, building)` lists the residents standing there now.
- `routines.reachable(player, npc_key)` tells whether the player stands where the NPC is
  (always true for NPCs without a routine). Use it wherever an NPC is looked up by name.
- `RoutineBoard.tick(now_hours)` moves everybody; `TownServices` calls it each
  tick with the world clock. Tests call it directly.
- Write a new kind by subclassing `Routine` and implementing `place(...)`.

## Hiding an NPC for a while

An NPC whose profile has `gone_until` (world hours) is invisible and cannot
be reached until that time has passed (`routines.HIDDEN`). The castle uses
this for a slave who has been drained until a replacement arrives.

# Control: a player is held by someone

A *control kind* describes one way a player character loses control: the
player keeps watching the game but cannot act. The first use is
"slave of Alexandra", but the system knows nothing about her: any building
can add a kind.

## Add a kind in 2 minutes

Create `control.py` in any building folder under `towns/<town>/<building>/`:

```python
from cursed_descent.control import ControlKind

KINDS = (
    ControlKind(
        key="leash_example",
        title="On a leash",
        hours=48,
        safeword=True,
        can_end=True,
        start_text="{holder} clips a leash to your collar.",
        watch_text="You follow {holder} and can only watch.",
    ),
)
```

It is found by its file name, nothing is registered. Texts may use
`{holder}` (name of the one who holds) and `{name}` (the player).

## Fields

| Field | Meaning |
|---|---|
| `key`, `title` | unique id, panel title |
| `hours` | world hours until the hold ends by itself (0 = never) |
| `safeword` | player may release themselves with `[slave release]` |
| `can_end` | player may use END (see below) |
| `open_commands` | extra commands allowed while held (looking, status, chat, talk are always open) |
| `*_text` | start, watch, release, expire, end_ask, end, locked |

## What the player can do

- `[slave]` shows status, `[slave release]` is the safeword.
- `[slave end]` asks, `[slave end confirm]` ends the *character*: a copy
  stays behind as a permanent slave NPC (`npc="slave"`), the player respawns
  like after a death.
- The web panel shows the same as buttons (Status, Safeword, End character).

## Programmer API

```python
from cursed_descent import control
control.start(services, player, "leash_example", holder="Alexandra")
control.kind_of(player)      # ControlKind or None
control.holder_of(player)    # name or ""
control.holders("leash_example", repository)  # held players, oldest first
control.release(services, player)
```

State lives in `player.profile["control"]`: `kind`, `holder`, `since`,
`until` (world hours), `data` (free dict for the kind's own use).
Every command passes `control.lock` first, so a held player cannot do
anything not listed as open.

## Debugging

`!slavereset` (debug/admin only) frees the caller from any leash and clears
Alexandra's "remembers your face" cooldown, so the offer can be tried again
at once.

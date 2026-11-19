# The Drainer (event, very rare monster)

A hollow-eyed figure with a belt of bottles. Code: `events/drainer/`, monster template in `monster/drainers/content.py`.

## Rules
- Spawn rule `drainer` (stage 12+, weight 1, `once_per_run`). `!trigger drainer` shows him at any time.
- Every living human member votes (NPC companions do not): `sacrifice <name>` for a member who still has something to give, `challenge` to fight. A strict majority decides at once; if everybody has voted without a majority, the top options are drawn by lot.
  The idle safety net (PAUSED_IDLE_SECONDS) ends the event: no vote -> he fades away; otherwise the votes cast count.
- Sacrifice: nobody dies and nobody leaves the group. The character is drained permanently, one part per sacrifice, the first that is left (`PARTS` in `config.py`):
  1. chest: bust to 0 (label "Boy Chest" for Female, "Flat Tire" for the rest)
  2. butt to `MIN_BUTT` 60 ("Flat-ass")
  3. manhood (only `HUNG_GENDERS`): endowment and girth to the minimum ("Fail Male")
  4. balls (only `HUNG_GENDERS`): replaced one to one by silicone (`body["fake"]["balls"]`, "Silicone balls")
  Female characters stop after butt. A character with nothing left is not offered. The labels are stored in `body["drained"]` and shown by `body_text`.
- Every drained part goes into a bottle (`ledger.py`, file `drainer.json` in the data folder): id, victim, gender, part, the old values, `held` (true while it is in somebody's hand or bag). One bottle holds one part. Examine and the location tab list whose bottles he carries.
- Fight: strong boss (`hp 600, attack 26, defense 12`, scaled by stage like all enemies). On a win one random bottle leaves his belt and the party votes who gets it (`give <name>`, `depart` leaves it back on the shelf). Only members with room in the bag can receive it. A strict majority decides; if everybody has voted without a majority (for example everybody wants it), the dice decide.
- The bottle becomes a real item: template `drainer_bottle_<id>` (consumable, epic, never loot), named after the real values ("Bottle: Lena's chest (450 cc)"), fixed price per part (`PRICES` in `config.py`), registered at startup from `drainer.json` (`Ledger.register_all`). It can be traded, stored and sold to an NPC trader at the fixed price. `consume <nr|name>` drinks it: the values return in full (the higher value wins), the bottle is gone. Manhood and balls bottles only work for hung genders (a Female cannot grow a cock in the clinic either). In a fight `use` refuses it.
- A market with player-set prices can reuse the item as it is.
- Wipe: the party falls (or surrenders) -> one random human member who still has a part is drained and a bottle is added.

## Files
- `config.py` constants, `ledger.py` body changes and the bottle file, `event.py` vote and resolve (`DrainerMixin`)
- `content.py`, `fates.py` texts, `spawn.py` the spawn rule; fate `drained` is the death text when he kills someone in the fight
- `web/run_panels.py: drainer_panel` (sacrifice / give buttons, votes, bottle shelf)
- `session.py`: `clear_bonus` hands over to `offer_restore`, `end_run` calls `drainer_wipe`

## Reset
Nothing. Delete `drainer.json` to empty his belt (the drained bodies stay drained).

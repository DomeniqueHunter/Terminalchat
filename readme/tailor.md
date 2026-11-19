# Rook & Thread (tailor of Dusk Hollow)

Folder `towns/dusk_hollow_vampires/tailor/`. Owner: Mistress Delphine Rook (NPC `delphine`, vampire tailor). A counter building: every item in `content.py` is an `Offer`; price = `price` of the item, bought with `!tailor <nr>` or the buttons. Wares are never looted and never in other shops.

## Wares (`items.py`)
25 pieces in the slots crotch (skirts, trousers, hotpants), lingerie (thongs, garters), feet, gloves, head, chest (blouses, coats, dresses) and accessory (nipple chains), gender class `lady`, `gent` or `both`. Common 40, rare 150, epic 500 (a few higher). Mistress Delphine's own two pieces (`delphine_*`) are gear and not for sale.
Items with `reveals` leave areas bare (see [exposure](exposure.md)).

Restraint gear (tab Bindings) is described in [kept](kept.md).

## Sets (`ITEM_SETS` in `items.py`; the bonuses of every reached step add up)
| Set | Pieces | 2 | 3 | 4 |
|---|---|---|---|---|
| Pale Court | veil, ballgown, lace gloves, lacquered ankle boots | +2 INT | +3 armor | +4 allure |
| Velvet Hours | velvet laced thong, pleated velvet skirt, open-bodice velvet dress, silk thigh-highs | +2 allure | +1 allure | +3 allure, +2 VIT |
| Revealing Mistress | lace thong, satin hotpants, dress of open doors, gilded bell chains | +3 allure | +2 allure | +3 allure |
| Dagger & Lace | dagger garter, slit silk skirt, corset bodice dress | +2 AGI | +10 % crit, +2 armor | - |
| Gentleman of the Hollow | silk pouch brief, tailored black trousers, velvet frock coat, gentleman's black boots | +2 STR | +3 armor | +10 % melee, +4 allure |
Every piece of a set sits in its own slot, so each set can be completed. A test checks this.

## Reset
Nothing. A new NPC file is seeded from `npcs.py` at the next start.

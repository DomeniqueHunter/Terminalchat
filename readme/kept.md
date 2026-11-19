# Contract of Keeping and bindings (Dusk Hollow only)

Only the vampire town has this for now. Other peoples can switch it on later with their own masters.

## Contract of Keeping (Castle Markov)
Needs the castle invitation. `!castle <nr>` with one of the five contract entries: Mistress Delphine, Mistress Camilla, Master Cassian, Master Ignatius, Mistress Leopoldine.
- Lasts 24 hours real time (`HOURS` in `castle/kept_content.py`). In that time the hero cannot use `lobby`, `join`, `start` or `force`.
- `Serve your master`: up to 6 scenes per contract, each pays 25-45 gold.
- When the time is up: 300 gold and the buff `kept_glow` (+3 allure, +1 VIT) until the next run ends. The end is settled the next time the hero tries a blocked command or opens the castle.
- `Buy out your contract`: 150 gold, no pay, no buff.
- State is `player.profile["kept"] = {master, until, serves}`. Nothing to reset.

### Titles
Each master has a `title` in `MASTERS` (`castle/kept_content.py`). Anybody can ask for another one: change `"Mistress"` to `"Master"` there, for instance for a very muscular vampire woman who prefers it.

### More masters
Add an entry to `MASTERS` (title, name, sign line, serve line). The castle menu picks it up. Other towns would copy `castle/kept.py` into their own building, or the code moves to a shared module.

## Bondage act
A new act `bondage` for the brothel shifts (`serve bondage give|receive`). Only Dusk Hollow offers it (`TOWN_ACTS` in `town_buildings/brothel/practices_content.py`); `practices bondage` shows the texts. Add a town to `TOWN_ACTS` to switch it on there. Dominant vampires (Delphine, Camilla, Cassian, Ignatius, Leopoldine) have it in `npcs/kinks.py` (`bond`).

## Bindings (Rook & Thread, tab "Bindings")
Restraint gear in the normal slots, so no new slot is needed.

| Item | Slot | Price | Allure |
|---|---|---|---|
| Leather Wrist Cuffs | gloves | 40 | 1 |
| Leather Ankle Cuffs | feet | 40 | 1 |
| Velvet Blindfold | head | 40 | 1 |
| Collar with Ring | accessory | 150 | 2 (+1 VIT) |
| Chain Leash | accessory | 150 | 2 |
| Silk Rope Harness | chest | 150 | 2 (bare breasts) |
| Leather Gag | head | 150 | 2 |
| Spreader Bar | accessory | 500 | 3 |

Set **Kept**: wrist cuffs, ankle cuffs, blindfold, collar. 2 pieces +2 allure, 3 pieces +2 more, 4 pieces +4 more and +2 VIT.

## For developers
`Offer.show_if` shows a counter entry only while a profile flag is set (`hide_if` is the opposite). Buildings may define `lock(services, player, command)`; if it returns messages the command is blocked.

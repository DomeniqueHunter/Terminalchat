# Plants

Every garden plant is one folder `cursed_descent/plants/<key>/`. `plants/__init__.py` finds all folders by itself and collects them into `PLANTS`, `ITEMS`, `BUFFS` and `DROPS`; nothing else has to be changed for a new plant.

Files of a plant folder (all required, they may be empty):

- `plant.py`: `PLANT` dict. `name`, `need` (growth needed for each stage, one entry per stage in `furnishing/plants.py` `STAGES`), `comfort` (per stage), `regrow` (stage index after a harvest), `nectar` / `nectar_overgrown` (min, max), `nectar_item`, `seed_item`, `seed_chance`, `feed` (rules for the feed interaction: `label`, `min_endowment`, `min_balls`, `min_sweat_tier`, `store_from`, `store_cap`), `looks` (one text per stage), `wilted` (text) and `texts` (overrides of the default texts, see `furnishing/plants.py` `TEXTS`; use `{plant}` where the plant name is needed).
- `items.py`: `ITEMS` dict with the seed (`"seed": "<key>"`) and the harvest item.
- `buffs.py`: `BUFFS` dict (`home_bloom` and `home_drained` are used by the engine).
- `drops.py`: `DROP` dict or `None`. `tribe` of enemies that drop the seed, `item`, `chance` per enemy, `max`, `boss` (count when a boss of that tribe is there) and `text`.

Rules of the engine (growth per run, wilting, feeding, Overgrown, Drained) are described in `readme/furnishing.md`.

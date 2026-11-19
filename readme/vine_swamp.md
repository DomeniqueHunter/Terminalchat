# Vine Swamp, Pheromone Bloom and Pod Garden

- Biome `Vine Swamp` (from stage 16, `monster/biomes.py`), boss Swamp Seductress Ylvara.
- Monster `pheromone_bloom` (`monster/vines/content.py`, tribe `vines`, sweeps the whole party).
- Futa chars (`FUTA_GENDERS` in `config.py`) get warnings in the swamp. Sweat above 30 % of
  `VINE_FULL_SWEAT` gives a chance of a Bloom ambush, above 60 % it is certain (`vine_ambush.py`).
- Fates: futas end as `podded` (pod variant is stored in the remains `detail`), everybody else as
  `vined` (`locations/pod_garden/fates.py`, picked in `combat.pick_other_fate`).
- Pod variants: classic, pumpkin, tuber, cocoon, flytrap, nectar, burrow (picked from the fate text via `MARKERS`).
- Event location `pod_garden` (`locations/pod_garden/`): lists up to `POD_SHOWN` unharvested pods
  from other runs, `harvest <nr>` gives the pod item, sometimes goo and a seed, and the gear the
  victim lost.
- Pods sell in every tavern for `POD_SELL_FACTOR` times their price (`town_buildings/tavern/pods.py`,
  `!sellpods <nr|all>`).
- Seeds: after a cleared stage the vines (tribe `vines`) drop `seductress_seed` (`chance` per vine, at most `max`; a boss always gives `boss`; set in `plants/seductress/drops.py`). The seed is a plain item for now and will be planted in the house garden later.

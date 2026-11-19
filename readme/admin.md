# Admin and debug commands

These work for admins and in debug mode only.

- `!time`, `!time 19:30`, `!time +2d`: world clock (see routines.md).
- `!slavereset`: frees the caller from any leash (see control.md).
- `!rename Old name | New name`: renames a character. The character keeps its
  id; the database handle/key, the JSON `name` and every other place that
  stores the old name as a plain value (other characters, houses, mail) are
  updated. Names that are already taken are refused.

# Mail housekeeping

Mail lives in `mail/<char id>.json`, one file per player; `mail.json` only
holds the counter and pending NPC replies. Read letters disappear after 14
world days, collected parcels after 7, unread ones after 60. A letter can
also be deleted with its Delete button.

## Items

- `!itemlist [slot|rarity|search word] [page]` lists the items (id, name, slot, rarity), 40 per page.
- `!giveitem <item id or name> [player]` puts the item into the bag of the player (default: yourself).
- `!items` only cleans up unused item records (`!items purge`).


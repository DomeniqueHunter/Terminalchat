# Mage tower prototype: initial names and files. The mage lives in his NPC json;
# changing the name there renames him in the game (file name stays fixed).
SCOPE = "mage_tower"
DEFAULTS = {
    "file": "mage_items.json",
}

# Initial records of the NPCs living here: the NPC json is seeded from these
# values once; later edits happen in the json.
NPCS = {'archmage_orlen': {'schema_version': 6,
                    'name': 'Orlen',
                    'needs': {'hunger': 0,
                              'thirst': 0,
                              'sleep': 0,
                              'arousal': 0},
                    'npc': 'archmage_orlen',
                    'age': 58,
                    'spouse': '',
                    'personality': 'bored, vain, amused by everything small',
                    'race': '',
                    'profile': {'kind': 'figure',
                                'role': "Archmage of the Mage's Tower",
                                'town': 'last_light',
                                'building': 'mage_tower',
                                'look': 'A tall man in midnight-blue robes, '
                                        'silver at the temples, rings on '
                                        'every finger. He looks at you the '
                                        'way a collector looks at a pinned '
                                        'insect: with interest, and with no '
                                        'hurry. The robes do little to hide '
                                        'what hangs beneath them, and your '
                                        'eyes keep drifting there no matter '
                                        'how hard you try not to look.',
                                'quotes': ["'Everything has a price. Most "
                                           "things have a fair one.'",
                                           "'Magic is only patience with "
                                           "better manners.'",
                                           "'Do try not to touch the "
                                           "shelves.'"],
                                'topics': {},
                                'address': 'event:mage_tower:1',
                                'home': "Mage's Tower",
                                'prefs': {'role': 'switch',
                                          'positions': [],
                                          'flow': {'bdsm': 'G',
                                                   'spanking': 'T'}}},
                    'bag_extra': 0,
                    'first_name': 'Orlen',
                    'last_name': '',
                    'gender': 'Male',
                    'level': 1,
                    'exp': 0,
                    'free_points': 0,
                    'gold': 50,
                    'body': {'height': 188,
                             'weight': 80,
                             'build': 'Average',
                             'breasts': 'None',
                             'muscle': 30,
                             'endowment': 50,
                             'girth': 20,
                             'balls': 9,
                             'bust': 0,
                             'butt': 95,
                             'fake': {},
                             'breasts_real': 'None'},
                    'stats': {'strength': 5,
                              'agility': 5,
                              'vitality': 5,
                              'intelligence': 5},
                    'affinity': {'melee': 0,
                                 'magic': 0,
                                 'dodge': 0,
                                 'guard': 0,
                                 'heal': 0},
                    'equipment': {'weapon': {'id': 'archmage_orlen_staff_of_patient_manners',
                                             'by': 'shop'},
                                  'head': {'id': 'archmage_orlen_silver_thread_hood',
                                           'by': 'shop'},
                                  'chest': {'id': 'archmage_orlen_midnight_blue_archmage_robes',
                                            'by': 'shop'},
                                  'gloves': None,
                                  'feet': None,
                                  'accessory': {'id': 'archmage_orlen_ring_set_of_ten_rings',
                                                'by': 'shop'},
                                  'lingerie': None,
                                  'crotch': None},
                    'inventory': ['potion_small', 'potion_small'],
                    'records': {'deepest_stage': 0, 'runs': 0, 'kills': 0},
                    'deaths': {},
                    'pregnant': '',
                    'offspring': [],
                    'body_mods': {},
                    'enhancements': []}}

NPC_TOKENS = {
    "archmage_orlen": {
        "owner": "Archmage {first}",
        "owner_short": "{first}",
    },
}

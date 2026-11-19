# Initial records of the NPCs working here: the NPC json is seeded from these values once;
# later edits happen in the json.
NPCS = {'thorgrim': {'schema_version': 6,
              'name': 'Thorgrim',
              'needs': {'hunger': 0, 'thirst': 0, 'sleep': 0, 'arousal': 0},
              'npc': 'thorgrim',
              'age': 124,
              'spouse': '',
              'personality': 'stern, exact, proud of a spotless ledger',
              'race': 'dwarf',
              'profile': {'kind': 'resident',
                          'role': 'Postmaster of Ironhold',
                          'town': 'ironhold',
                          'building': 'post_office',
                          'look': 'A stocky dwarf in a soot-grey uniform '
                                  'coat, a long iron-grey beard braided with '
                                  'brass rings, a stamp the size of a fist '
                                  'and forearms like anvils.',
                          'quotes': ["'A seal is a promise. Break it and I "
                                     "will remember.'",
                                     "'Weigh it, seal it, pay it. In that "
                                     "order.'",
                                     "'Dwarves do not lose mail. Mail loses "
                                     "its way, and I find it.'"],
                          'topics': {'work': ["'Every letter weighed to the "
                                              'grain, every parcel sealed '
                                              'with iron wax. That is how '
                                              "trust is made.'"],
                                     'town': ["'Ironhold runs on ledgers and "
                                              'hammers. I keep the ledgers '
                                              'straight so the hammers can '
                                              "swing.'"],
                                     'self': ["'My grandfather carried post "
                                              'through the deep halls for '
                                              'ninety years. I only have a '
                                              "few decades to catch up.'"]},
                          'address': 'town:ironhold:post_office:1',
                          'home': 'Post Office, Ironhold',
                          'prefs': {'role': 'switch',
                                    'positions': [],
                                    'flow': {}}},
              'bag_extra': 0,
              'first_name': 'Thorgrim',
              'last_name': 'Sealwright',
              'gender': 'Male',
              'level': 1,
              'exp': 0,
              'free_points': 0,
              'gold': 50,
              'body': {'height': 134,
                       'weight': 88,
                       'build': 'Heavy',
                       'breasts': 'None',
                       'endowment': 14,
                       'girth': 14,
                       'balls': 6,
                       'endowment_shape': 'Stout',
                       'muscle': 65,
                       'bust': 0,
                       'butt': 100,
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
              'equipment': {'weapon': None,
                            'head': None,
                            'chest': {'id': 'thorgrim_soot_grey_uniform_coat',
                                      'by': 'shop'},
                            'gloves': None,
                            'feet': None,
                            'accessory': {'id': 'thorgrim_iron_seal_stamp',
                                          'by': 'shop'},
                            'lingerie': None,
                            'crotch': None},
              'inventory': ['potion_small'],
              'records': {'deepest_stage': 0, 'runs': 0, 'kills': 0},
              'deaths': {},
              'pregnant': '',
              'offspring': [],
              'body_mods': {},
              'enhancements': []}}

# Initial records of the NPCs living here: the NPC json is seeded from these
# values once; later edits happen in the json.
NPCS = {'grizzle': {'schema_version': 6,
             'name': 'Grizzle',
             'needs': {'hunger': 0, 'thirst': 0, 'sleep': 0, 'arousal': 0},
             'npc': 'grizzle',
             'age': 62,
             'spouse': '',
             'personality': 'loud, cheerful, labels everything',
             'race': '',
             'profile': {'kind': 'figure',
                         'role': 'Goblin foreman of the Sweatery',
                         'town': 'last_light',
                         'building': 'sweatery',
                         'look': 'A squat old goblin with a measuring jug on '
                                 'a chain around his neck, a clipboard full '
                                 'of names and a grin that shows three teeth. '
                                 'Every bottle in the shed carries his '
                                 'scrawl.',
                         'quotes': ["'Naked is best, boots are fine!'",
                                    "'Squeals? Workplace noise. Keep "
                                    "sweating!'",
                                    "'Honest pay for honest sweat.'"],
                         'topics': {'work': ["'Run, lift, lie on the plate, "
                                             'haul sacks. All of it makes '
                                             'sweat. Sweat makes potions. '
                                             "Potions make me rich.'",
                                             "'Five cycles per shift. Do not "
                                             'skip a cycle. I can tell by the '
                                             "smell.'",
                                             "'The grill is a house "
                                             'specialty. Clamp, flip, gather '
                                             "the drippings.'"],
                                    'town': ["'Brewers buy by the litre. "
                                             'Alchemists buy by the smell. '
                                             "Nobody ever buys by the name.'",
                                             "'Gnomes run a fancy sweatery "
                                             'two tunnels over. Very brass. '
                                             "Very boring.'",
                                             "'Tell the town we pay fair. And "
                                             'that nobody has ever caught '
                                             "fire. Very much.'"],
                                    'self': ["'I label. I label everything. "
                                             "My wife is labelled too.'",
                                             "'Boots stay on, always. Boots "
                                             'are where the good stuff '
                                             "hides.'",
                                             "'I sniff the sweat and I can "
                                             'tell who you are. Do not ask '
                                             "how.'"]},
                         'address': 'event:sweatery:1',
                         'home': 'Perspiratorium',
                         'prefs': {'role': 'switch',
                                   'positions': [],
                                   'flow': {'foot': 'G',
                                            'facesitting': 'G',
                                            'footjob': 'T'}}},
             'bag_extra': 0,
             'first_name': 'Grizzle',
             'last_name': '',
             'gender': 'Male',
             'level': 1,
             'exp': 0,
             'free_points': 0,
             'gold': 50,
             'body': {'height': 122,
                      'weight': 44,
                      'build': 'Thin',
                      'breasts': 'None',
                      'muscle': 15,
                      'endowment': 12,
                      'girth': 10,
                      'balls': 4,
                      'bust': 0,
                      'butt': 82,
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
             'equipment': {'weapon': {'id': 'grizzle_foreman_s_clipboard',
                                      'by': 'shop'},
                           'head': None,
                           'chest': None,
                           'gloves': None,
                           'feet': None,
                           'accessory': {'id': 'grizzle_measuring_jug_chain',
                                         'by': 'shop'},
                           'lingerie': None,
                           'crotch': None},
             'inventory': ['potion_small', 'potion_small'],
             'records': {'deepest_stage': 0, 'runs': 0, 'kills': 0},
             'deaths': {},
             'pregnant': '',
             'offspring': [],
             'body_mods': {},
             'enhancements': []},
 'tinkerwick': {'schema_version': 6,
                'name': 'Professor Tinkerwick',
                'needs': {'hunger': 0, 'thirst': 0, 'sleep': 0, 'arousal': 0},
                'npc': 'tinkerwick',
                'age': 94,
                'spouse': '',
                'personality': 'precise, absent-minded, obsessed with '
                               'tolerances',
                'race': '',
                'profile': {'kind': 'figure',
                            'role': 'Gnome head of the Perspiratorium',
                            'town': 'last_light',
                            'building': 'sweatery',
                            'look': 'A tiny gnome in a brass-buttoned coat '
                                    'with three lenses on a swivel in front '
                                    'of her glasses, an engraved tag punch in '
                                    'one hand and a pressure gauge in the '
                                    'other.',
                            'quotes': ["'Please remove all metal. It "
                                       "interferes with the readings.'",
                                       "'Within tolerance. Continue.'",
                                       "'Precision is the only form of "
                                       "kindness.'"],
                            'topics': {'work': ["'Each station is calibrated. "
                                                'The treadmill to the nearest '
                                                'millimetre, the heater to '
                                                'the nearest degree, the '
                                                'sweat to the nearest '
                                                "millilitre.'",
                                                "'We extract more per litre "
                                                'than the goblins. Their '
                                                'method is, how shall I say, '
                                                "enthusiastic.'",
                                                "'Safety margin is two "
                                                'degrees. Sometimes three. '
                                                "Never four. We learned.'"],
                                       'town': ["'The alchemists send me "
                                                'their assistants. I send '
                                                'back precise results and '
                                                "mild embarrassment.'",
                                                "'There is a goblin in the "
                                                'next tunnel who labels '
                                                'bottles with a crayon. '
                                                "Barbaric.'",
                                                "'I am writing a paper on the "
                                                'thermodynamics of heroes. '
                                                "Peer review is pending.'"],
                                       'self': ["'Eleven lenses. Three are "
                                                "decorative.'",
                                                "'I do not squeal. I have "
                                                'never squealed. I hum, at a '
                                                "measured pitch.'",
                                                "'Tea is at four. Do not "
                                                "disturb the tea.'"]},
                            'address': 'event:sweatery:2',
                            'home': 'Perspiratorium',
                            'prefs': {'role': 'switch',
                                      'positions': [],
                                      'flow': {'footjob': 'G', 'foot': 'T'}}},
                'bag_extra': 0,
                'first_name': 'Professor Tinkerwick',
                'last_name': '',
                'gender': 'Female',
                'level': 1,
                'exp': 0,
                'free_points': 0,
                'gold': 50,
                'body': {'height': 105,
                         'weight': 32,
                         'build': 'Slim',
                         'breasts': 'Flat',
                         'muscle': 12,
                         'bust': 120,
                         'butt': 88,
                         'endowment': 15,
                         'girth': 12,
                         'balls': 5,
                         'fake': {},
                         'breasts_real': 'Flat'},
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
                              'head': {'id': 'tinkerwick_three_lens_swivel_spectacles',
                                       'by': 'shop'},
                              'chest': {'id': 'tinkerwick_brass_buttoned_coat',
                                        'by': 'shop'},
                              'gloves': None,
                              'feet': None,
                              'accessory': {'id': 'tinkerwick_engraved_tag_punch',
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

from ...races import race_of_town


ROUGH_MOVES = {
    "slap": ("bust", "The regulars take turns slapping your {bust} {style}; "
             "they jiggle, redden and the {output} sprays over the "
             "rim.", 1.3),
    "ballslap": ("cock", "A fist-sized patron slaps your {balls} {style}. "
                 "You yelp, your {cock} jerks and the {output} spurts "
                 "into the mug.", 1.3),
    "wring": ("any", "Two patrons grab you and wring out the {output} "
              "{style}, ignoring every gasp.", 1.4),
}


def roughness_of(town_key:str) -> tuple[float, str]:
    race = race_of_town(town_key)
    return race.roughness, race.roughness_style

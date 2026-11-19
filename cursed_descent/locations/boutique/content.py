EVENT_TEXTS = {
    "couture": {
        "scent": "<<boutique.owner>> inhales deeply through her nose and "
                 "smiles. 'Mmm. Beautifully worked-in material. I can "
                 "hardly wait.' She sharpens her scissors a little faster.",
        "intro": "🧵 A tall futa in a skin-tight black leather dress – "
                 "corset laced high, gloves to the elbow, boots to the "
                 "thigh, all of it stitched from very particular hides – "
                 "sashays out of the dark, measuring tape in hand. Silver "
                 "streaks in her "
                 "black hair, laugh lines she wears like jewellery, "
                 "fifty-six years old and never better. 'Darlings, that "
                 "fabric – I mean, that skin – simply divine. Hold still. "
                 "I've been doing this since before your mothers were "
                 "born.' – <<boutique.owner>> attacks!",
        "win": "<<boutique.owner>> collapses with a creak of black leather. "
               "'Philistines…' {name} rummages through her sewing kit.",
        "fit": "Down here she has clearly been busy – {count} heroes turned "
               "to fabric and endless stairs to climb have given her arms "
               "and legs some real definition.",
        "toned": "Hauling {count} heroes – and her sewing table – this deep "
                 "into the dungeon has made her "
                 "strong: broad shoulders, toned arms, a waist like a "
                 "corset that laces itself. She cracks her knuckles.",
        "ripped": "{count} heroes have passed through her workroom, and it "
                  "shows: <<boutique.owner>> is positively ripped, her "
                  "leather dress creaking and straining over muscle. She rips "
                  "a measuring tape in half just to make a point.",
        "sweat_sheen": "A light sheen glows on her collarbones. 'It gets "
                       "warm down here, darling.'",
        "sweat_glistening": "She is glistening with sweat, the black "
                            "leather gleaming and clinging to every muscle. "
                            "She dabs her brow with a silk handkerchief – "
                            "made of someone, no doubt.",
        "sweat_dripping": "Sweat runs down her heaving, rock-hard body in "
                          "rivulets, steam rising from her shoulders in the "
                          "cold dungeon air. She grins. 'Let's make this "
                          "quick – I'm working on a new collection.'",
        "loot": "Among her samples is a finished piece from the boutique:",
    },
    "boutique": {
        "intro": "🧵 A shop window glows in the dark: '<<boutique.shop>> – "
                 "Haute Couture – thirty years of excellence'. "
                 "<<boutique.owner>>, fifty-six and utterly unbothered by "
                 "it, leans in the doorway, measuring tape around her neck. 'No fighting "
                 "today, "
                 "darlings – today you shop. Everything handmade, "
                 "everything one of a kind. Some of it you may even "
                 "recognize.'",
        "window": "The door beside the window swings open and Madame "
                  "<<boutique.owner_short>> beckons from inside. 'Window shopping, darlings? "
                  "Nonsense – come in. Today you buy.'",
        "stock": "  [{nr}] {item} – {price} gold",
        "sweaty": "<<boutique.owner>> wrinkles her nose as {name} steps in. "
                  "'Darling, don't touch the silk. … Actually – stand "
                  "still. Let me measure you.' The tape is already out.",
        "sweaty_sale": "<<boutique.owner>> breathes in deeply. 'Fresh off "
                       "the battlefield? I'll pay extra for that.'",
        "empty": "The racks are bare, the mannequins naked. <<boutique.owner>> "
                 "runs her measuring tape through her fingers and looks the "
                 "party over. 'Sold out, darlings. I could use fresh "
                 "material…'",
        "own": "<<boutique.owner>> winks at {name}: 'Recognize the stitching, "
               "darling? I kept the best part of you.'",
        "friend": "{name} stares at the {item}. That's {victim}. Definitely "
                  "{victim}.",
        "options": "Actions: {options} ({seconds} s)",
        "enter": "🧵 A little bell rings as the party steps inside. "
                 "Mannequins in couture line the walls.",
        "buy": "{name} buys the {item} for {price} gold. <<boutique.owner>> "
               "wraps it in tissue paper. 'Wear it well – they certainly "
               "did.'",
        "buy_own": "{name} buys back {their} own {item} for {price} gold. "
                   "<<boutique.owner>> claps. 'A perfect fit – of course it "
                   "is!'",
        "poor": "{name} can't afford the {item} ({price} gold, {name} has "
                "{gold}). <<boutique.owner>> sniffs. 'Window shopping, then.'",
        "full": "{name}'s bag is full. 'Come back when you have room, "
                "darling.' ([sell <nr>] makes room.)",
        "sell": "<<boutique.owner>> inspects the {item} with a loupe, sniffs, "
                "and pays {name} {price} gold. 'Fabric is fabric.' "
                "(💰 {gold})",
        "sell_what": "'Sell what, darling? [sell <nr>] – your bag "
                     "number.'",
        "sellself": "{name} steps onto the little podium. <<boutique.owner>> "
                    "circles {name} slowly, tape measure in hand, and "
                    "counts out {gold} gold. 'A model who volunteers! How "
                    "refreshing. Hold very, very still.'",
        "fresh": "Fresh from the workroom: [{nr}] {item} – {price} gold",
        "depart": "<<boutique.owner>> blows a kiss as the party leaves. 'Do "
                  "drop in again – or let me drop in on you.'",
    },
}


BOUTIQUE_GARMENTS = {
    "codpiece": {"slot": "crotch", "label": "Codpiece", "allure": 4,
                 "armor": 2, "keywords": ["codpiece"],
                 "requires": ["Male", "Herm", "Shemale", "Male-Herm",
                              "Transgender"]},
    "ballbra": {"slot": "crotch", "label": "Ball Bra", "allure": 3,
                "armor": 1, "keywords": ["ball bra"],
                "requires": ["Male", "Herm", "Shemale", "Male-Herm",
                             "Transgender"]},
    "bra": {"slot": "lingerie", "label": "Bra", "allure": 3,
            "keywords": ["bra", "lingerie", "push-up"]},
    "boots": {"slot": "feet", "label": "Boots", "armor": 2, "allure": 2,
              "keywords": ["boots"]},
    "gloves": {"slot": "gloves", "label": "Gloves", "armor": 1,
               "allure": 2, "keywords": ["gloves"]},
    "corset": {"slot": "chest", "label": "Corset", "armor": 4, "allure": 3,
               "keywords": ["corset"]},
    "catsuit": {"slot": "chest", "label": "Catsuit", "armor": 3,
                "allure": 4, "keywords": ["catsuit"]},
    "suit": {"slot": "chest", "label": "Suit", "armor": 5, "allure": 1,
             "keywords": ["suit"]},
    "gown": {"slot": "chest", "label": "Gown", "armor": 2, "allure": 4,
             "keywords": ["gown"]},
    "handbag": {"slot": "accessory", "label": "Handbag", "allure": 2,
                "keywords": ["handbag"]},
    "mask": {"slot": "head", "label": "Mask", "armor": 2, "allure": 2,
             "keywords": ["mask"]},
}


BOUTIQUE_FALLBACK = ("bra", "boots", "gloves")

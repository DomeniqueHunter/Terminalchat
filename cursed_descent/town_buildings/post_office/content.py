KEY = "post_office"
TITLE = "The Post Office"
BLURB = ("Letters and parcels for anybody, anywhere. Collect your parcels "
         "at any post office.")
HELP = ("The Post Office: [post_office] visits it. [mail] shows your "
        "mailbox, [mail send <name> | <subject> | <text> [| gold [| item]]] "
        "writes a letter (also from home), [mail reply <id> | <text>], "
        "[mail read <id>], [mail delete <id>], [mail sent], "
        "[mail block <name>] and [mail unblock <name>]. Parcels (gold, one "
        "item) are collected with [mail collect <id>] in a post office.")
OFFER = "The post office smells of paper, wax and old string."
CLOSED = "The post office is shut while you are down in the dungeon."
AWAY = "Letters and parcels wait until you are back from the dungeon."
NOT_HERE = ("You can only collect parcels at a post office. Letters can be "
            "read and written anywhere.")
EMPTY = "Your mailbox is empty."
UNKNOWN = "There is no letter with that number."
NO_REPLY = "Nobody can answer that letter."
NO_ATTACH = "That letter carries no parcel."
BAG_FULL = "Your bag is full. The item stays in the letter."

CLERKS = {
    "last_light": ("hedda", "Hedda Fenwick",
                   "'Letters, parcels, bad news, good news. Step up, "
                   "love.' Hedda stamps without looking."),
    "mudgate": ("skitter", "Skitter Quillwick",
                "'You want post? Post costs coins! Coins buy string!' "
                "Skitter bounces on his stool."),
    "ironhold": ("thorgrim", "Thorgrim Sealwright",
                 "'Seal it, weigh it, pay it.' Thorgrim brings a stamp down "
                 "like a hammer."),
    "cogsworth": ("wimble", "Wimble Gearwright",
                  "'Welcome to the sorting engine!' Wimble tugs a lever "
                  "and a brass chute rattles."),
    "brandholm": ("leif", "Leif Ketilsson",
                  "'Post! Sign here, here and here.' Leif shifts from "
                  "foot to foot, out of breath."),
    "dusk_hollow": ("mortimer", "Mortimer Ashquill",
                    "'Night post, madam, sir.' Mortimer's wax seal "
                    "glints like a drop of blood."),
}

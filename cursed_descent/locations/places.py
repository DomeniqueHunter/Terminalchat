from ..settings import defaults


PLACE_LOOKS = {
    "hut": {
        "owner": "",
        "outside": "🔎 A squat timber lodge half swallowed by ferns. Antlers "
                   "over the door, a boot scraper shaped like a bear trap, "
                   "and a brass plate: 'T. <<npc.reginald_last>> – Big Game'. The "
                   "curtains are drawn, but something inside glints like "
                   "glass eyes.",
        "inside": "🔎 Every wall is a trophy wall: heads, hides and mounted "
                  "specimens that were clearly once people. A gun cabinet, "
                  "a writing desk with a cigar box, an armchair that looks "
                  "far too well-fitted and a rug that has a face.",
    },
    "butcher_shop": {
        "owner": "Hamhock",
        "outside": "🔎 A low brick shop with a cleaver-shaped sign, sawdust "
                   "on the step and a drain that never quite runs clear. "
                   "Through the open door: hooks, a scrubbed block and a "
                   "huge pigman humming over a whetstone.",
        "inside": "🔎 White tile, sawdust and a long counter with a brass "
                  "scale. Hooks hang in neat rows behind it, a cold chest "
                  "keeps the good cuts, and every knife on the rack is "
                  "named. <<npc.hamhock_first>>'s apron is stiff with the day's work.",
    },
    "farm": {
        "owner": "Old Trotter",
        "outside": "🔎 A red barn, a muddy yard and a fence of grey "
                   "planks. Pens full of fat pigs, a plough leaning by "
                   "the gate and a market carriage with ribbons on its "
                   "shafts. <<npc.old_trotter_first>> watches from the fence, chewing "
                   "a straw.",
        "inside": "🔎 Warm hay, milk pails, a plough harness hanging from "
                  "a nail and a ledger of everyone who ever worked here. "
                  "The stalls are deep and clean. <<npc.old_trotter_first>>'s pipe "
                  "glows in the corner as he counts.",
    },
    "adept": {
        "owner": "",
        "outside": "🔎 A circle of chalk runes on the corridor floor, "
                   "still smudged where someone knelt to draw it. A young "
                   "mage in an oversized robe hovers beside it, wand "
                   "twitching.",
        "inside": "🔎 Inside the circle the air hums. Candle stubs mark the "
                  "points, a half-eaten sandwich sits by the notes, and a "
                  "row of stone figures along the wall looks a little too "
                  "lifelike.",
    },
    "boutique": {
        "owner": defaults("boutique")["figure_first"],
        "outside": "🔎 A shop window glows in the dark: "
                   "'<<boutique.shop>>'. Mannequins in couture, leather "
                   "and silk, each stitched with a little tag.",
        "inside": "🔎 Bolts of cloth, a cutting table with a tape-measure "
                  "whip and mannequins that are far too convincing. "
                  "<<boutique.figure_first>> looks you up and down, measuring.",
    },
}

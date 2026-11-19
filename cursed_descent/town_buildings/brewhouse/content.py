from ..counter import Offer, Special
from ..work.model import Job


KEY = "brewhouse"
TITLE = "Brewhouse"
BLURB = "A <<npc.astrid_last>> sister runs the vats."
OWNER = "The <<npc.astrid_last>> sister"
PLACE = "🍺 The Brewhouse – a <<npc.astrid_last>> sister runs the vats."
CLOSED = "The Brewhouse is shut while you are in the dungeon."
CUT = 0.25
BASE_HEAL = 90

STYLES = {
    "last_light": ("Ada <<npc.astrid_last>>", "Yogurt Drink"),
    "ironhold": ("Gerda <<npc.astrid_last>>", "Dwarf Stout"),
    "cogsworth": ("Tilly <<npc.astrid_last>>", "Cog Fizz"),
    "mudgate": ("Snizzle <<npc.astrid_last>>", "Sour Mash"),
}
AROMAS = {
    "Equine": "Stallion", "Canine": "Wolfhound", "Draconic": "Dragonfire",
    "breasts": "Creamy", "balls": "Heavy", "endowment": "Virile",
    "muscle": "Ironbody", "butt": "Peachy", "plain": "Plain",
}
BATH_DONE = (
    "{sister} skims the vat, sniffs and nods. 'Aroma: {aroma}. That is "
    "going to sell.'"
)
BREW_DONE = "{sister} corks a bottle of plain {style} for you."

JOBS = (
    Job("brew", "Brewer's Hand", KEY, 4, 18, "vitality",
        "Stir, bottle and taste."),
)
HIDDEN_JOBS = {
    "bath": Job("bath", "Vat Bather", KEY, 4, 26, "vitality",
                "Soak in the vat – your aroma goes into the batch."),
    "vore": Job("vore", "Batch", KEY, 3, 30, "vitality",
                "Be the batch."),
    "service": Job("service", "Brewmistress Aide", KEY, 3, 24, "vitality",
                   "Kneel and use your mouth."),
}
SESSION_LINES = {
    "brew": [
        "You stir the vat with a paddle as long as you are tall.",
        "You fill bottles by lamplight, a cork between your teeth.",
        "The sister hands you a spoon. 'Taste. Tell me if it is ready.'",
        "You roll a keg across the cellar and stack it on the rack.",
    ],
    "bath": [
        "You lower yourself into the vat; the batch swirls around you.",
        "The sister stirs slowly around you. 'Hold still, let it take.'",
        "Your skin tingles as the brew soaks you in and you into the brew.",
        "You rest your head on the rim while the aroma seeps out into the "
        "mash.",
    ],
    "service": [
        "You kneel at her feet, warm and close.",
        "The vats bubble behind you while you work.",
        "She leans back, breathing heavily.",
    ],
    "vore": [
        "You are inside her, warm, heavy and held.",
        "The world is a slow, wet heartbeat.",
        "Everything sloshes gently around you.",
    ],
}
SPECIAL = Special(
    KEY, TITLE, BLURB, "🍺", "The <<npc.astrid_last>> sisters",
    "'Every vat has a recipe. Yours can go in the vat, too.'",
    (Offer("Work the vats (4 rounds, 25% cut)", "job", item="brew"),
     Offer("Bathe in a vat (undress, 4 rounds, random vat)", "bath"),
     Offer("Be the batch (3 rounds, she takes you in)", "vore"),
     Offer("Service the brewmistress (3 rounds, for those too heavy)",
           "service")))

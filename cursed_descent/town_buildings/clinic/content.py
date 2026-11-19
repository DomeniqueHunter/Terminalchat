from ...config import CLINIC_MAGIC_FACTOR, CLINIC_PRICES

OFFER = "Let me look at you. {advice} See the list below."

HELP = f"""📖 Help – Clinic
Dr. <<npc.vane_first>>'s Flesh Atelier sits right beside <<npc.velvet_first>>'s shop at the entrance
and is open whenever you are not on a run. Changes are permanent.
  clinic             – show everything she offers and the prices
  mod <part> up|down – grow or shrink a body part by one step; prices
                        rise with size. Parts: height, weight, muscle,
                        bust, butt (and cock, girth, balls if you have
                        them)
  mod <part> up magic – the real thing (bust, butt, cock, girth, balls):
                        {CLINIC_MAGIC_FACTOR}x the price and it can fail.
                        The plain 'up' is a cheaper implant (removed first
                        when you shrink; implants never give milk)
  mod build <name>   – a new figure, e.g. 'build muscular' \
({CLINIC_PRICES['build']} gold)
  mod shape <name>   – endowment shape (equine, canine, ...) \
({CLINIC_PRICES['shape']} gold)
  mod butt|balls|endowment – permanent enhancements: more allure,
                        a little less AGI
  mod remove <name>  – take an enhancement back \
({CLINIC_PRICES['remove']} gold)"""

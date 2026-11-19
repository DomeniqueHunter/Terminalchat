from . import Race


ADVICE = {'bust': 'Your chest could be so much fuller – a pair of implants is quick and neat: [mod bust up].', 'butt': 'A rounder, fuller rear would suit you. Implants: [mod butt up].', 'cock': 'A few more centimetres, an implant: [mod cock up].', 'balls': 'Fuller balls hang so nicely. Implants: [mod balls up].', 'build_thin': 'You are rather lean. More weight or muscle would help.', 'build_heavy': 'Carry it with pride – I can add curves where they count.', 'fine': 'Honestly, I would not change much. Maybe a polish.'}


RACE = Race(
    key='human',
    name='human',
    plural='humans',
    height=(150, 200),
    weight=(45, 160),
    roughness=1.0,
    roughness_style='firmly',
    advice=ADVICE,
    clinic_special=' My speciality is implants – quick, neat, reversible.',
    implant_only=False,
    member=(15, 12, 5),
    member_shape="Human",
    playable=True,
)

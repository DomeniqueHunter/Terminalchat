from ....town_buildings.bank import Bank


class TheCountingEngine(Bank):
    title = 'The Counting Engine'
    blurb = 'A machine does the sums. Rarely wrong. Never sorry.'


BUILDING = TheCountingEngine()

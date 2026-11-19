from ....town_buildings.tavern import Tavern


class TheRedCup(Tavern):
    decency = 0
    title = 'The Red Cup'
    blurb = 'Wine of a very particular vintage. Ask no questions about the vintage.'


BUILDING = TheRedCup()

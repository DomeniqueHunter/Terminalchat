from ....town_buildings.tavern import Tavern


class TheRottenLadle(Tavern):
    decency = 1
    title = 'The Rotten Ladle'
    blurb = 'Soup of the day: unknown. Strong, though.'


BUILDING = TheRottenLadle()

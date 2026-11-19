from ....town_buildings.tavern import Tavern


class TheBrassCog(Tavern):
    decency = 1
    title = 'The Brass Cog'
    blurb = 'Steam-brewed cider and a piano that plays itself badly.'


BUILDING = TheBrassCog()

from ....town_buildings.orphanage import Orphanage


class TheLanternHouse(Orphanage):
    title = "The Lantern House"
    blurb = ("The Lantern House smells of warm porridge and old wood. "
             "Small faces peek around a doorframe, then vanish giggling.")
    greeting = ("The Lantern House smells of warm porridge and old wood. "
                "Small faces peek around a doorframe, then vanish "
                "giggling. Donate gold, food, milk or cream with "
                "[donate].")


BUILDING = TheLanternHouse()

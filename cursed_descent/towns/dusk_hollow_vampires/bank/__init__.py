from ....town_buildings.bank import Bank


class BloodBullion(Bank):
    decency = 2
    title = 'Blood & Bullion'
    blurb = 'Gold keeps better than blood, they say. The vault never sleeps.'


BUILDING = BloodBullion()

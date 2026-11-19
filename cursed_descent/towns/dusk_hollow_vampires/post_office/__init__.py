from ....town_buildings.post_office import PostOffice


class TheNightPost(PostOffice):
    decency = 2
    title = 'The Night Post'
    blurb = 'Letters by moonlight, sealed in red wax.'


BUILDING = TheNightPost()

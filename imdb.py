import urllib.request
from bs4 import BeautifulSoup

URL = "http://www.imdb.com/title/{id}"




def get_rating_for_id(id):
    ''' get the user ratings for input imdb id '''
    request = urllib.request.urlopen(URL.format(id=id))

    if request.code == 200:
        source = request.read()
        soup = BeautifulSoup(source, 'lxml')

        rating_value = soup.find("span", {"itemprop": "ratingValue"}).contents[0]
        rating_count = soup.find("span", {"itemprop": "ratingCount"}).contents[0]

        return rating_value, rating_count


get_rating_for_id('tt0098904')



imdb_id = 'tt0098904'

rating_url = "http://www.imdb.com/title/{id}/epdate"

request = urllib.request.urlopen(rating_url.format(id=imdb_id))


source = request.read()
soup = BeautifulSoup(source, 'lxml')

a = soup.find('h4')

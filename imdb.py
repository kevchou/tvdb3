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


# ----------------------------------------------------
# Ratings for every ep
URL_RATINGS = "http://www.imdb.com/title/{id}/epdate"


def get_ratings_for_show(id):

    data = []

    # Parse http with show ratings
    url = URL_RATINGS.format(id=imdb_id)
    raw_http = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(raw_http, 'lxml')

    # Find table containing ratings in the source
    table = soup.find('table')
    rows = table.find_all('tr')

    for row in rows:

        cols = row.find_all('td')

        try:
            ep_num = cols[0].contents[0].encode('ascii', 'ignore').decode('ascii')
            separator = ep_num.find('.')

            season_num = int(ep_num[:separator])
            episode_num = int(ep_num[separator+1:])

            ep_name = cols[1].find('a').contents[0]
            rating_value = float(cols[2].contents[0])
            rating_cnt = int(cols[3].contents[0].replace(',', ''))

            rating = {
                "Season": season_num,
                "Episode": ep_num,
                "Title": ep_name,
                "Rating": rating_value,
                "Votes": rating_cnt
                }

            data.append(rating)

        except IndexError:
            pass

    return data

# Get source http and parse
seinfeld = 'tt0098904'           # Seinfeld

x = get_ratings_for_show(seinfeld)



for ep in x:
    print("%s %s - %s" % (ep['Season'], ep['Episode'], ep['Rating']))

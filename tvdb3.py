import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime

# TVDB url constants
TVDB_URL = 'http://thetvdb.com/api/'

SEARCH_URL = 'GetSeries.php?seriesname={query}'

SERIES_INFO_URL = '/series/{id}/en.xml'
SERIES_EPISODES_URL = '/series/{id}/all/en.xml'

APIKEY = '15C9D64D3EFCC581'


def get_tvdb_soup(series_id):
    """Retrieves XML from inputted series_id number and returns a BeautifulSoup
    object"""

    url = TVDB_URL + APIKEY + SERIES_EPISODES_URL.format(id=series_id)
    request = urllib.request.urlopen(url)

    if request.code == 200:

        raw_xml = request.read()
        soup = BeautifulSoup(raw_xml, 'xml')

    return soup


class Show(dict):
    """A Show object that holds all the episodes of a show"""

    def __init__(self, series_id):
        dict.__init__(self)

        # Query tvdb and return a BeautifulSoup object
        soup = get_tvdb_soup(series_id)

        self.show_name = soup.find('Series').find('SeriesName').text

        for ep in soup.find_all('Episode'):

            season_num = int(ep.find("SeasonNumber").text)
            ep_num = int(ep.find("EpisodeNumber").text)
            ep_name = ep.find("EpisodeName").text
            air_date = ep.find("FirstAired").text

            # If the season object doesnt exist yet, create it
            if season_num not in self:
                self[season_num] = Season(show_name=self.show_name,
                                          season_num=season_num)

            self[season_num][ep_num] = Episode(show_name=self.show_name,
                                               episode_title=ep_name,
                                               season_num=season_num,
                                               episode_num=ep_num,
                                               air_date=air_date)

    def __getitem__(self, season_num):
        return self.setdefault(season_num, Season(show_name=self.show_name,
                                                  season_num=season_num))

    def __repr__(self):
        return "{name:s} - {num_seas:d} Seasons".format(name=self.show_name,
                                                        num_seas=len(self))

    def get_next_air_dates(self):
        """ Finds unaired episodes and prints them """
        not_aired = []

        for season in self.values():
            for episode in season.values():
                try:
                    d = datetime.strptime(episode.air_date, "%Y-%m-%d")
                    if d >= datetime.now():
                        not_aired.append(episode)

                except ValueError:
                    # air_date missing. just dont append episode
                    pass

        return not_aired
            

class Season(dict):

    def __init__(self, show_name, season_num):
        dict.__init__(self)
        self.show_name = show_name
        self.season_num = season_num

    def __getitem__(self, episode_num):
        return self.setdefault(episode_num, Episode(show_name=None,
                                                    episode_title=None,
                                                    season_num=None,
                                                    episode_num=None))

    def __repr__(self):
        return("{:} - S{:02d}: {:} episodes".format(self.show_name, self.season_num, len(self)))
               

    def get_episode_list(self):
        return ["{num} - {title}".format(num=ep.ep_num, title=ep.episode_title)
                for ep in self.values()]


class Episode:

    def __init__(self, show_name, episode_title, season_num, episode_num,
                 air_date=None):
        self.show_name = show_name
        self.episode_title = episode_title
        self.season_num = season_num
        self.ep_num = episode_num
        self.air_date = air_date

    def __repr__(self):
        output_string = "{show} - S{season:02d}E{ep:02d}: {title:s}"
        return output_string.format(show=self.show_name,
                                    season=self.season_num,
                                    ep=self.ep_num,
                                    title=self.episode_title)


def search(query):
    '''
    Searches tvdb for the input show name to find the correct series id.
    Inputs: show name string
    '''

    assert type(query) == str, "Input needs to be a string"

    search_results = {}

    url = TVDB_URL + SEARCH_URL.format(query=query)
    url = url.replace(' ', '%20')

    request = urllib.request.urlopen(url)

    if request.code == 200:

        raw_xml = request.read()
        soup = BeautifulSoup(raw_xml, 'xml')

        results = soup.find_all('Series')

        for result in results:
            show_id = int(result.find('id').text)

            search_results[show_id] = Show(show_id)

    row_format = "{:<10}" + "{:>20}"
    print(row_format.format("Show ID", "Show Name"))
    for id, show in search_results.items():
        print(row_format.format(id, show.show_name))

    return search_results


class MyShows:
    """Instances of this class will hold an array of Show objects"""
    
    def __init__(self):
        self.my_shows = []

    def add_show(self, series_id):
        """Adds show to the self.my_shows list"""

        new_show = Show(series_id)
        self.my_shows.append(new_show)
        
        print("Added {:} to my shows".format(new_show.show_name))

    def get_next_air_dates(self):
        
        next_eps = []
        
        for show in self.my_shows:
            next_eps += show.get_next_air_dates()

        # Sort by air date
        next_eps = sorted(next_eps, key = lambda ep: ep.air_date)
        
        return next_eps
    
    def __repr__(self):
        return "{:}".format([i for i in self.my_shows])


######## For Testing
    
# example of searching for a show
s = search('11.22.63')


myshows = MyShows()

myshows.add_show(79169)  # Seinfeld
myshows.add_show(275557) # Broad City
myshows.add_show(194031) # Bob's Burgers
myshows.add_show(301824) # 11.22.63

nextairs = myshows.get_next_air_dates()

print()
print("{:<20} | {:<40} | {:<10}".format("Show", "Episode", "Next Air"))
print("-"*20 + "-+-" + "-" * 40 + "-+-" + "-"*10)
for ep in nextairs:
    print("{:<20} | {:<40} |  {:>10}".format(ep.show_name, ep.episode_title, ep.air_date))



s = myshows.my_shows[1]

import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime
from pandas import DataFrame

# TVDB constants
TVDB_URL = 'http://thetvdb.com/api/'
SEARCH_URL = 'GetSeries.php?seriesname={show_name}'

SERIES_INFO_URL = '/series/{series_id}/en.xml'
SERIES_EPISODES_URL = '/series/{tvdb_id}/all/en.xml'

APIKEY = '15C9D64D3EFCC581'


def show_search(show_name):
    """ Searches tvdb for the input show name to find the correct series id.

    Arguments:
    show_name -- show name string
    """

    assert type(show_name) == str, "Input needs to be a string"

    url = TVDB_URL + SEARCH_URL.format(show_name=show_name).replace(" ", "%20")
    request = urllib.request.urlopen(url)

    search_results = {}
    if request.code == 200:
        raw_xml = request.read()
        soup = BeautifulSoup(raw_xml, 'xml')

        results = soup.find_all('Series')

        for result in results:
            show_id = result.find('id').text
            show_name = result.find('SeriesName').text
            search_results[show_id] = show_name
    
    return search_results


def get_soup_for_series(tvdb_id):
    """Retrieves XML from inputted series_id number and returns a BeautifulSoup
    object
    """

    url = TVDB_URL + APIKEY + SERIES_EPISODES_URL.format(tvdb_id=tvdb_id)
    request = urllib.request.urlopen(url)

    if request.code == 200:
        raw_xml = request.read()
        soup = BeautifulSoup(raw_xml, 'xml')
    else:
        print("request error")
        
    return soup


class Episode:
    def __init__(self, show_name, episode_title, season_num, episode_num, imdb_id, air_date=None):
        self.show_name = show_name
        self.episode_title = episode_title
        self.season_num = season_num
        self.episode_num = episode_num
        self.imdb_id = imdb_id
        self.air_date = air_date


class Season:
    def __init__(self, season_num):
        self.season_num = season_num
        self._episodes = dict()

    def get_episode(self, ep_num):
        episode = self._episodes.get(ep_num)

        if episode is not None:
            return episode
        else:
            print("No such episode - {:}".format(ep_num))
            return None

    def set_episode(self, episode):
        self._episodes[episode.episode_num] = episode

        
class Show:
    def __init__(self, tvdb_id):
        self._seasons = dict()

        soup = get_soup_for_series(tvdb_id)

        self.show_name = soup.find('Series').find('SeriesName').text
        self.imdb_id = soup.find('Series').find('IMDB_ID').text

        for ep in soup.find_all('Episode'):
            season_num = int(ep.find('SeasonNumber').text)
            ep_num = int(ep.find('EpisodeNumber').text)
            ep_title = ep.find('EpisodeName').text
            air_date = ep.find('FirstAired').text
            imdb_id = ep.find('IMDB_ID').text

            # If a season object does not exist, create one
            if season_num not in self._seasons:
                self.set_season(Season(season_num))

            # Set episode objects to corresponding season
            self.get_season(season_num) \
                .set_episode(Episode(self.show_name,
                                     ep_title,
                                     season_num,
                                     ep_num,
                                     imdb_id,
                                     air_date))
            
    def get_season(self, season_num):
        season = self._seasons.get(season_num)

        if season is not None:
            return season
        else:
            print("No such season - {:}".format(season_num))
            return None

    def set_season(self, season):
        self._seasons[season.season_num] = season

    def get_df(self):
        data = []
        for s in self._seasons:
            for e in self.get_season(s)._episodes:
                ep = self.get_season(s).get_episode(e)
                data.append({'season': ep.season_num,
                             'episode': ep.episode_num,
                             'title': ep.episode_title,
                             'airdate': ep.air_date})
        return DataFrame(data)

bob = Show(194031)

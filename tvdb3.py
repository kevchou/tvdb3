import re
import os
import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime
import sys, argparse
from xml.etree.ElementTree import parse

TVDB_URL = 'http://thetvdb.com/api/'

SEARCH_URL = 'GetSeries.php?seriesname={query}'

SERIES_INFO_URL = '/series/{id}/en.xml'
SERIES_EPISODES_URL = '/series/{id}/all/en.xml'

APIKEY = '15C9D64D3EFCC581'

# Video file extensions
exts = ('.mkv', '.mp4', '.avi')

# REGULAR EXPRESSIONS FOR FILE NAME SEARCHES
# Multi episode files, like 'S09E01 - E02"
multi_ep_regex = re.compile('([sS][0-9]+[eE][0-9]+.*[eE][0-9]+)|([0-9]+(x|\.)[0-9]+(x|\.)[0-9]+)')

# Looks for strings like "S09E01" or "9x01", "9.01"
single_ep_regex = re.compile('([sS][0-9]+.?[eE][0-9]+)|([0-9]+(x|\.)[0-9]+)')

# Regex for file extensions
video_ext_regex = re.compile('(\.mkv|\.avi|\.mp4)')

s_rgx = re.compile('[sS][0-9]+')
e_rgx = re.compile('[eE][0-9]+')
alt_rgx = re.compile('(x|\.)')


class Show(dict):
    def __init__(self, show_name):
        dict.__init__(self)
        self.show_name = show_name

    def __getitem__(self, season_num):
        if season_num in self:
            return dict.__getitem__(self, season_num)
        else:
            dict.__setitem__(self, season_num, Season(show_name=self.show_name,
                                                      season_num=season_num))
            return dict.__getitem__(self, season_num)

    def __str__(self):
        print("{name:s} - {num_seas:d} Seasons".format(name=self.show_name,
                                                       num_seas=len(self)))

    def get_next_air(self):
        all_eps = []

        for season in self.values():
            print(season)
            



[list(s.values()) for s in b.values()]
        
[ep for ep in b[3].values() if ep.air_date > datetime.now()]

        

class Season(dict):
    def __init__(self, show_name, season_num):
        dict.__init__(self)
        self.show_name = show_name
        self.season_num = season_num

    def __getitem__(self, episode_num):
        if episode_num in self:
            return dict.__getitem__(self, episode_num)
        else:
            dict.__setitem__(self, episode_num, Episode(episode_title=None,
                                                        season_num=None,
                                                        episode_num=None))
            return dict.__getitem__(self, episode_num)

    def __str__(self):
        print("List of episodes for season {:d}:\n".format(self.season_num) +
              "\n".join(self.get_episode_list()))

    def get_episode_list(self):
        return [str(ep.ep) + " - " + ep.title for ep in self.values()]


class Episode:
    def __init__(self, episode_title, season_num, episode_num, air_date=None):
        self.episode_title = episode_title
        self.season_num = season_num
        self.ep_num = episode_num
        self.air_date = air_date

    def __str__(self):
        print("S{season:02d}E{ep:02d} - {title:s}".format(season=self.season_num,
                                                          ep=self.ep_num,
                                                          title=self.episode_title))


def search(query):
    '''
    Searches tvdb for the input show name to find the correct series id.
    Inputs: show name string
    '''
    assert type(query) == str, "Input needs to be a string"
    
    results_array = []

    # Query TVDB for input show
    url = TVDB_URL + SEARCH_URL.format(query=query)
    url = url.replace(' ', '%20')
    
    request = urllib.request.urlopen(url)

    if request.code == 200:
        
        raw_xml = request.read()

        soup = BeautifulSoup(raw_xml, 'xml')
        
        results = soup.find_all('Series')
    
        for i, result in enumerate(results):
            show_name = result.find('SeriesName').text
            show_id = result.find('id').text

            results_array.append((i, show_name, show_id))

    return results_array


def get_show_info(series_id):
    url = TVDB_URL + APIKEY + SERIES_INFO_URL.format(id=series_id)

    request = urllib.request.urlopen(url)

    if request.code == 200:
        raw_xml = request.read()
        soup = BeautifulSoup(raw_xml, 'xml')

        show = soup.find('Series')

        show_name = show.find('SeriesName').text
        show_id = show.find('id').text

        print('{id} - {name}'.format(id=show_id, name=show_name))


def get_show_episodes(series_id):
    url = TVDB_URL + APIKEY + SERIES_EPISODES_URL.format(id=series_id)
    request = urllib.request.urlopen(url)

    if request.code == 200:

        raw_xml = request.read()
        soup = BeautifulSoup(raw_xml, 'xml')

        series = soup.find('Series')
        show_name = series.find('SeriesName').text

        show = Show(show_name)

        for ep in soup.find_all('Episode'):
            season_num = ep.find("SeasonNumber").text
            ep_num = ep.find("EpisodeNumber").text
            ep_name = ep.find("EpisodeName").text
            air_date = ep.find("FirstAired").text

            season_num = int(season_num)
            ep_num = int(ep_num)
            air_date = datetime.strptime(air_date, '%Y-%m-%d')

            show[season_num][ep_num] = Episode(ep_name,
                                               season_num,
                                               ep_num,
                                               air_date)
        return show



b = get_show_episodes(275557)


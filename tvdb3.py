import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime

import re
import os
import sys, argparse


# TVDB url constants
TVDB_URL = 'http://thetvdb.com/api/'

SEARCH_URL = 'GetSeries.php?seriesname={query}'

SERIES_INFO_URL = '/series/{id}/en.xml'
SERIES_EPISODES_URL = '/series/{id}/all/en.xml'

APIKEY = '15C9D64D3EFCC581'


# Video file extensions
exts = ('.mkv', '.mp4', '.avi')


# REGULAR EXPRESSIONS FOR FILE NAME SEARCHES
# Multi episode files, like 'S09E01 - E02"
# multi_ep_regex = re.compile('([sS][0-9]+[eE][0-9]+.*[eE][0-9]+)|([0-9]+(x|\.)[0-9]+(x|\.)[0-9]+)')

# # Looks for strings like "S09E01" or "9x01", "9.01"
# single_ep_regex = re.compile('([sS][0-9]+.?[eE][0-9]+)|([0-9]+(x|\.)[0-9]+)')

# # Regex for file extensions
# video_ext_regex = re.compile('(\.mkv|\.avi|\.mp4)')

# s_rgx = re.compile('[sS][0-9]+')
# e_rgx = re.compile('[eE][0-9]+')
# alt_rgx = re.compile('(x|\.)')


class Show(dict):
    """ A Show object that holds all the episodes of a show """

    def __init__(self, series_id):
        dict.__init__(self)

        # Query tvdb and return a BeautifulSoup object
        soup = self.get_tvdb_soup(series_id)

        self.show_name = soup.find('Series').find('SeriesName').text

        for ep in soup.find_all('Episode'):
            
            season_num = int(ep.find("SeasonNumber").text)
            ep_num     = int(ep.find("EpisodeNumber").text)
            ep_name    = ep.find("EpisodeName").text
            air_date   = ep.find("FirstAired").text

            if season_num not in self:
                self[season_num] = Season(show_name = self.show_name,
                                          season_num = season_num)

            self[season_num][ep_num] = Episode(episode_title=ep_name,
                                               season_num=season_num,
                                               episode_num=ep_num,
                                               air_date=air_date)
            
    def __getitem__(self, season_num):
        if season_num in self:
            return dict.__getitem__(self, season_num)
        else:
            dict.__setitem__(self, season_num, Season(show_name=self.show_name,
                                                      season_num=season_num))
            return dict.__getitem__(self, season_num)

    def __repr__(self):
        return "{name:s} - {num_seas:d} Seasons".format(name=self.show_name,
                                                        num_seas=len(self))

    def print_next_air(self):
        """ Finds unaired episodes and prints them """
        not_aired = []

        for season in self.values():
            for episode in season.values():
                try:
                    d = datetime.strptime(episode.air_date, "%Y-%m-%d")
                    if d > datetime.now():
                        not_aired.append(episode)
                        
                except ValueError:
                    # air_date must not be of format 'YYYY-MM-DD'
                    pass
                    

        for ep in not_aired:
            print('{a} {n}'.format(a=ep.air_date, n=ep))

            
    def get_tvdb_soup(self, series_id):
        """ Reads xml file from tvdb and turns it into a BeautifulSoup object """
        
        url = TVDB_URL + APIKEY + SERIES_EPISODES_URL.format(id=series_id)
        request = urllib.request.urlopen(url)

        if request.code == 200:
            
            raw_xml = request.read()
            soup = BeautifulSoup(raw_xml, 'xml')
            
            return soup
        

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
        return("Season {:d}:\n".format(self.season_num) +
              "\n".join(self.get_episode_list()))

    def get_episode_list(self):
        return ["{num} - {title}".format(num=ep.ep_num, title=ep.episode_title)
                for ep in self.values()]

                
class Episode:
    
    def __init__(self, episode_title, season_num, episode_num, air_date=None):
        self.episode_title = episode_title
        self.season_num = season_num
        self.ep_num = episode_num
        self.air_date = air_date

    def __str__(self):
        return "S{season:02d}E{ep:02d} - {title:s}".format(season=self.season_num,
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



b = 275557
s = 79169

s = search('seinfeld')

seinfeld = Show(s)
broad = Show(b)
bob = Show(194031)

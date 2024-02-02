
import os
import pandas as pd
from typing import List 
from typing import Dict
from bs4 import BeautifulSoup
import requests
import json
import logging

# from showcase.utils.playlist_helper import get_track_ids_from_track_list
from constants import SCOPE, SPOTIPY_REDIRECT_URI#, MIN_TRACKS, MIN_SIMILARITY, venues_to_include
from config import VENUES
from spotify_connector import SpotifyConnector
from spotipy.oauth2 import SpotifyOauthError
from spotify_playlist import SpotifyPlaylist
from utils.show_name_parser import ShowNameParser

spotipy_local_pl_id = os.getenv('LOCAL_PL_ID')
spotipy_client_id = os.getenv('SPOTIPY_CLIENT_ID')
spotipy_client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')


class Showcase:

    def scrape_venues(self,venues: List[str])->List[str]:
        """
        Pull artist names from event pages of select venues

        Inputs:
        -------
        venues : List[str]
            List of venues

        Outputs:
        --------
        artists : List[str]
            List of artist names
        show_info_dict : Dict
            Dictionary containing show information
        """
        show_info_list = []
        for venue in venues:
            try:
                show_info_list += self._scrape_venue(venue)
            except TypeError as e:
                msg = f"Error scraping {venue}. None returned."
                logging.warning(msg)
                pass

        return show_info_list
    
    def _scrape_venue(self, venue: str)->List[str]:
        """
        Pull artist names from event page

        Inputs:
        --------
        venue : str
            Venue name, should correspond to a config file
        
        Outputs:
        --------
        artists : List[str]
            List of artist names
        show_info_dict : Dict
            Dictionary containing show information
        """

        fpath = f"spotify_local_shows/venues/{venue}_config.json"
        with open(fpath, 'r') as j:
            venue_dict = json.loads(j.read())
        page = requests.get(venue_dict["webpage_url"])
        soup = BeautifulSoup(page.content, "html.parser")
        shows_container = soup.find('div', class_=venue_dict["show_container"])
        show_info_list = []
        for iter in venue_dict["iters"].values():
            
            for show in shows_container.find_all('div', class_=iter["iter_name"]):
                show_dict = {}
                for kw,item in iter["items"].items():
                    if "sub_index" not in item.keys():
                        show_dict.update({kw:show.find("div", class_=item["loc"]).text})
                    else: 
                        show_dict.update({kw:show.find_all("div", class_=item["loc"])[item["sub_index"]].text})
                show_dict.update({"venue":venue_dict["venue_name"]})
                show_info_list.append(show_dict)
        return show_info_list
    
    def save_to_csv(self, show_info_list:List[Dict], fpath:str, attrs_to_print:List[str] = ['artist_name', 'show_date', 'venue']):
        """
        Save show info to csv

        Inputs:
        -------
        show_info_list : List[Dict]
            List of dictionaries containing show info
        fpath : str
            File path to save to
        """
        # with open(fpath, 'w') as f:
        #     f.write("artist_name,show_date,venue\n")
        #     for show in show_info_list:
        #         f.write(f"{show['artist_name']}\n")

        # for now convert to pandas df for easy filtering/ordering
        df = pd.DataFrame(show_info_list)
        if 'show_date' in df.columns:
            df['show_date'] = pd.to_datetime(df['show_date'])
        df.to_csv(fpath, index=False)

    def parse_show_name(self, show_info_list, parser):
        """
        Parse show name into individual band names

        Inputs:
        --------
        show_name : str
            Name of show

        Outputs:
        --------
        artists : List[str]
            List of artist names
        """
        artist_info_list = []
        for show in show_info_list:
            artist_info_list += parser.parse_show_name(show)
        return artist_info_list

    def get_all_artist_ids(self, artist_info_list):
        artist_ids = [artist['artist_uuid'] for artist in artist_info_list]

        return artist_ids
    
    ## May need to implement later
    # def _str_date_to_datetime(self, date_str:str)->pd.Timestamp:
    #     """
    #     Convert date string to datetime

    #     Inputs:
    #     -------
    #     date_str : str
    #         Date string

    #     Outputs:
    #     --------
    #     date : pd.Timestamp
    #         Timestamp
    #     """
    #     return pd.to_datetime(date_str)
        


def handle():
    try:
        sp = SpotifyConnector(spotipy_client_id=spotipy_client_id,
                        spotipy_client_secret=spotipy_client_secret,
                        spotipy_redirect_uri=SPOTIPY_REDIRECT_URI,
                        scope=SCOPE)
    except SpotifyOauthError:
        sp = None
    showcase = Showcase()
    show_info_list = showcase.scrape_venues(['horseshoe_tavern'])
    showcase.save_to_csv(show_info_list, 'show_info.csv')

    parser = ShowNameParser(sp)
  
    artist_info_list = showcase.parse_show_name(show_info_list, parser)
    artist_ids = showcase.get_all_artist_ids(artist_info_list)
    playlist = SpotifyPlaylist(sp=sp, playlist_id=spotipy_local_pl_id)
    playlist.add_top_tracks_from_artist_id_list(artist_ids)



if __name__== "__main__":
    handle()
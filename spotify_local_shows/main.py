
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

SPOTIPY_LOCAL_PL_ID = os.getenv('LOCAL_PL_ID')
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
        # print(shows_container)
        for iter in venue_dict["iters"].values():
            
            for show in shows_container.find_all('div', class_=iter["iter_name"]):
                show_dict = {}
                print(show)
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
        print(df.head())
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
        

    # def add_top_n_from_all_artists(self, artists:List[str])->List:
    #     """
    #     Add top tracks from each artist to the playlist

    #     Inputs:
    #     -------
    #     artists : List[str]
    #         List of artists

    #     """
    #     top_n_track_ids = []
    #     for artist in artists:
    #         top_n_track_ids += self._add_artist_top5(artist)
    #     self.sp.client.playlist_replace_items(SPOTIPY_LOCAL_PL_ID, top_n_track_ids[:100]) # can only add 100 at a time - need to fix this

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
    print(len(show_info_list))
    # showcase.save_to_csv(show_info_list, 'show_info.csv')

    parser = ShowNameParser(sp)
    artist_info_list = showcase.parse_show_name(show_info_list, parser)
    print(artist_info_list)
    # for artist in artists:
    #     print(parser.parse_show_name(artist))
    # name = 'Talon with Stankonya & The Hogtown Rebels'
    # a = parser.split_show_name(name)
    # print(a)
    # results=sp.client.search(q="artist:Sam", type='artist')
    # print(results)

    # with open('sam_results.pkl', 'wb') as fn:
    #     pickle.dump(results, fn)
    # sp = None
    # print(sp)
    # playlist_adder = LocalArtistPlaylist(sp)
    # playlist_adder.scrape_venues(venues=venues_to_include)
    # artists = ['status / non-status', 'langhorne slim ', 'billy woods  - aethiopes tour 2022', 'nu music night', 'devin cuddy band & villages', ' housewife', 'tommy youngsteen perform fleetwood mac rumours', " north america's tribute to oasis", 'zach oliver', 'alessandro montelli', 'christine jackson', " the chills' soft bomb 30th anniversary tour ", 'craig finn & the uptown controllers', ' tropical fuck storm ', 'wine lips', 'priors', 'the f***ing astronauts', 'born in the gta', 'fleece', ' amanda shires ', 'julie title ', 'illuminati hotties', 'mariel buckley', 'black joe lewis & cedric burnside', 'the creepshow', 'weld', ' organ thieves', 'espanola', ' buff justice', 'percocet blonde', 'absolute color', ' chew bear', 'lupo', 'mellon collie caravan', 'ivey gardens', 'palm', ' battle of the bands', 'limblifter', 'mick flannery', ' cudbear', 'paper saw', 'samantha aucoin', ' sons of the east ', 'kylie fox', ' brooklyn doran', 'lea holtom', 'the dictators', ' night finger & gene champagne & the un-teens', ' bartees strange', 'the surfrajettes', 'prancer', 'mbg ', 'david cross', 'drugdealer', ' campchella 2022', 'daniel james mcfadyen', 'wayley & mikalyn', 'hanorah', 'your hunni', 'heavy head ', " gloin 'we found this' record release show", 'brian walker’s 16th jam', ' a past president', 'rheostatics', 'the strumbellas', ' nikki lane ', '54.40 ', ' jeff rosenstock & laura stevenson', 'the sadies', 'david wilcox', 'lisa leblanc']
    # playlist_adder.add_top5_from_all_artists(artists)
    # print('here')

if __name__== "__main__":
    handle()
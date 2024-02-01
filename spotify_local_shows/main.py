
import os
from typing import List 
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
        artists = []
        for venue in venues:
            try:
                artists += self._scrape_venue(venue)
            except TypeError as e:
                msg = f"Error scraping {venue}. None returned."
                logging.warning(msg)
                pass

        return artists
    
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
        shows_list = []
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

                shows_list.append(show_dict)
        print(shows_list)

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
    showcase._scrape_venue('horseshoe_tavern')
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
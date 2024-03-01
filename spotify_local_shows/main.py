
import os
import pandas as pd
from typing import List 
from typing import Dict
from datetime import datetime
import dateutil
import logging
logging.getLogger().setLevel(logging.INFO)


from constants import SCOPE, SPOTIPY_REDIRECT_URI
from config import VENUES, start_date, end_date, MIN_TRACKS
from spotify_connector import SpotifyConnector
from spotipy.oauth2 import SpotifyOauthError
from spotify_playlist import SpotifyPlaylist
from show_name_parser import ShowNameParser
from event_scraper import EventScraper

spotipy_local_pl_id = os.getenv('LOCAL_PL_ID')
spotipy_client_id = os.getenv('SPOTIPY_CLIENT_ID')
spotipy_client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')


 
def save_to_csv(show_info_list:List[Dict], fpath:str, attrs_to_print:List[str] = ['artist_name', 'show_date', 'venue']):
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
    msg = f"Saving show list to {fpath}"
    logging.info(msg)
    if 'show_date' in df.columns:
        df['show_date'] = pd.to_datetime(df['show_date'])
    df.to_csv(fpath, index=False)

def parse_show_name(show_info_list, parser):
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

def get_all_artist_ids(artist_info_list):
    artist_ids = [artist['artist_uuid'] for artist in artist_info_list]

    return artist_ids
def convert_datetime(show_info_list):
    def add_show_datetime(show):
        try:
            show_date = dateutil.parser.parse(show['show_date_str']).date()
        except dateutil.parser._parser.ParserError:
            show_date = None
        
        show.update({'show_date':show_date})
    [add_show_datetime(show) for show in show_info_list]
        
def filter_show_by_date(show_info_list, start_date=None, end_date=None):
    """
    Filter show info by date

    Inputs:
    -------
    show_info_list : List[Dict]
        List of dictionaries containing show info
    start_date : str
        Start date
    end_date : str
        End date

    Outputs:
    --------
    filtered_show_info_list : List[Dict]
        List of dictionaries containing show info
    """

    if end_date is None and start_date is None:
        return show_info_list
    
    start_date = start_date or datetime.now().date()
    show_info_list = [show for show in show_info_list if show['show_date'] is not None]
    show_info_list = [show for show in show_info_list if show['show_date'] >= start_date]
    if end_date is None:
        return show_info_list
    show_info_list = [show for show in show_info_list if show['show_date'] <= end_date]
    return show_info_list

def handle():
    # Establish connection to Spotify through Spotipy
    try:
        sp = SpotifyConnector(spotipy_client_id=spotipy_client_id,
                        spotipy_client_secret=spotipy_client_secret,
                        spotipy_redirect_uri=SPOTIPY_REDIRECT_URI,
                        scope=SCOPE)
        msg = "Spotify connection successful"
        logging.info(msg)
    except SpotifyOauthError:
        sp = None
        msg = "Spotify connection failed. Saving events locally to csv only"
        logging.info(msg)

    # Scrape event pages for show info  
    event_scraper = EventScraper()
    show_info_list = event_scraper.scrape_venues(venues=VENUES)
    # show_info_list = [{'show_name': 'Boeckner (Dan Boeckner of Wolf Parade, Handsome Furs)', 'show_date_str': 'Friday, June 7, 2024', 'venue': 'horseshoe_tavern'}, {'show_name': 'Reverend Horton Heat with The Surfrajettes', 'show_date_str': 'Saturday, June 15, 2024', 'venue': 'horseshoe_tavern'}, {'show_name': 'The Life & Music of Johnny Cash', 'show_date_str': 'Sunday, June 16, 2024', 'venue': 'horseshoe_tavern'}, {'show_name': 'MRG Live presents  Mo Lowda & The Humble', 'show_date_str': 'Thursday, June 20, 2024', 'venue': 'horseshoe_tavern'}, {'show_name': 'Oliver Hazard', 'show_date_str': 'Wednesday, October 16, 2024', 'venue': 'horseshoe_tavern'}]
    convert_datetime(show_info_list)
    show_info_list = filter_show_by_date(show_info_list, start_date=start_date, end_date=end_date)
    save_to_csv(show_info_list, 'show_info.csv')

    # Parse show names into artist names
    parser = ShowNameParser(sp)
    artist_info_list = []
    for show in show_info_list:
        artist_info_list += parser.parse_show_name(show)
    
    # Get artist ids
    artist_ids = get_all_artist_ids(artist_info_list)

    # Add top tracks from each artist to the playlist
    playlist = SpotifyPlaylist(sp=sp, playlist_id=spotipy_local_pl_id)
    playlist.add_top_tracks_from_artist_id_list(artist_ids, num_top_tracks = MIN_TRACKS)



if __name__== "__main__":
    handle()
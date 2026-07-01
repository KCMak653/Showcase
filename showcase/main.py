
import os
import pandas as pd
from typing import List 
from typing import Dict
from datetime import datetime
import dateutil
import logging
logging.getLogger().setLevel(logging.INFO)


from constants import SCOPE
from config import VENUES, start_date, end_date, MIN_TRACKS
from spotify_connector import SpotifyConnector
from spotipy.oauth2 import SpotifyOauthError
from spotify_playlist import SpotifyPlaylist
from show_name_parser import ShowNameParser
from event_scraper.event_scraper import EventScraper
from llm_io.providers import OpenAIModelIO
from event_filter.event_filter import EventFilter
from show_formatter.show_formatter import ShowFormatter
from spotify_io.spotify_io import SpotifyIO
from playlist_creator.playlist_creator import PlaylistCreator


def handle():
    before_filter = datetime(2026, 2, 28)
    after_filter = datetime(2026, 3,14)
    venue_name = "Horseshoe Tavern"
    model_name = "gpt-4.1-mini"
    model_io = OpenAIModelIO(model_name)
    sp_io = SpotifyIO()
    event_scraper = EventScraper(model_io, debug=True, debug_file_path="event_scraper/debug_event.yaml")
    urls = ["https://www.horseshoetavern.com/events", "https://www.leespalace.com/events", "https://www.themonarchtavern.com/home", "http://thebabyg.com/"]
    events = event_scraper.scrape_events_from_webpage_urls(urls)
    filtered_events = EventFilter.filter_events_data(events, after_timestamp = after_filter, before_timestamp=before_filter) 
    print("\n\n\nfiltered_events\n\n\n", filtered_events)
    show_formatter = ShowFormatter(model_io, sp_io)
    shows = show_formatter.format_shows(filtered_events)
    print("\n\n\nshows\n\n\n", shows)
    [print(show) for show in shows]
    playlist_creator = PlaylistCreator(sp_io)
    playlist_creator.create_playlist(shows, after_timestamp=after_filter, before_timestamp=before_filter, show_order_select="headliner", num_tracks=2)





if __name__== "__main__":
    handle()
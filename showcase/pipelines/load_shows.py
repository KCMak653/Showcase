import logging
import os

from showcase.event_scraper import EventScraper
from showcase.llm_io.factory import create_model_io
from showcase.settings import load_env
from showcase.show_formatter.show_formatter import ShowFormatter
from showcase.spotify_io.spotify_io import SpotifyIO
from showcase.db_io.storage_backends.supabase_db_io import SupabaseDBIO
from showcase.pipelines.constants.venues import VENUES_TEST

logging.getLogger().setLevel(logging.INFO)


def handle():
    load_env()
    dev_mode = os.environ.get("ENV")
    model_io = create_model_io()
    sp_io = SpotifyIO()
    db_io = SupabaseDBIO(table = "toronto_shows", primary_key="id")
    event_scraper = EventScraper(model_io, debug=True)
    # urls = [
    #     "https://www.horseshoetavern.com/events",
    #     # "https://www.leespalace.com/events",
    #     # "https://www.themonarchtavern.com/home",
    #     # "http://thebabyg.com/",
    # ]
    events = event_scraper.scrape_events_from_webpage_urls(VENUES_TEST)
    show_formatter = ShowFormatter(model_io, sp_io)
    shows = show_formatter.format_shows(events)
    show_list = [show.as_dict() for show in shows]
    print("\n\n\nshows\n\n\n", show_list)
    # show_list = [{'artist_uri': 'spotify:artist:7cETzIYBVYBvs8oJG1wywk', 'band_name': 'The Messenger Birds', 'show_time': '2026-11-21T20:00:00', 'venue': 'Horseshoe Tavern', 'order': 'HEADLINER'}, 
    #              {'artist_uri': 'spotify:artist:4IEpQR24sUgq6BQw2MdZIy', 'band_name': 'GHOSTWOMAN', 'show_time': '2026-11-27T19:00:00', 'venue': 'Horseshoe Tavern', 'order': 'HEADLINER'}]
    db_io.replace_table(show_list)
    




if __name__ == "__main__":
    handle()

import logging
from datetime import datetime, timedelta

from showcase.event_filter.event_filter import EventFilter
from showcase.event_scraper import EventScraper
from showcase.llm_io.factory import create_model_io
from showcase.playlist_creator.playlist_creator import PlaylistCreator
from showcase.settings import load_env
from showcase.show_formatter.show_formatter import ShowFormatter
from showcase.pipelines.constants.venues import VENUES
from showcase.spotify_io.spotify_io import SpotifyIO

logging.getLogger().setLevel(logging.INFO)

DEFAULT_VENUES = {
    "Horseshoe Tavern": VENUES["Horseshoe Tavern"],
    "Lee's Palace": VENUES["Lee's Palace"],
    "The Monarch Tavern": VENUES["The Monarch Tavern"],
    "The Baby G": VENUES["The Baby G"],
}


def handle():
    load_env()
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    before_filter = today
    after_filter = today + timedelta(days=30)
    model_io = create_model_io()
    sp_io = SpotifyIO()
    event_scraper = EventScraper(model_io, debug=True)
    events = event_scraper.scrape_events_from_webpage_urls(DEFAULT_VENUES)
    filtered_events = EventFilter.filter_events_data(
        events,
        after_timestamp=after_filter,
        before_timestamp=before_filter,
    )
    print("\n\n\nfiltered_events\n\n\n", filtered_events)
    show_formatter = ShowFormatter(model_io, sp_io)
    shows = show_formatter.format_shows(filtered_events)
    print("\n\n\nshows\n\n\n", shows)
    for show in shows:
        print(show)
    playlist_creator = PlaylistCreator(sp_io)
    playlist_creator.create_playlist(
        shows,
        after_timestamp=after_filter,
        before_timestamp=before_filter,
        show_order_select="headliner",
        num_tracks=2,
    )


if __name__ == "__main__":
    handle()

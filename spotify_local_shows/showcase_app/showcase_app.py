from typing import List

from spotify_local_shows.llm_io.model_io import ModelIO
from spotify_local_shows.llm_io.providers import OpenAIModelIO
from spotify_local_shows.data.event import Event
from spotify_local_shows.event_scraper import EventScraper

class ShowcaseApp:
    def __init__(self, model_name: str):
        # Create model
        self.model_io = OpenAIModelIO(model_name)


    def create_playlist(self, event_list_urls: List[str]):
        
        event_scraper = EventScraper(self.model_io)
        events : List[Event] = []
        for event_list_url in event_list_urls:
            events.append(event_scraper.scrape_url(event_list_url))



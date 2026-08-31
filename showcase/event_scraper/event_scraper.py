import logging
from pathlib import Path
from typing import Any, Dict, List

from bs4 import BeautifulSoup
import requests
import yaml

from showcase.llm_io.model_io import ModelIO

logger = logging.getLogger(__name__)

_EVENT_SCRAPER_DIR = Path(__file__).resolve().parent


class EventScraper:

    EXAMPLE_EVENT_LIST = (_EVENT_SCRAPER_DIR / "example_event_list.yaml").read_text()
    PROMPT = f""" 
        You are a helpful assistant that extracts event information of live music shows from event webpage html into a yaml file.
        Return in text the .yaml file for inspection

        There may be other events interwoven with the live music events i.e Taco Tuesday, Karaoke, Trivia, Dance Party nights. Do your best to omit events that are obviously not live music.

        An event is made up of one or more bands playing. Each show will list the bands names playing and an event_timestamp for the event.

        Requirements: 
        - Use only the keys provided in the default example_event_list.yaml file. Do not create your own keys
        - The 'event_timestamp' value must be in "YYYY-MM-DDTHH:MM:SS" ISO 8601 format.
        - Output must be in yaml.
        - Values must be specified for keys marked @Required
        - Maintain the band names as is, do not parse out, format or change order
        - IMPORTANT: Use only standard double quotes (") for string values, not smart quotes or backticks
        - Do not wrap the output in markdown code blocks or backticks
        - Return only the raw configuration content

        default.yaml file:

        {EXAMPLE_EVENT_LIST}

"""
    def __init__(self, model_io: ModelIO, debug: bool = False, debug_file_prefix: str = "", num_retries: int=2, run_id: int=0):
        self.model_io = model_io
        self.debug = debug
        self.debug_file_prefix = debug_file_prefix or str(_EVENT_SCRAPER_DIR / "debug_event")
        self.num_retries = num_retries
        self.run_id = run_id

    def scrape_events_from_webpage_urls(self, event_list_urls : Dict[str,str]) -> List[dict]:
        result = {}
        if event_list_urls:
            for venue, event_list_url in event_list_urls.items():
                result[venue] = self.scrape_event_list(event_list_url=event_list_url, venue = venue)
        return self.hydrate_events_with_venue(result)


    def scrape_event_list(self, event_list_url: str, venue: str):
        # Scrape all webpage data, send to LLM which will parse out the event names
        events = {}
        if event_list_url is not None:
            logging.info(f"Scraping venue - {venue} - with url: {event_list_url}")
            scraped_url = self.scrape_url(event_list_url)
            if scraped_url is not None:
                response = self.model_io.get_response(event_list_url+str(scraped_url), self.PROMPT)
                if self.debug:
                    self.write_yaml_to_file(
                        response,
                        f"{self.debug_file_prefix}_{venue}.yaml",
                    )
                try:
                    parsed = yaml.safe_load(response)
                    # Return inner events dict so structure is { event_1: {}, event_2: {} }, not { events: { ... } }
                    events = parsed.get("events", parsed) if isinstance(parsed, dict) else {}
                except yaml.YAMLError as e:
                    logger.error(f"Could not create dict for {venue} using yaml.safe_load()")
                    return {}
                    # errs = True
                    # warnings = [f"Could not create dict using yaml.safe_load(), reconstruct response to be in yaml format: {e}"] 

        return events

    @staticmethod
    def hydrate_events_with_venue(events_by_venue: Dict[str, Dict[str, Any]]) -> List[dict]:
        """Flatten { url: { event_1: {}, event_2: {} } } to a list of event dicts."""
        out = []
        for venue, url_events in events_by_venue.items():
            if isinstance(url_events, dict):
                for event in url_events.values():
                    if event and isinstance(event, dict):
                        event["venue"] = venue
                        out.append(event)
        return out

    def scrape_url(self, url):
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        return soup

    
    def write_yaml_to_file(self, config_string, file_path='events.yaml'):
        """
        Write a YAML configuration string directly to a file. For debugging mode only.
        
        Args:
            config_string (str): The YAML configuration string
            file_path (str): Path to the output file
        """
        # Clean up the config string - remove markdown code blocks and normalize quotes
        # cleaned_config = self.clean_config_string(config_string)
        cleaned_config = config_string
        with open(file_path, 'w') as f:
            f.write(cleaned_config)
        
 
    
if __name__ == "__main__":
    from showcase.llm_io.providers import OpenAIModelIO
    from showcase.settings import load_env

    load_env()
    print("Testing EventScraper with YAML output...")

    model_name = "gpt-4.1"
    model_io = OpenAIModelIO(model_name)
    event_scraper = EventScraper(model_io, debug=True)
    urls = {
        "Horseshoe Tavern": "https://www.horseshoetavern.com/events",
    }
    event_scraper.scrape_events_from_webpage_urls(urls)

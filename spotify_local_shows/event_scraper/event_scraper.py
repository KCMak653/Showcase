import logging
from typing import Any, Dict, List

from bs4 import BeautifulSoup
import requests
import yaml

from llm_io.model_io import ModelIO
import logging

logger = logging.getLogger(__name__)


class EventScraper:

    EXAMPLE_EVENT_LIST = open("event_scraper/example_event_list.yaml", "r").read()
    PROMPT = f""" 
        You are a helpful assistant that extracts event information of live music shows from event webpage html into a yaml file.
        Return in text the .yaml file for inspection

        An event is made up of one or more bands playing. Each show will list the bands names playing and an event_timestamp for the event.

        The venue name should be present in the html or the url of the webpage.

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
    def __init__(self, model_io : ModelIO, debug: bool = False, debug_file_path = "", num_retries=2):
        self.model_io = model_io
        self.debug = debug
        self.debug_file_path = debug_file_path
        self.num_retries = num_retries

    def scrape_events_from_webpage_urls(self, event_list_urls : List[str]) -> List[dict]:
        result = {}
        if event_list_urls:
            for event_list_url in event_list_urls:
                result[event_list_url] = self.scrape_event_list(event_list_url=event_list_url)
        return self.flatten_events_dict(result)


    def scrape_event_list(self, event_list_url: str):
        # Scrape all webpage data, send to LLM which will parse out the event names
        if event_list_url is not None:
            logging.info(f"Scraping url: {event_list_url}")
            scraped_url = self.scrape_url(event_list_url)
            if scraped_url is not None:
                response = self.model_io.get_response(event_list_url+str(scraped_url), self.PROMPT)
                if self.debug:
                    self.write_yaml_to_file(response, self.debug_file_path)
                try:
                    parsed = yaml.safe_load(response)
                    # Return inner events dict so structure is { event_1: {}, event_2: {} }, not { events: { ... } }
                    events = parsed.get("events", parsed) if isinstance(parsed, dict) else {}
                except yaml.YAMLError as e:
                    logger.error("Could not create dict using yaml.safe_load()")
                    return {}
                    # errs = True
                    # warnings = [f"Could not create dict using yaml.safe_load(), reconstruct response to be in yaml format: {e}"] 

        print(events)
        return events

    @staticmethod
    def flatten_events_dict(events_by_url: Dict[str, Dict[str, Any]]) -> List[dict]:
        """Flatten { url: { event_1: {}, event_2: {} } } to a list of event dicts."""
        out = []
        for url_events in events_by_url.values():
            if isinstance(url_events, dict):
                for event in url_events.values():
                    if isinstance(event, dict) and event:
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
    print("Testing EventScraper with YAML output...")
    
    model_name = "gpt-4.1"
    model_io = OpenAIModelIO(model_name)
    event_scraper = EventScraper(model_io, debug=True, debug_file_path="event_scraper/debug_event.yaml")
    url = "https://www.horseshoetavern.com/events"
    event_scraper.scrape_events_from_webpage_urls([url])

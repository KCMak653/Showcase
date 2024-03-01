import logging
from typing import List

from bs4 import BeautifulSoup
import requests
import json
import pandas as pd

from utils.event_scraper_helper import extract_shows



class EventScraper:

    def scrape_venue(self, venue: str):

        fpath = f"spotify_local_shows/venues/{venue}_config.json"
        try: 
            with open(fpath, 'r') as j:
                venue_dict = json.loads(j.read())
            
            msg = f"Scraping {venue_dict['venue_name']} event page.."
            logging.info(msg)
            
            page = requests.get(venue_dict["webpage_url"])
            soup = BeautifulSoup(page.content, "html.parser")
        except FileNotFoundError as e:
            msg = f"Error scraping {venue}. Config file not found."
            logging.warning(msg)
            soup = None


        return soup
    
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
                soup = self.scrape_venue(venue)
                if soup is not None:
                    show_info_list += extract_shows(soup, venue)
            except TypeError as e:
                msg = f"Error scraping {venue}. None returned."
                logging.warning(msg, e)
                pass

        return show_info_list
 
    
if __name__ == "__main__":
    scraper = EventScraper()
    venues = ["dakota_tavern", "abc", "horseshoe_tavern"]
    show_info_list = scraper.scrape_venues(venues)
    print(show_info_list)

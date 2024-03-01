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
    
    # def _scrape_venue(self, venue: str)->List[str]:
    #     """
    #     Pull artist names from event page

    #     Inputs:
    #     --------
    #     venue : str
    #         Venue name, should correspond to a config file
        
    #     Outputs:
    #     --------
    #     artists : List[str]
    #         List of artist names
    #     show_info_dict : Dict
    #         Dictionary containing show information
    #     """

    #     fpath = f"spotify_local_shows/venues/{venue}_config.json"
    #     with open(fpath, 'r') as j:
    #         venue_dict = json.loads(j.read())
        
    #     msg = f"Scraping {venue_dict['venue_name']} event page.."
    #     logging.info(msg)
        
    #     page = requests.get(venue_dict["webpage_url"])
    #     soup = BeautifulSoup(page.content, "html.parser")
    #     # print(soup.prettify())
    #     xs = soup.find_all('a')
    #     for x in xs:
    #         c=x.find('h3', class_='portfolio-title')
    #         if c is not None and c['class']==['portfolio-title']: 
    #             print(c.get_text())
    #     klsd
    #     # print(soup.get_text())
    #     shows_container = soup.find('div', class_=venue_dict["show_container"])
    #     # print(shows_container)
    #     show_info_list = []
    #     for iter in venue_dict["iters"].values():
            
    #         for show in shows_container.find_all('div', class_=iter["iter_name"]):
    #             show_dict = {}
    #             for kw,item in iter["items"].items():
    #                 if "sub_index" not in item.keys():
    #                     show_dict.update({kw:show.find("div", class_=item["loc"]).text})
    #                 else: 
    #                     show_dict.update({kw:show.find_all("div", class_=item["loc"])[item["sub_index"]].text})
    #             show_dict.update({"venue":venue_dict["venue_name"]})
    #             show_dict['show_date'] = pd.to_datetime(show_dict['show_date']).date()
    #             show_info_list.append(show_dict)
    #     msg = f"Finished scraping {venue_dict['venue_name']} event page."
    #     logging.info(msg)
    #     return show_info_list
    
    
if __name__ == "__main__":
    scraper = EventScraper()
    venues = ["dakota_tavern", "abc", "horseshoe_tavern"]
    show_info_list = scraper.scrape_venues(venues)
    print(show_info_list)

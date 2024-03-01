## Event page specific scraping code 

##  - Would love to generalize someday - maybe use LLM to generate,
## right now event page structure is just too disparate

## Add your event venue code in here

# Each function takes in soupified html code and returns a list of dicts with show_name and show_date

import re
from bs4 import BeautifulSoup
import requests
import json
import logging

def extract_shows(soup, venue: str):
    show_dict = {}
    if venue == 'horseshoe_tavern':
        show_dict = _extract_shows_horseshoe_tavern(soup)
    elif venue == 'dakota_tavern':
        show_dict = _extract_shows_dakota_tavern(soup)
    elif venue == 'lees_palace':
        show_dict = _extract_shows_lees_palace(soup)

    return show_dict

def _extract_shows_lees_palace(soup):
    shows_container = find_show_data(soup, attrs={'name':'div', 'class_':"schedule-event heaa"})
    shows = []
    for show_container in shows_container:
        # Skip Dance Cave events
        show_data = find_show_data(show_container, attrs={'name':'div', 'class_':'schedule-event-time tp'})
        if any(['Dance Cave' in x for x in show_data]):
            continue
        show_dict = {}
        show_dict['show_name'] = find_show_data(show_container, attrs={'name':'div', 'class_':'schedule-speaker-name aa'}, first=True).get_text()
        show_dict['show_date_str'] = find_show_data(show_container, attrs={'name':'div', 'class_':'schedule-event-time tp'}, first=True).get_text()
        if show_dict is not None:
            show_dict['venue'] = 'lees_palace'
        shows.append(show_dict)
    return shows

def _extract_shows_horseshoe_tavern(soup):
    shows_container = find_show_data(soup, attrs={'name':'div', 'class_':'schedule np w-dyn-list'}, first=True)
    shows_container = find_show_data(shows_container, attrs={'name':'div', 'class_':"w-dyn-item"})
    shows =[]
    for show_container in shows_container:
        show_dict = {}
        show_dict['show_name'] = find_show_data(show_container, attrs = {'name':'div', 'class_':"schedule-speaker-name aa"}, first=True).get_text()
        show_dict['show_date_str'] = find_show_data(show_container, attrs = {'name':"div", 'class_':"schedule-event-time tp"})[0].get_text()
        if show_dict is not None:
            show_dict['venue'] = 'horseshoe_tavern'
        shows.append(show_dict)
    return shows

def _extract_shows_dakota_tavern(soup):
    show_containers = find_show_data(soup, attrs={'name':'a'})
    shows = []
    for show_container in show_containers:
        show_data = find_show_data(show_container, attrs={'name':'h3', 'class_':['portfolio-title']}, first=True)
        if show_data is None or show_data.get('class') != ['portfolio-title']:
            continue 
        pattern = r'^(.*)-(.*)$'
        show_dict = regex_show_data(show_data.get_text(), pattern)
        if show_dict:
            show_dict['venue'] = 'dakota_tavern'
            shows.append(show_dict)
    return shows

def find_show_data(soup, attrs = None, first = False):
    attrs = attrs or {}
    if first: 
        match = soup.find(**attrs)
    else:
        match = soup.find_all(**attrs)
        match = match or None
    return match 


def regex_show_data(show_data, pattern, items =['show_date_str', 'show_name']):
    match = re.search(pattern, show_data)
    if match is not None and len(match.groups()) == len(items):
        show_dict = {item: match.group(i+1).strip() for i, item in enumerate(items)}
        return show_dict

if __name__== "__main__":
    venue = 'lees_palace'
    fpath = f"spotify_local_shows/venues/{venue}_config.json"
    with open(fpath, 'r') as j:
        venue_dict = json.loads(j.read())
    
    msg = f"Scraping {venue_dict['venue_name']} event page.."
    logging.info(msg)
    
    page = requests.get(venue_dict["webpage_url"])
    soup = BeautifulSoup(page.content, "html.parser")

    shows = _extract_shows_lees_palace(soup)
    print(shows)


# Showcase

Glossary: 
show - singular band performance
event - can contain one or multiple shows i.e openers + headliner

## Setup & run

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Copy `.env.example` to `.env` and fill in credentials (Spotify + your chosen LLM provider).

Run the pipeline:

```bash
showcase
# or
python -m showcase.main
```

---

General (new) structure

Event scraper:
Input: List of urls
Output: Event yaml/dict containing band names (single string), event time and event date

 -> Given list urls, scrape webpage contents -> pass to ML model that extracts event name, time, date -> return event yaml

Show name parser:
Input: Event yaml/dict
Output: List of Show objects containing individual names, uri, date, time, order of events, before/after acts

TODO - add filtering here
TODO - uri

-> parses event name into individual show names -> pass to ML model, returns possibilities -> perform fuzzywuzzy mapping 
 - cover band extraction??

PlaylistCreator
    Input: SpotifyPlaylist and list of shows
    Output: Nothing - creates playlist 

 API signature:
    Stage 1: Input urls


Should be able to work without spotify i.e parse webpage, create list of shows (ai best guess)
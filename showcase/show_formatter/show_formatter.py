from showcase.llm_io.providers import OpenAIModelIO
from showcase.llm_io.model_io import ModelIO
from fuzzywuzzy import process
from typing import Tuple, List, Dict
import ast
from showcase.llm_io.providers.openrouter_model_io import OpenRouterModelIO
from showcase.spotify_io.spotify_io import SpotifyIO
from showcase.data.show import Show
from showcase.data.show_order_enum import ShowOrder

class ShowFormatter:
    PROMPT = """ 
You are an AI assistant specializing in the extraction and formatting of potential band name combinations from a single show listing. Your primary task is to identify all reasonable possibilities for how the names in a listing could be interpreted as separate or combined band names. The final output must be a dict of sets, where each set represents one distinct, complete grouping of possible band names associated with the event id.

For each item in the list:

### 1. Pre-Processing and Name Extraction

1.  **Remove Descriptive Phrases:** Eliminate generic descriptive text and promotional elements (e.g., "special events nights," "EP release," "Special Presentation", "<phrase>:") or prefixing to focus only on potential band names. Usually any prefixing before a colon ":"

### 2. Core Task: Identifying All Possible Sets

1.  **Return All Possibilities:** Generate a dict with event_id key value a list of sets that accounts for all plausible interpretations of name groupings.
2.  **Completeness:** Every element in the original, cleaned show listing must be included in every returned possibility set. **Do not drop any names.**

### 3. Handling Connectors, Conjunctions, and Formatting

1.  **Connectors:** This rule applies to conjunctions and common separators (e.g., +, &, and, with, vs., presents).
    * **If Kept Whole:** Maintain the original connector/conjunction (e.g., "Band A + Band B").
    * **If Split:** Remove the connector/conjunction from the resulting separate names (e.g., "Band A", "Band B").
2.  **Contractions:** If standard grammatical contractions (e.g., *don't*, *we'll*) are split, remove the contraction (e.g., *don't* becomes *do not*). If the name is kept whole, maintain the original contraction.

### 4. Required Output Format

1.  **Input:** A dict of event_id key to single show name value is provided at a time. Iterate through the dict one at a time.
2.  **Output Type:** The return must be a **Dict of list of sets** using the same keys in the input.
3.  **Set Contents:** Each set must contain a **complete list** of the derived possible band names for that specific interpretation for a single show.

**Example:**
Input = {event_1:"Florence + The Machine with Modest Mouse", event_2:"Equator, Early Tombs & Dogs"}
Return: {
  "event_1": [
    {"Florence + The Machine with Modest Mouse"},
    {"Florence + The Machine", "Modest Mouse"},
    {"Florence", "The Machine", "Modest Mouse"},
    {"Florence", "The Machine with Modest Mouse"}
  ],
  "event_2": [
    {"Equator, Early Tombs & Dogs"},
    {"Equator", "Early Tombs & Dogs"},
    {"Equator", "Early Tombs", "Dogs"},
    {"Equator, Early Tombs", "Dogs"}
  ]
}
    """

    def __init__(self, model_io : ModelIO, sp_io : SpotifyIO, min_similarity = 70):
        self.model_io = model_io
        self.sp_io = sp_io
        self.min_similarity = min_similarity

    def format_shows(self, event_list: List[Dict]) -> List[Show]:
        """
        Formats a list of event dictionaries into a single list of Show objects.
        """
        all_shows = []
        if not event_list:
            return all_shows
        bands = {f"event_{i}":event['bands'] for i,event in enumerate(event_list)}
        if not bands:
            return all_shows
        candidates_str = self.model_io.get_response(str(bands), self.PROMPT)
        if not candidates_str:
            return all_shows
        try:
            candidates_all = ast.literal_eval(candidates_str)
        except (ValueError, SyntaxError):
            return all_shows
        for id,candidates in candidates_all.items():
            show_names = self.select_best_candidate(candidates)
            if show_names is not None:
                a=event_list[int(id.split('_')[1])]
                shows = self.create_shows_from_list(show_names, event_list[int(id.split('_')[1])])
                all_shows.extend(shows)
        return all_shows


    def get_most_similar_value(self, artist_name:str) -> Tuple[str,str,int]:
        """
        Adapted from ShowNameParser.get_most_similar_value
        """
        # Return top 10 matches as name:id pairs
        results=self.sp_io.search_artists(artist_name)
        if results and results["artists"]["items"]:
            name_id_dict = {a['name']:a['uri'] for a in results["artists"]["items"]}
        else:
            return None

        # Select closest match based on name
        best_match = process.extractOne(artist_name, name_id_dict.keys())

        # assert name meets similarity threshold
        if best_match and best_match[1] > self.min_similarity:
            return (best_match[0], name_id_dict[best_match[0]], best_match[1])
        else:
            return None

    def select_best_candidate(self, candidates: list):
        best_candidate_set = None
        max_avg_score = -1

        for candidate_set in candidates:
            new_candidate_list = []
            total_score = 0
            num_artists = len(candidate_set)
            if num_artists == 0:
                continue

            for artist_name in candidate_set:
                match = self.get_most_similar_value(artist_name)
                if match:
                    # match is (name, uri, similarity)
                    candidate_dict = {"original_artist_name":artist_name, "best_match_artist_name":match[0], "best_match_artist_uri":match[1], "similarity_score":match[2]}
                    new_candidate_list.append(candidate_dict)
                    total_score += match[2]

            avg_score_over_all_in_set = total_score / num_artists
            if avg_score_over_all_in_set > max_avg_score:
                max_avg_score = avg_score_over_all_in_set
                best_candidate_set = new_candidate_list

        return best_candidate_set
    
    def create_shows_from_list(self, show_names, show_info):
        shows = []
        for i, show_name_dict in enumerate(show_names):
            show_order = ShowOrder.HEADLINER if i == 0 else ShowOrder.OPENER
            shows.append(Show(
                band_name=show_name_dict["best_match_artist_name"], 
                event_timestamp=show_info.get("event_timestamp", ""), 
                venue=show_info.get("venue", ""),
                show_order=show_order,
                original_band_name=show_name_dict["original_artist_name"], 
                similarity_score=show_name_dict["similarity_score"], 
                artist_uri=show_name_dict["best_match_artist_uri"]
            ))
        return shows
    



if __name__ == "__main__":
    from showcase.settings import load_env

    load_env()
    model_name = "gpt-4.1-mini"
    model_io = OpenRouterModelIO(model_name)
    
    # Example data in the format expected by format_shows (List[Dict])
    event_list = [
        {'bands': 'Uncovered: Rich Freed & the Renegades | The Boo Radley Project | The Pressures', 'event_timestamp': '2025-12-15T20:00:00', 'venue': 'The Cameron House'},
         {'bands': 'Jog EP Release with Joshua Jellybones & Human Magic Power Trio', 'event_timestamp': '2025-12-17T20:00:00', 'venue': 'The Horseshoe Tavern'},
          {'bands': 'Dopamine Dream', 'event_timestamp': '2025-12-18T20:30:00', 'venue': 'Lee\'s Palace'}
    ]
    sp_io = SpotifyIO()
    show_formatter = ShowFormatter(model_io, sp_io)
    shows = show_formatter.format_shows(event_list)
    [print(show) for show in shows]
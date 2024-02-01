"""
This code takes a 'show' name and parses it out into the individual band names. 

This is more of an art than a science as band names can have conjuctions i.e Florence + the Machine, Tom Petty and the Heartbreakers, etc.
But this is also how venues group together bands playing on a single night - <headliner>, <opener>, <opener>

To cap it off, its not ideal to blindly search random combination of collocated words, as you'll likely get a higher match on single words and single words can be a band name
i.e If you go through word by word for 'The Queen is Dead', you'll get a strong match on Queen 

OH and on top of that - how do you handle cover bands??

The show name is split on any conjunctions and combines different collocated combinations

Example: (Reverend Horton Heat with The Surfrajettes will yield Reverend Horton Heat with The Surfrajettes)

This code uses the Spotipy API to test different search combinations of names to find likely matches
It uses Spotify's search functionality to return the top 10 matches, then uses fuzzywuzzy to find the closest match, this is repeated for word combination

"""

from fuzzywuzzy import process
from typing import List

CONJUNCTIONS = [" with ", " and ", " & ", " + ", " featuring ", " presents "]
REMOVE_AFTER = ['-']


class ShowNameParser():

    def __init__(self, sp):
        """
        Connect to Spotify
        """
        self.sp = sp

    @staticmethod
    def remove_after_keyword(artist_name:str) -> str:
        """
        Remove everything after a keyword, but before a conjunction
        """
        for keyword in REMOVE_AFTER:
            if keyword in artist_name:
                artist_name = artist_name.split(keyword)[0]
        return artist_name

    def get_artist_name_combos(show_name: str) -> List[tuple]:
        """
        Get all combinations of artist names from show name
        """
        for conjunction in CONJUNCTIONS:
            show_name=show_name.replace(conjunction, "$&$"+conjunction+"$&$")
        split_names = show_name.split("$&$")
        # remove any straying or leading conjunctions
        n=0
        combos = []
        while n < len(split_names):
            for i in range(0,len(split_names),2):
                combos.append(''.join(split_names[i:i+n+1]))
            n = n+2
        return list(set(combos))
    
    def get_most_similar_value(self, artist_name:str) -> int:
        
        # Return top 10 matches as name:id pairs
        
        ## TODO: Generalize this code
        results=self.sp.client.search(q=f"artist:{artist_name}", type='artist')
        if len(results)>0:
            name_id_dict = {a['name']:a['uri'] for a in results["artists"]["items"]}
        else:
            return None
        # Select closest match based on name
        best_match = process.extractOne(artist_name, name_id_dict.keys())
        # assert name meets similarity threshold
        if best_match is None or len(best_match)<2:
            return None
        if best_match[1] > min_similarity:
            return name_id_dict[best_match[0]]
        else:
            return None
    def remove_specified_artist_names(self, artist_names:List[str], remove_names:List[str])->List[str]:
        """
        Remove specified artist names from list
        """
        return [artist for artist in artist_names if artist not in remove_names]

    # def _get_artist_id_from_name(self, artist_name, min_similarity = 70):
        
    #     # Return top 10 matches as name:id pairs
    #     results=self.sp.client.search(q=f"artist:{artist_name}", type='artist')
    #     if len(results)>0:
    #         name_id_dict = {a['name']:a['uri'] for a in results["artists"]["items"]}
    #     else:
    #         return None
    #     # Select closest match based on name
    #     best_match = process.extractOne(artist_name, name_id_dict.keys())
    #     # assert name meets similarity threshold
    #     if best_match is None or len(best_match)<2:
    #         return None
    #     if best_match[1] > min_similarity:
    #         return name_id_dict[best_match[0]]
    #     else:
    #         return None
    
    # def parse_show_name(self, show_name:str)->List[str]:
    #     """
    #     Parse show name into individual band names

    #     Inputs:
    #     --------
    #     show_name : str
    #         Name of show

    #     Outputs:
    #     --------
    #     artists : List[str]
    #         List of artist names
    #     """
    #     # Split on conjunctions
    #     show_name = show_name.replace(" with ", " ")
    #     show_name = show_name.replace(" and ", " ")
    #     show_name = show_name.replace(" & ", " ")
    #     show_name = show_name.replace(" + ", " ")
    #     show_name = show_name.replace(" featuring ", " ")
    #     show_name = show_name.replace(" presents ", " ")
    #     show_name = show_name.replace(" presents ", " ")
    #     show_name = show_name.replace(" presents ", " ")
    #     show_name = show_name.replace


if __name__ == "__main__":
    print('here')
    print('Talon with Stankonya & The Hogtown Rebels')
    a = 'Talon with Stankonya & The Hogtown Rebels'
    
    


"""
# Show Name Parser Class

This class parses through a show's name and breaks it out into the individual band names. 

This is more of an art than a science as band names can have conjuctions i.e Florence + the Machine, Tom Petty and the Heartbreakers, etc.
But this is also how venues group together bands playing on a single night - <headliner>, <opener>, <opener>

To cap it off, its not ideal to blindly search random combination of collocated words, as you'll likely get a higher match on single words and single words can be a band name
i.e If you go through word by word for 'The Queen is Dead', you'll get a strong match on Queen 

OH and on top of that - how do you handle cover bands??

The show name is split on any conjunctions and combines different collocated combinations

Example: (Reverend Horton Heat with The Surfrajettes will yield (Reverend Horton Heat with The SurfrajettesReverend Horton Heat with The Surfrajettes)

The Spotipy API is then used to test different combinations of names to find the likeliest match
Spotify's search functionality is used to return the top 10 matches, then fuzzywuzzy is usedto find the closest match. t
This is repeated for each bandname combination

# Future improvements:

Have a popularity filter - either global or venue level - which excludes bands that are too popular to be playing at the venue

i.e if the venue is pretty small and the band is Queen & King, the combos will be (Queen, King, Queen & King) - 'Queen' is going to give a similarity score of 100 - but no chance they are playing at the venue
This will also filter out cover bands 

"""
import numpy as np
from fuzzywuzzy import process
from typing import List
from typing import Tuple
from typing import Dict

min_similarity = 70

CONJUNCTIONS = [" with ", " and ", " & ", " + ", " featuring ", " presents ", " | ", ", "]
REMOVE_AFTER = ['-']


class ShowNameParser:

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

    @staticmethod
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
        # remove duplicates while maintaining list order
        combos = [combo for i, combo in enumerate(combos) if i == combos.index(combo)]
        return combos
    
    def get_most_similar_value(self, artist_name:str) -> Tuple[str,str,int]:
                
        ## TODO: Generalize this code
        
        # Return top 10 matches as name:id pairs
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
            return (best_match[0],name_id_dict[best_match[0]],best_match[1]) 
        else:
            return None
        
    
    @staticmethod
    def _get_indices_from_length(length:int)->str:
        """
        Get indices from len
        """
        n = 0.5*np.sqrt(8*length+1)-0.5
        return [int(n*i - i*(i-1)/2) for i in range(0,int(n))]
    
    def _remove_combo_options(self,name_combos:List[str])->List[str]:
        """
        Remove combo options
        """
        length = len(name_combos)
        inds_to_remove = self._get_indices_from_length(length)
        return [name for i,name in enumerate(name_combos) if i not in inds_to_remove]
    
    def get_best_match(self, name_combos:List[str])->Tuple[str,str,int]:
        """
        Get best match from list of name combos
        """

        inds = self._get_indices_from_length(len(name_combos))
        candidates = [name_combos[i] for i in inds]
        best_match = None
        best_match_score = 0
        ind = 0 # change to -1 if no match
        for i,name in enumerate(candidates):
            match = self.get_most_similar_value(name)
            if match is not None:
                if match[2]>best_match_score:
                    best_match = match
                    best_match_score = match[2]
                    ind = i
        return best_match, ind
    
    def split_show_name(self, show_name:str)->List[str]:
        # Step one: split into possible combinations
        artist_names = []
        name_combos = self.get_artist_name_combos(show_name)
        # Step two: Find best combination containing the first listed
            # artist. Once the best match is found, recursively remove artists
            # from the list that are in the combination
        
        # TODO turn this into recursion
        while len(name_combos)>0:
            best_match, ind = self.get_best_match(name_combos)
            if best_match is not None:
                artist_names.append((best_match[0],best_match[1]))
            while ind > -1:
                name_combos = self._remove_combo_options(name_combos)
                ind -= 1
        return artist_names

        
    def remove_specified_artist_names(self, artist_names:List[str], remove_names:List[str])->List[str]:
        """
        Remove specified artist names from list
        """
        return [artist for artist in artist_names if artist not in remove_names]

    def parse_show_name(self, show_dict:Dict, artist_names_to_ignore = None) -> List[Dict]:
        """
        Parse show name into individual band names

        Inputs:
        --------
        show_name : str
            Name of show

        Outputs:
        --------
        artists : List[str]
            List of artist names
        """
        artist_names_to_ignore = artist_names_to_ignore or []
        artist_name = show_dict['artist_name']
        if artist_name in artist_names_to_ignore:
            return None
        
        artist_names = self.split_show_name(artist_name)

        parsed_artist_list = []
        for name in artist_names:
            artist_name = self.remove_after_keyword(name[0])
            artist_uuid = name[1]
            parsed_artist_list.append({'artist_name':artist_name,'artist_uuid':artist_uuid,'show_date':show_dict['show_date'], 'show_name':show_dict['artist_name']})

        return parsed_artist_list


if __name__ == "__main__":
    sp = None
    parser = ShowNameParser(sp)

    
    


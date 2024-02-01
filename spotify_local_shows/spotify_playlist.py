from utils.playlist_helper import track_df_from_tracks
from fuzzywuzzy import process

class SpotifyPlaylist:
    def __init__(self, sp):
        """
        Connect to Spotify
        """
        self.sp = sp

    def get_playlist_df(self, pl_id, df_schema):
        # Get all tracks
        tracks = []
        offset = 0
        while True:
            response = self.sp.client.playlist_items(pl_id,
                                        offset=offset)
            
            if len(response['items']) == 0:
                break
            tracks +=response['items']
            offset = offset + len(response['items'])
        
        track_df = track_df_from_tracks(tracks=tracks, df_schema=df_schema)

        return track_df

    def get_artist_id_from_name(self, artist_name, min_similarity = 70):
        
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
            return name_id_dict[best_match[0]]
        else:
            return None
    
    def get_top_tracks_from_artist_id(self, artist_id, num_top_tracks = 5):
        if artist_id is not None:
            top_tracks = self.sp.client.artist_top_tracks(artist_id)
            if len(top_tracks['tracks'])>num_top_tracks:
                top_tracks['tracks'] = top_tracks['tracks'][:num_top_tracks]
            return top_tracks
        
    def get_top_tracks_from_artist_name(self, artist_name, num_top_tracks = 5, min_similarity = 70):
        # Get uri from artist
        artist_id = self.get_artist_id_from_name(artist_name, min_similarity)
        return self.get_top_tracks_from_artist_id(artist_id)


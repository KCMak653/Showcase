from utils.playlist_helper import track_df_from_tracks
from fuzzywuzzy import process

class SpotifyPlaylist:
    def __init__(self, sp, playlist_id):
        """
        Connect to Spotify
        """
        self.sp = sp
        self.playlist_id = playlist_id

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
            top_tracks = self.sp.client.artist_top_tracks(artist_id)['tracks']
            num_top_tracks = min(num_top_tracks, len(top_tracks))
            top_tracks = [track['uri'] for track in top_tracks[:num_top_tracks]]
            
            return top_tracks


    def get_top_tracks_from_artist_name(self, artist_name, num_top_tracks = 5, min_similarity = 70):
        # Get uri from artist
        artist_id = self.get_artist_id_from_name(artist_name, min_similarity)
        return self.get_top_tracks_from_artist_id(artist_id, num_top_tracks=num_top_tracks)

    # Maybe reconfig to add_top_tracks_from_artist_id and do artist iteratively
    def add_top_tracks_from_artist_id_list(self, artist_id_list, num_top_tracks = 5):
        """
        Add top tracks from each artist to the playlist

        Inputs:
        -------
        artists : List[str]
            List of artists

        """
        top_n_track_ids = []
        for artist_id in artist_id_list:
            top_n_track_ids += self.get_top_tracks_from_artist_id(artist_id, num_top_tracks)
        num_tracks = len(top_n_track_ids)
        self.sp.client.playlist_replace_items(self.playlist_id, top_n_track_ids[:100])
        i = 100
        while num_tracks > i:
            self.sp.client.playlist_add_items(self.playlist_id, top_n_track_ids[i:i+100])
            i += 100
        
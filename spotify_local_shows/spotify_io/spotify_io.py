import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class SpotifyIO:
    """
    A wrapper class for the Spotipy client to handle authentication and provide
    domain-specific methods for interacting with the Spotify API.
    """
    def __init__(self, client_id=None, client_secret=None, redirect_uri=None, scope="playlist-modify-private"):
        """
        Initializes the SpotifyIO client.

        Credentials can be passed as arguments or set as environment variables
        (SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI).
        """
        self.client_id = client_id or os.environ.get('SPOTIPY_CLIENT_ID')
        self.client_secret = client_secret or os.environ.get('SPOTIPY_CLIENT_SECRET')
        self.redirect_uri = redirect_uri or os.environ.get('SPOTIPY_REDIRECT_URI')
        self.scope = scope

        if not all([self.client_id, self.client_secret, self.redirect_uri, self.scope]):
            raise ValueError("Spotify API credentials and scope must be provided or set as environment variables.")

        self._client = self._initialize_client()

    def _initialize_client(self):
        """
        Initializes and returns a Spotipy client with automatic token handling.
        """
        auth_manager = SpotifyOAuth(client_id=self.client_id,
                                    client_secret=self.client_secret,
                                    redirect_uri=self.redirect_uri,
                                    scope=self.scope,
                                    cache_path=".spotify_token_cache")

        client = spotipy.Spotify(auth_manager=auth_manager)
        return client

    def search_artists(self, artist_name, limit=10):
        """
        Searches for an artist on Spotify by name.

        Args:
            artist_name (str): The name of the artist to search for.
            limit (int): The maximum number of results to return.

        Returns:
            dict: The raw search result from the Spotify API, or None if the
                  artist_name is empty.
        """
        if not artist_name:
            return None
        return self._client.search(q=f'artist:{artist_name}', type='artist', limit=limit)

    
    def get_tracks_in_playlist(self, playlist_id):
        # Get all tracks
        tracks = []
        offset = 0
        while True:
            response = self._client.playlist_items(playlist_id,
                                        offset=offset)
            
            if len(response['items']) == 0:
                break
            tracks +=response['items']
            offset = offset + len(response['items'])
        return tracks
    
    def get_top_tracks_from_artist_id(self, artist_id, num_top_tracks = 5):
        if artist_id is not None:
            top_tracks = self._client.artist_top_tracks(artist_id)['tracks']
            num_top_tracks = min(num_top_tracks, len(top_tracks))
            top_tracks = [track['uri'] for track in top_tracks[:num_top_tracks]]
            
            return top_tracks

    def replace_items_in_playlist(self, playlist_id, track_ids):
        # TODO verify functionality - some sort of 100 item limit??
        self._client.playlist_replace_items(playlist_id, track_ids)

    def add_items_to_playlist(self, playlist_id, track_ids):
        """Adds tracks to a playlist, handling the 100-item API limit by chunking."""
        chunk_size = 100
        for i in range(0, len(track_ids), chunk_size):
            chunk = track_ids[i:i + chunk_size]
            logger.info(f"Adding chunk of {len(chunk)} tracks to playlist {playlist_id}.")
            self._client.playlist_add_items(playlist_id, chunk)

    def create_playlist(self, playlist_name: str) -> str:
        """
        Creates a new private playlist for the authenticated user.

        Args:
            playlist_name (str): The name for the new playlist.

        Returns:
            str: The ID of the newly created playlist.
        """
        user_id = self._client.me()['id']
        playlist = self._client.user_playlist_create(user=user_id, name=playlist_name, public=False)
        return playlist['id']




if __name__ == "__main__":
    spotify_io = SpotifyIO()
    playlist_id = "5tyQi6SM2ohe4OT26LCsHH"
    artists = spotify_io.search_artists("shakira")
    tracks = spotify_io.get_top_tracks_from_artist_id("6DUKY45lfzxJLOfU0v9C0j")
    print(tracks)
    spotify_io.add_items_to_playlist(playlist_id, tracks)
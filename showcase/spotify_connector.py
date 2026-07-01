import spotipy

class SpotifyConnector:

    def __init__(
        self,
        spotipy_client_id,
        spotipy_client_secret,
        spotipy_redirect_uri,
        scope,

    ):
        """
        Initialize Spotify connection

        Wrapper around sp_oauth

        Args:
        -----
        spotipy_client_id : str
            Spotify client id
        spotipy_client_secret : str
            Spotify client secret
        spotipy_redirect_uri : str
            Redirect uri for Spotify
        scope : str
            Scope for Spotify api

        """

        sp_oauth = spotipy.oauth2.SpotifyOAuth(spotipy_client_id, spotipy_client_secret,spotipy_redirect_uri,scope)

        # #click "Accept" in your browser when the auth window pops up
        code = sp_oauth.get_auth_response(open_browser=True)
        token = sp_oauth.get_access_token(code)
        self.client = spotipy.Spotify(auth=token['access_token'])


SPOTIPY_CLIENT_ID = ''
SPOTIPY_CLIENT_SECRET = ''
SCOPE = ('user-read-recently-played,user-library-read,user-read-currently-playing,playlist-read-private,playlist-modify-private,playlist-modify-public,user-read-email,user-modify-playback-state,user-read-private,user-read-playback-state')
SPOTIPY_REDIRECT_URI = 'http://google.com/'
MIN_SIMILARITY = 70 # Similarity rating for fuzzywuzzy
import os
abc = os.getenv('x')
MIN_TRACKS = 2
my_local_show_pl_id = ''
venues_to_include = ['horseshoe_tavern']
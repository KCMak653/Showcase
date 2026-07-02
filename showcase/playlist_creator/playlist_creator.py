from showcase.spotify_io.spotify_io import SpotifyIO
from typing import List, Optional, Union
from showcase.data.show import Show
from showcase.data.show_order_enum import ShowOrder
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PlaylistCreator:
    # TODO make this flexible. For now just create a playlist everytime. 
    # It should be able to replace an existing one
    #
    def __init__(self, sp_io: SpotifyIO):
        self.sp_io = sp_io

    def create_playlist(
        self, 
        shows: List[Show], 
        num_tracks: int = 3,
        show_order_select: str = "all",
        venue_name: Optional[Union[str, List[str]]] = None,
        after_timestamp: Optional[datetime] = None,
        before_timestamp: Optional[datetime] = None
    ) -> Optional[str]:
        """
        Creates a new Spotify playlist from a list of shows.

        Args:
            shows: A list of Show objects.
            num_tracks: The number of top tracks to add for each artist.
            show_order_select: "all" (default) to include every show, "headliner" to include only headliners.
            venue_name: The venue(s) used to filter, for naming the playlist.
            after_timestamp: The start date used to filter, for naming the playlist.
            before_timestamp: The end date used to filter, for naming the playlist.

        Returns:
            The ID of the newly created playlist, or None if no shows were provided.
        """
        if not shows:
            logger.info("No shows provided; skipping playlist creation.")
            return None
        if show_order_select == "headliner":
            shows = [s for s in shows if s.show_order == ShowOrder.HEADLINER]
            if not shows:
                logger.info("No headliner shows after filtering; skipping playlist creation.")
                return None
        name_parts = ["showcase"]
        if venue_name:
            if isinstance(venue_name, list):
                name_parts.append(", ".join(venue_name))
            else:
                name_parts.append(venue_name)
        if after_timestamp:
            name_parts.append(f"from {before_timestamp.strftime('%b %d')}")
        if before_timestamp:
            name_parts.append(f"to {after_timestamp.strftime('%b %d')}")
        
        timestamp = datetime.now().strftime("%Y-%m-%d")
        name_parts.append(timestamp)
        playlist_name = " - ".join(name_parts)
        
        logger.info(f"Creating new playlist named: {playlist_name}")
        new_playlist_id = self.sp_io.create_playlist(playlist_name)

        # 2. Collect top tracks from all artists in the shows
        track_uris = []
        for show in shows:
            if show.artist_uri:
                logger.info(f"Fetching top {num_tracks} tracks for artist: {show.band_name} ({show.artist_uri})")
                top_tracks = self.sp_io.get_top_tracks_from_artist_id(
                    artist_id=show.artist_uri, 
                    num_top_tracks=num_tracks
                )
                if top_tracks:
                    track_uris.extend(top_tracks)
            else:
                logger.warning(f"Skipping artist {show.band_name} as no artist_uri is available.")

        # 3. Add collected tracks to the new playlist
        if track_uris:
            logger.info(f"Adding {len(track_uris)} tracks to playlist {new_playlist_id}")
            self.sp_io.add_items_to_playlist(new_playlist_id, track_uris)
        else:
            logger.warning("No tracks found to add to the playlist.")

        print(f"Successfully created playlist! ID: {new_playlist_id}")
        return new_playlist_id
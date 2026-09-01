from showcase.spotify_io.spotify_io import SpotifyIO
from typing import List, Optional, Union
from showcase.data.show import Show
from showcase.data.show_order_enum import ShowOrder
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Spotify replace-items limit; additional tracks are appended in chunks.
_SPOTIFY_REPLACE_LIMIT = 100


class PlaylistCreator:
    def __init__(self, sp_io: SpotifyIO):
        self.sp_io = sp_io

    @staticmethod
    def _filter_shows_by_order(
        shows: List[Show],
        show_order_select: str,
    ) -> List[Show]:
        if show_order_select == "headliner":
            return [s for s in shows if s.show_order == ShowOrder.HEADLINER]
        return shows

    def collect_track_uris_from_shows(
        self,
        shows: List[Show],
        num_tracks: int = 2,
        show_order_select: str = "headliner",
    ) -> List[str]:
        """
        Build an ordered, deduplicated list of Spotify track URIs from shows.

        Shows should already be sorted by event time. Track order follows show order;
        duplicate track URIs are skipped while preserving first-seen order.
        """
        filtered = self._filter_shows_by_order(shows, show_order_select)
        track_uris: List[str] = []
        seen: set[str] = set()

        for show in filtered:
            if not show.artist_uri:
                logger.warning(
                    "Skipping artist %s as no artist_uri is available.",
                    show.band_name,
                )
                continue
            logger.info(
                "Fetching top %s tracks for artist: %s (%s)",
                num_tracks,
                show.band_name,
                show.artist_uri,
            )
            top_tracks = self.sp_io.get_top_tracks_from_artist_id(
                artist_id=show.artist_uri,
                num_top_tracks=num_tracks,
            )
            if not top_tracks:
                continue
            for uri in top_tracks:
                if uri not in seen:
                    seen.add(uri)
                    track_uris.append(uri)

        return track_uris

    def _replace_playlist_tracks(self, playlist_id: str, track_uris: List[str]) -> None:
        """Replace playlist contents; chunk when exceeding Spotify replace limit."""
        if not track_uris:
            self.sp_io.replace_items_in_playlist(playlist_id, [])
            return

        head = track_uris[:_SPOTIFY_REPLACE_LIMIT]
        tail = track_uris[_SPOTIFY_REPLACE_LIMIT:]
        self.sp_io.replace_items_in_playlist(playlist_id, head)
        if tail:
            self.sp_io.add_items_to_playlist(playlist_id, tail)

    def sync_playlist(
        self,
        shows: List[Show],
        playlist_id: Optional[str] = None,
        playlist_name: str = "Showcase",
        num_tracks: int = 2,
        show_order_select: str = "headliner",
    ) -> Optional[str]:
        """
        Create or update a living playlist in place (web app sync path).

        When playlist_id is None, creates a new private playlist named playlist_name.
        Otherwise replaces all items in the existing playlist.

        Returns:
            The playlist ID, or None if no shows remain after filtering.
        """
        filtered = self._filter_shows_by_order(shows, show_order_select)
        if not filtered:
            logger.info("No shows after filtering; skipping playlist sync.")
            return playlist_id

        track_uris = self.collect_track_uris_from_shows(
            shows,
            num_tracks=num_tracks,
            show_order_select=show_order_select,
        )

        if playlist_id is None:
            logger.info("Creating new playlist named: %s", playlist_name)
            playlist_id = self.sp_io.create_playlist(playlist_name)

        if track_uris:
            logger.info(
                "Syncing %s tracks to playlist %s",
                len(track_uris),
                playlist_id,
            )
            self._replace_playlist_tracks(playlist_id, track_uris)
        else:
            logger.warning("No tracks found; clearing playlist %s", playlist_id)
            self.sp_io.replace_items_in_playlist(playlist_id, [])

        return playlist_id

    def create_playlist(
        self,
        shows: List[Show],
        num_tracks: int = 3,
        show_order_select: str = "all",
        venue_name: Optional[Union[str, List[str]]] = None,
        after_timestamp: Optional[datetime] = None,
        before_timestamp: Optional[datetime] = None,
    ) -> Optional[str]:
        """
        Creates a new Spotify playlist from a list of shows (CLI path).

        For update-in-place sync, prefer sync_playlist() instead.

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

        filtered = self._filter_shows_by_order(shows, show_order_select)
        if not filtered:
            logger.info("No headliner shows after filtering; skipping playlist creation.")
            return None

        name_parts = ["showcase"]
        if venue_name:
            if isinstance(venue_name, list):
                name_parts.append(", ".join(venue_name))
            else:
                name_parts.append(venue_name)
        if before_timestamp:
            name_parts.append(f"from {before_timestamp.strftime('%b %d')}")
        if after_timestamp:
            name_parts.append(f"to {after_timestamp.strftime('%b %d')}")

        timestamp = datetime.now().strftime("%Y-%m-%d")
        name_parts.append(timestamp)
        playlist_name = " - ".join(name_parts)

        track_uris = self.collect_track_uris_from_shows(
            shows,
            num_tracks=num_tracks,
            show_order_select=show_order_select,
        )

        logger.info("Creating new playlist named: %s", playlist_name)
        new_playlist_id = self.sp_io.create_playlist(playlist_name)

        if track_uris:
            logger.info(
                "Adding %s tracks to playlist %s",
                len(track_uris),
                new_playlist_id,
            )
            self._replace_playlist_tracks(new_playlist_id, track_uris)
        else:
            logger.warning("No tracks found to add to the playlist.")

        logger.info("Successfully created playlist! ID: %s", new_playlist_id)
        return new_playlist_id

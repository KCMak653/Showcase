from datetime import datetime
from typing import Optional
from showcase.data.show_order_enum import ShowOrder

# Data class containing show information
# A show is a singular band performance at a specific timestamp and venue.
class Show:

    def __init__(self, band_name: str, event_timestamp: str, venue: str, show_order: ShowOrder = ShowOrder.UNKNOWN, next_show = None, previous_show=None, original_band_name=None, similarity_score: float = None, artist_uri: str = None):
        self.band_name = band_name
        self.event_timestamp_str = event_timestamp
        self.venue = venue
        self.show_order = show_order
        self.next_show = next_show
        self.previous = previous_show
        self.original_band_name = original_band_name
        self.similarity_score = similarity_score
        self.artist_uri = artist_uri
        
        # Store the parsed datetime object internally
        self.event_datetime: Optional[datetime] = self._parse_timestamp(event_timestamp)

    def _parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """Parses the timestamp string into a datetime object."""
        if timestamp_str:
            try:
                return datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S")
            except (ValueError, TypeError):
                return None
        return None

    def get_band_name(self) -> str:
        return self.band_name
    
    def get_show_date(self) -> str:
        """Derives the date string (DD/MM/YYYY) from the internal datetime object."""
        if self.event_datetime:
            return self.event_datetime.strftime("%d/%m/%Y")
        return ""
    
    def get_show_time(self) -> str:
        """Derives the time string (HH:MM:SS) from the internal datetime object."""
        if self.event_datetime:
            return self.event_datetime.strftime("%H:%M:%S")
        return ""

    def get_show_timestamp_str(self) -> str:
        """Returns the original full event timestamp string."""
        return self.event_timestamp_str

    def get_show_timestamp_obj(self) -> Optional[datetime]:
        """Returns the event timestamp as a datetime object."""
        return self.event_datetime
    
    def get_show_order(self) -> ShowOrder:
        return self.show_order

    def __str__(self):
        return (f"Band: {self.band_name}, Timestamp: {self.event_timestamp_str}, Venue: {self.venue}, "
                f"Order: {self.show_order.name}")


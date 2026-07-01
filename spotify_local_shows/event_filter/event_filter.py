from typing import List, Optional, Dict, Union
from datetime import datetime


class EventFilter:
    """
    A utility class to filter event data.
    This class can filter raw event dictionaries and can be extended to filter Show objects.
    """

    @classmethod
    def filter_events_data(
        cls,
        events_data: List[Dict],
        venue_name: Optional[Union[str, List[str]]] = None,
        after_timestamp: Optional[datetime] = None,
        before_timestamp: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Orchestrates filtering of a list of raw event dictionaries.

        Args:
            events_data: A list of event dicts (e.g. from EventScraper.scrape_events_from_webpage_urls).
            venue_name: A venue name or list of venue names to filter by.
            after_timestamp: Only include events on or after this datetime.
            before_timestamp: Only include events on or before this datetime.

        Returns:
            A new list of event dictionaries that pass all active filters.
        """
        filtered = events_data
        if venue_name:
            filtered = cls._filter_by_venue(filtered, venue_name)
        if after_timestamp or before_timestamp:
            filtered = cls._filter_by_timestamp(filtered, after_timestamp, before_timestamp)
        return filtered

    @staticmethod
    def _filter_by_venue(
        events_data: List[Dict],
        venue_name: Union[str, List[str]]
    ) -> List[Dict]:
        """Filters events by venue name(s)."""
        allowed_venues = []
        if isinstance(venue_name, str):
            allowed_venues = [venue_name.lower()]
        elif isinstance(venue_name, list):
            allowed_venues = [name.lower() for name in venue_name]
        if not allowed_venues:
            return events_data

        return [
            event for event in events_data
            if event.get('venue') and any(allowed in event['venue'].lower() for allowed in allowed_venues)
        ]

    @staticmethod
    def _filter_by_timestamp(
        events_data: List[Dict],
        after_timestamp: Optional[datetime],
        before_timestamp: Optional[datetime]
    ) -> List[Dict]:
        """Filters events by a datetime range."""
        if not after_timestamp and not before_timestamp:
            return events_data

        filtered_list = []
        for event in events_data:
            event_timestamp_str = event.get('event_timestamp')
            if not event_timestamp_str:
                continue
            try:
                event_datetime_obj = datetime.strptime(event_timestamp_str, "%Y-%m-%dT%H:%M:%S")
                if after_timestamp and event_datetime_obj > after_timestamp:
                    continue
                if before_timestamp and event_datetime_obj < before_timestamp:
                    continue
                filtered_list.append(event)
            except (ValueError, TypeError):
                continue
        return filtered_list

if __name__ == '__main__':
    # --- Test Cases ---
    test_events_data = [
        {
            "bands": "The Cool Cats",
            "event_timestamp": "2026-02-15T21:00:00",
            "venue": "The Horseshoe Tavern"
        },
        {
            "bands": "The Rockers",
            "event_timestamp": "2026-02-15T22:00:00",
            "venue": "Lee's Palace"
        },
        {
            "bands": "Acoustic Duo",
            "event_timestamp": "2026-03-01T19:30:00",
            "venue": "The Cameron House"
        },
        {
            "bands": "Jazz Trio",
            "event_timestamp": "2026-03-10T20:00:00",
            "venue": "The Horseshoe Tavern"
        },
        {
            "bands": "Solo Artist",
            "event_timestamp": "2026-03-10T21:00:00",
            "venue": "Lee's Palace",
        },
        {
            "bands": "No Venue Band",
            "event_timestamp": "2026-03-11T20:00:00",
            "venue": "" 
        },
        {
            "bands": "No Timestamp Band",
            "event_timestamp": "",
            "venue": "The Horseshoe Tavern"
        }
    ]

    print("--- Original Data ---")
    for item in test_events_data:
        print(item)

    print("\n--- 1. Filter by single venue: 'Lee\\'s Palace' ---")
    filtered_1 = EventFilter.filter_events_data(test_events_data, venue_name="Lee's Palace")
    for item in filtered_1:
        print(item)

    print("\n--- 2. Filter by list of venues: ['Lee\\'s Palace', 'The Cameron House'] ---")
    filtered_2 = EventFilter.filter_events_data(test_events_data, venue_name=["Lee's Palace", "The Cameron House"])
    for item in filtered_2:
        print(item)
    
    print("\n--- 3. Filter for events after March 1, 2026 ---")
    filtered_3 = EventFilter.filter_events_data(test_events_data, after_timestamp=datetime(2026, 3, 1))
    for item in filtered_3:
        print(item)
    
    print("\n--- 4. Filter for events at 'The Horseshoe Tavern' after March 1, 2026 ---")
    filtered_4 = EventFilter.filter_events_data(
        test_events_data, 
        venue_name="The Horseshoe Tavern", 
        after_timestamp=datetime(2026, 3, 1)
    )
    for item in filtered_4:
        print(item)

    print("\n--- 5. No filters (should return all events) ---")
    filtered_5 = EventFilter.filter_events_data(test_events_data)
    # This will return all events because the timestamp filter only runs if a timestamp is provided.
    # The No Timestamp Band event will be filtered out if a timestamp is provided.
    for item in filtered_5:
        print(item)

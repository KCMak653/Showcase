from datetime import datetime

MIN_SIMILARITY = 70 # Similarity rating for fuzzywuzzy
MIN_TRACKS = 2
VENUES = ['horseshoe_tavern']
start_date = datetime.now().date()
# end_date = datetime.strptime('2024-04-01', '%Y-%m-%d').date()
end_date = None
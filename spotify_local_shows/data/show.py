
# Data class containing show information
# A show is a singular band
class Show:

    def __init__(self, band_name, show_date, show_time):
        self.band_name = band_name
        self.show_date = show_date
        self.show_time = show_time

    def get_band_name(self):
        return self.band_name
    
    def get_show_date(self):
        return self.show_date
    
    def get_show_time(self):
        return self.show_time


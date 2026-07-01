from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

class SupabaseDBIO:
    def authenticate(self):
        url = os.environ["SUPABASE_URL"]
        key = os.environ["SUPABASE_KEY"]

        supabase = create_client(url, key)

if __name__ == "__main__":
    supabase_db_io = SupabaseDBIO()
    supabase_db_io.authenticate()
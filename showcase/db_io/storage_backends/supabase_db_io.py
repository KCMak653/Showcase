from supabase import create_client
import os

class SupabaseDBIO:
    def authenticate(self):
        url = os.environ["SUPABASE_URL"]
        key = os.environ["SUPABASE_KEY"]

        supabase = create_client(url, key)

if __name__ == "__main__":
    from showcase.settings import load_env

    load_env()
    supabase_db_io = SupabaseDBIO()
    supabase_db_io.authenticate()
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

def get_client():
    url: str = os.environ.get("host")
    password: str = os.environ.get("password")
    supabase: Client = create_client(url, password)
    return supabase

db = get_client()

if __name__ == "__main__":
    print(
        db.table('subsections')
        .select("keyphrases")
        .eq('section_id', '04-02')
        .eq('subsection', 1)
        .execute()
        .data
        )
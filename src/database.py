import os
from supabase import create_client, Client


def get_client():
    url: str = os.getenv("SUPABASE_HOST")
    password: str = os.getenv("SUPABASE_PASSWORD")
    supabase: Client = create_client(url, password)
    return supabase


db = get_client()

if __name__ == "__main__":
print(db.table("subsections")
        .select("keyphrases")
        .data[0])

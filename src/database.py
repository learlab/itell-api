import os
from supabase import create_client, Client
from models.textbook import TextbookNames


def get_client(textbook_name: TextbookNames):
    url: str = os.getenv(f"{textbook_name.name}_HOST")
    password: str = os.getenv(f"{textbook_name.name}_PASSWORD")
    supabase: Client = create_client(url, password)
    return supabase


if __name__ == "__main__":
    db = get_client(TextbookNames.MACRO_ECON)
    print(db.table("subsections").select("keyphrases").data[0])

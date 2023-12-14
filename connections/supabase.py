import os
from supabase.client import create_client, Client
from models.textbook import TextbookNames


def get_client(textbook_name: TextbookNames):
    url: str = os.environ[f"{textbook_name.name}_HOST"]
    password: str = os.environ[f"{textbook_name.name}_PASSWORD"]
    supabase: Client = create_client(url, password)
    return supabase

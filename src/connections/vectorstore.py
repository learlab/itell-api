import os
from supabase.client import create_client, Client


def get_vector_store():
    url: str = os.environ["VECTOR_HOST"]
    key: str = os.environ["VECTOR_KEY"]
    supabase: Client = create_client(url, key)
    return supabase

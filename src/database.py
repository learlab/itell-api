import os
import json
import requests
from supabase.client import create_client, Client
from models.textbook import TextbookNames


class Strapi:
    url: str = os.environ["STRAPI_URL"]
    key: str = os.environ["STRAPI_KEY"]

    def fetch(self, query) -> dict:
        headers = {"Authorization": f"Bearer {self.key}"}
        response = requests.request("GET", self.url + query, headers=headers)
        return json.loads(response.text)


def get_strapi():
    return Strapi()


def get_client(textbook_name: TextbookNames):
    url: str = os.environ[f"{textbook_name.name}_HOST"]
    password: str = os.environ[f"{textbook_name.name}_PASSWORD"]
    supabase: Client = create_client(url, password)
    return supabase


def get_vector_store():
    url: str = os.environ["VECTOR_HOST"]
    key: str = os.environ["VECTOR_KEY"]
    supabase: Client = create_client(url, key)
    return supabase

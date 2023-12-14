import os
import json
import requests


class Strapi:
    url: str = os.environ["STRAPI_URL"]
    key: str = os.environ["STRAPI_KEY"]

    def fetch(self, query) -> dict:
        headers = {"Authorization": f"Bearer {self.key}"}
        response = requests.request("GET", self.url + query, headers=headers)
        return json.loads(response.text)

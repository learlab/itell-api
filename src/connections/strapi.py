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

    # TODO: implement these and handle error cases to move this logic out of
    # the main src code
    def chunk_from_page_and_chunk_slug(self) -> None:
        raise NotImplementedError

    def text_meta_from_page_slug(self) -> None:
        raise NotImplementedError

    def chunks_from_page_slug(self) -> None:
        raise NotImplementedError
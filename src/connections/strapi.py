import os
import httpx


class Strapi:
    url: str = os.environ["STRAPI_URL"]
    key: str = os.environ["STRAPI_KEY"]

    async def fetch(self, query: str) -> dict:
        headers = {"Authorization": f"Bearer {self.key}"}
        async with httpx.AsyncClient() as client:
            r = await client.get(self.url + query, headers=headers)
            if r.status_code != 200:
                raise Exception(f"Error {r.status_code}: {r.reason_phrase}")
            content = r.json()
            if not isinstance(content, dict):
                raise TypeError(f"Expected dict, got {type(content)}")
            return content

    # TODO: implement these and handle error cases to move this logic out of
    # the main src code
    def chunk_from_page_and_chunk_slug(self) -> None:
        raise NotImplementedError

    def text_meta_from_page_slug(self) -> None:
        raise NotImplementedError

    def chunks_from_page_slug(self) -> None:
        raise NotImplementedError

    def log_request(self, request):
        print(f"Sending request to {request.url} with body {request.body}")

    def log_response(self, response):
        print(f"Received response {response.status_code} with body {response.content}")

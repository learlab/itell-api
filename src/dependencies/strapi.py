import os
from typing import AsyncGenerator, Optional, Union

import httpx
from cachetools import TTLCache, keys
from fastapi import HTTPException
from pydantic import ValidationError

from ..schemas.strapi import (
    Chunk,
    PageWithChunksResponse,
    PageWithVolumeResponse,
    Volume,
)
from ..utils.async_cache import acached


class Strapi:
    def __init__(self):
        """Initialize client."""
        self.url = os.environ["STRAPI_URL"]
        self.key = os.environ["STRAPI_KEY"]

        if not self.url.endswith("/"):
            self.url = self.url + "/"

        # Shared client instance allows for HTTP Connection Pooling
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {self.key}"}, timeout=httpx.Timeout(10.0)
        )

    def _hash_request_url(self, request: httpx.Request) -> str:
        """Since all requests are GET without any payload,
        we can cache the response based on the (hashable) URL."""
        return keys.hashkey(request.url)

    async def _get(
        self,
        url: str,
        params: dict,
    ) -> dict:
        req = self.client.build_request("GET", url, params=params)
        resp = await self._send(req)

        return resp.json()

    @acached(cache=TTLCache(maxsize=128, ttl=600), key=_hash_request_url)
    async def _send(self, request: httpx.Request) -> httpx.Response:
        try:
            resp = await self.client.send(request)
        except httpx.TimeoutException as err:
            raise HTTPException(status_code=504, detail=f"Strapi Timeout: {err}")
        if resp.status_code != 200:
            message = (
                f"Error connecting to Strapi {resp.status_code}:"
                f" {resp.reason_phrase}"
                f"\n{request.url}"
            )
            raise HTTPException(
                status_code=404,
                detail=message,
            )
        return resp

    async def get_entry(
        self,
        plural_api_id: str,
        document_id: int,
        populate: Optional[list[str]] = None,
        fields: Optional[list[str]] = None,
    ) -> dict:
        """Get entry by id."""
        populate_param: dict = self._stringify_parameters("populate", populate)
        fields_param: dict = self._stringify_parameters("fields", fields)
        params: dict = {**populate_param, **fields_param}
        url: str = f"{self.url}api/{plural_api_id}/{document_id}"
        return await self._get(url, params)  # type: ignore

    async def get_entries(
        self,
        plural_api_id: str,
        sort: Optional[list[str]] = None,
        filters: Optional[dict] = None,
        populate: Optional[Union[dict, list[str]]] = None,
        fields: Optional[list[str]] = None,
        pagination: Optional[dict] = None,
        publication_state: Optional[str] = None,
    ) -> dict:
        """Get list of entries."""
        sort_param: dict = self._stringify_parameters("sort", sort)
        filters_param: dict = self._stringify_parameters("filters", filters)
        populate_param: dict = self._stringify_parameters("populate", populate)
        fields_param: dict = self._stringify_parameters("fields", fields)
        pagination_param: dict = self._stringify_parameters("pagination", pagination)
        publication_state_param: dict = self._stringify_parameters(
            "publicationState", publication_state
        )
        url: str = f"{self.url}api/{plural_api_id}"
        params: dict = {
            **sort_param,
            **filters_param,
            **pagination_param,
            **populate_param,
            **fields_param,
            **publication_state_param,
        }
        return await self._get(url, params)

    def _stringify_parameters(
        self, name: str, parameters: Union[dict, list[str], str, None]
    ) -> dict:
        """Stringify dict for query parameters."""
        if type(parameters) is dict:
            return {name + k: v for k, v in self._flatten_parameters(parameters)}
        elif type(parameters) is str:
            return {name: parameters}
        elif type(parameters) is list:
            return {f"{name}[{i}]": p for i, p in enumerate(parameters)}
        else:
            return {}

    def _flatten_parameters(self, parameters: dict):
        """Flatten parameters dict for query."""
        for key, value in parameters.items():
            if isinstance(value, dict):
                for key1, value1 in self._flatten_parameters(value):
                    yield f"[{key}]{key1}", value1
            else:
                yield f"[{key}]", value

    async def get_chunk(self, page_slug: str, chunk_slug: str) -> Chunk:
        """Used for answer scoring.
        Should return a component dictionary."""
        json_response = await self.get_entries(
            plural_api_id="pages",
            filters={"Slug": {"$eq": page_slug}},
            populate={
                "Content": {
                    "on": {
                        "page.chunk": {"filters": {"Slug": {"$eq": chunk_slug}}},
                        "page.plain-chunk": {"filters": {"Slug": {"$eq": chunk_slug}}},
                        "page.video": {"filters": {"Slug": {"$eq": chunk_slug}}},
                    }
                }
            },
        )

        try:
            page_with_chunks = PageWithChunksResponse(**json_response)
        except ValidationError as error:
            raise HTTPException(
                status_code=404,
                detail=f"Chunk '{chunk_slug}' not found in page '{page_slug}'. {error}",
            )

        return page_with_chunks.data[0].content[0]

    async def get_text_meta(self, page_slug) -> Volume:
        json_response = await self.get_entries(
            plural_api_id="pages",
            filters={"Slug": {"$eq": page_slug}},
            populate=["Volume"],
        )

        try:
            page_with_text = PageWithVolumeResponse(**json_response)
        except ValidationError as error:
            raise HTTPException(
                status_code=404,
                detail=f"No parent text found for {page_slug}. {error}",
            )

        text_meta = page_with_text.data[0].volume

        return text_meta

    async def get_chunks(self, page_slug: str) -> list[Chunk]:
        """Used for summary scoring.
        Should return a list of component dictionaries."""
        json_response = await self.get_entries(
            plural_api_id="pages",
            filters={"Slug": {"$eq": page_slug}},
            populate="Content",
        )

        try:
            page_with_chunks = PageWithChunksResponse(**json_response)
        except ValidationError as error:
            print(json_response)
            raise HTTPException(
                status_code=404,
                detail=f"No chunks found for {page_slug}. {error}",
            )

        return page_with_chunks.data[0].content


async def get_strapi() -> AsyncGenerator[Strapi, None]:
    strapi = Strapi()
    try:
        yield strapi
    finally:
        await strapi.client.aclose()

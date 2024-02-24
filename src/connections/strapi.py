from ..models.strapi import Chunk, PageWithChunks, PageWithText, Text

import os
import httpx
from typing import Union, Optional
from pydantic import ValidationError
from fastapi import HTTPException
import sentry_sdk as sentry


class Strapi:
    url: str = os.environ["STRAPI_URL"]
    key: str = os.environ["STRAPI_KEY"]

    def __init__(self):
        """Initialize client."""
        if not self.url.endswith("/"):
            self.url = self.url + "/"
        self.headers = {"Authorization": f"Bearer {self.key}"}

    async def _get(self, url: str, params: dict) -> dict:
        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
            try:
                r = await client.get(url, headers=self.headers, params=params)
            except httpx.TimeoutException as err:
                sentry.capture_exception(err)
                raise HTTPException(status_code=504, detail=f"Strapi Timeout: {err}")
            if r.status_code != 200:
                message = (
                    f"Error connecting to Strapi {r.status_code}: {r.reason_phrase}"
                )
                sentry.capture_message(message)
                raise HTTPException(
                    status_code=404,
                    detail=(message),
                )
            result: dict = r.json()
            return result

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
            filters={"slug": {"$eq": page_slug}},
            populate={"Content": {"filters": {"Slug": {"$eq": chunk_slug}}}},
        )

        try:
            return PageWithChunks(**json_response).data[0].attributes.Content[0]
        except ValidationError as error:
            sentry.capture_exception(error)
            raise HTTPException(status_code=404, detail=str(error))

    async def get_text_meta(self, page_slug) -> Text:
        json_response = await self.get_entries(
            plural_api_id="pages",
            filters={"slug": {"$eq": page_slug}},
            populate=["text"],
        )

        try:
            text_meta = (
                PageWithText(**json_response).data[0].attributes.text.data.attributes
            )
        except (AttributeError, ValidationError) as error:
            sentry.capture_exception(error)
            raise HTTPException(
                status_code=404,
                detail=f"No parent text found for {page_slug}\n\n{error}",
            )

        if text_meta.Title is None:
            message = "Requested page does not have a parent text with a title."
            sentry.capture_message(message)
            raise HTTPException(status_code=404, detail=message)

        if text_meta.slug is None:
            message = "Requested page does not have a parent text with a slug."
            sentry.capture_message(message)
            raise HTTPException(status_code=404, detail=message)

        return text_meta

    async def get_chunks(self, page_slug: str) -> list[Chunk]:
        """Used for summary scoring.
        Should return a list of component dictionaries."""
        json_response = await self.get_entries(
            plural_api_id="pages",
            filters={"slug": {"$eq": page_slug}},
            populate={"Content": "*"},
        )
        try:
            return PageWithChunks(**json_response).data[0].attributes.Content
        except ValidationError as error:
            sentry.capture_exception(error)
            raise HTTPException(status_code=404, detail=str(error))

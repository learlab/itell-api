import os
import httpx
from typing import Union, Optional


class Strapi:
    url: str = os.environ["STRAPI_URL"]
    key: str = os.environ["STRAPI_KEY"]

    def __init__(self):
        """Initialize client."""
        if not self.url.endswith("/"):
            self.url = self.url + "/"
        self.headers = {"Authorization": f"Bearer {self.key}"}

    async def get(self, url: str, params: dict) -> dict:
        async with httpx.AsyncClient() as client:
            r = await client.get(url, headers=self.headers, params=params)
            if r.status_code != 200:
                raise Exception(f"Error {r.status_code}: {r.reason_phrase}")
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
        return await self.get(url, params)  # type: ignore

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
        return await self.get(url, params)

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

    # TODO: implement these and handle error cases to move this logic out of
    # the main src/*.py code
    def chunk_from_page_and_chunk_slug(self) -> dict[str, Union[int, str]]:
        """Used for answer scoring.
        Should return a component dictionary."""
        raise NotImplementedError

    def text_meta_from_page_slug(self) -> None:
        raise NotImplementedError

    def chunks_from_page_slug(self) -> list[dict[str, Union[int, str]]]:
        """Used for summary scoring.
        Should return a list of component dictionaries."""
        raise NotImplementedError

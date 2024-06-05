from ..models.api_keys import CreateAPIKeyInput, DeleteAPIKeyInput

from fastapi import APIRouter, Response
from .logging_router import LoggingRoute
from ..api_keys import create_new_api_key, delete_api_key

router = APIRouter(route_class=LoggingRoute)


@router.post("/generate/api_key")
async def generate_api_key(input_body: CreateAPIKeyInput) -> Response:
    """Creates an API key for the Content Management System."""
    return await create_new_api_key(input_body)


@router.post("/delete/api_key")
async def delete_api_key_endpoint(input_body: DeleteAPIKeyInput) -> Response:
    """Deletes an API key for the Content Management System."""
    return await delete_api_key(input_body)

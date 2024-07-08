from fastapi import APIRouter, Request, Response

from ..services.api_keys import create_new_api_key, delete_api_key
from ..schemas.api_keys import CreateAPIKeyInput, DeleteAPIKeyInput
from ..logging.logging_router import LoggingRoute

router = APIRouter(route_class=LoggingRoute)


@router.post("/generate/api_key")
async def generate_api_key(
    input_body: CreateAPIKeyInput,
    request: Request,
) -> Response:
    """Creates an API key for the Content Management System."""
    supabase = request.app.state.supabase
    return await create_new_api_key(input_body, supabase)


@router.post("/delete/api_key")
async def delete_api_key_endpoint(
    input_body: DeleteAPIKeyInput,
    request: Request,
) -> Response:
    """Deletes an API key for the Content Management System."""
    supabase = request.app.state.supabase
    return await delete_api_key(input_body, supabase)

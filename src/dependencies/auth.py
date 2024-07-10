from typing import Annotated

from cachetools import TTLCache, keys
from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import APIKeyHeader

from ..schemas.api_keys import AuthEntry
from ..utils.async_cache import acached
from .supabase import SupabaseClient

api_key_header = APIKeyHeader(name="API-Key")


def hash_api_key(token: str, request) -> str:
    """Hash the API key for caching, ignoring the Supabase dependency."""
    return keys.hashkey(token)


@acached(cache=TTLCache(maxsize=1024, ttl=600), key=hash_api_key)
async def get_role(
    token: Annotated[str, Security(api_key_header)],
    request: Request,
) -> str:
    supabase: SupabaseClient = request.app.state.supabase
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
        )

    response = (
        await supabase.table("api_keys")
        .select("role", "nickname")
        .eq("api_key", token)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
        )

    try:
        auth_entry = AuthEntry(**response.data[0])
    except IndexError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
        )
    except ValueError as e:  # Model validation failed
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Invalid response from database during authentication. {e}",
        )

    # Add nickname to (global) request state for use in logging
    request.state.auth = auth_entry

    return auth_entry


async def developer_role(
    auth: Annotated[AuthEntry, Depends(get_role)],
) -> str:

    if not auth.role == "developer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource",
        )

    return auth

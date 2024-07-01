from typing import Annotated

from cachetools import TTLCache, keys
from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import APIKeyHeader

from .async_cache import acached
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
        await supabase.table("api_keys").select("role").eq("api_key", token).execute()
    )

    role = response.data

    if not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
        )

    return role[0]["role"]


async def developer_role(
    role: Annotated[str, Depends(get_role)],
) -> str:

    if not role == "developer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource",
        )

    return role

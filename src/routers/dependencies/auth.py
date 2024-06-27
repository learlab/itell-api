from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from cachetools import TTLCache, keys
from .supabase import SupabaseDep
from .async_cache import acached

api_key_header = APIKeyHeader(name="API-Key")


def hash_api_key(supabase: SupabaseDep, api_key_header: str) -> str:
    '''Hash the API key for caching, ignoring the Supabase dependency.'''
    return keys.hashkey(api_key_header)


@acached(cache=TTLCache(maxsize=1024, ttl=600), key=hash_api_key)
async def get_role(
    supabase: SupabaseDep,
    api_key_header: str = Security(api_key_header),
) -> str:
    if not api_key_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
        )

    response = (
        await supabase
        .table("api_keys")
        .select("role")
        .eq("api_key", api_key_header)
        .execute()
    )

    role = response.data

    if not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
        )

    return role[0]["role"]


async def developer_role(
    supabase: SupabaseDep,
    api_key_header: str = Security(api_key_header),
) -> str:

    role = await get_role(supabase, api_key_header)

    if not role == "developer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource",
        )

    return role

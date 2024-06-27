from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from cachetools import cached, TTLCache
from .supabase import SupabaseDep

api_key_header = APIKeyHeader(name="API-Key")


@cached(cache=TTLCache(maxsize=1024, ttl=600))
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

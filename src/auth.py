from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from .connections.vectorstore import get_vector_store
from cachetools import cached, TTLCache

api_key_header = APIKeyHeader(name="API-Key")


@cached(cache=TTLCache(maxsize=1024, ttl=600))
def get_role(api_key_header: str = Security(api_key_header)):
    if not api_key_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
        )

    db = get_vector_store()

    role = (
        db.table("api_keys").select("role").eq(
            "api_key", api_key_header).execute().data
    )

    if not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
        )

    return role[0]["role"]


def developer_role(api_key_header: str = Security(api_key_header)):
    role = get_role(api_key_header)

    if not role == "developer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource",
        )

    return role

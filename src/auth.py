from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from .connections.vectorstore import get_vector_store

api_key_header = APIKeyHeader(name="API-Key")


def get_role(api_key_header: str = Security(api_key_header)):
    db = get_vector_store()

    role = (
        db.table("api_keys").select("role").eq("api_key", api_key_header).execute().data
    )

    if role:
        return role[0]["role"]
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid API key"
    )


def developer_role(api_key_header: str = Security(api_key_header)):
    role = get_role(api_key_header)

    if role == "developer":
        return role
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to access this resource",
    )

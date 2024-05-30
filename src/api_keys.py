from .models.api_keys import CreateAPIKeyInput, DeleteAPIKeyInput
from fastapi import Response, HTTPException
from .connections.vectorstore import get_vector_store

async def create_new_api_key(api_key: CreateAPIKeyInput) -> Response:
    db = get_vector_store()
    
    if api_key.role not in ["developer", "deployment"]:
        raise HTTPException(status_code=400, detail="Role must be 'developer' or 'deployment'")

    upsert_response = (
        db.table("api_keys")
        .upsert(
            {
                "nickname": api_key.nickname,
                "role": api_key.role,
            }
        )
        .execute()
    )

    return Response(content=upsert_response.data[0]["api_key"], status_code=201)

async def delete_api_key(api_key: DeleteAPIKeyInput) -> Response:
    db = get_vector_store()

    delete_response = (
        db.table("api_keys")
        .delete()
        .eq("api_key", api_key.api_key)
        .execute()
    )

    return Response(content=delete_response.data[0]["api_key"], status_code=200)
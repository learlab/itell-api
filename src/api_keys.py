from .models.api_keys import CreateAPIKeyInput, DeleteAPIKeyInput
from .routers.dependencies.supabase import SupabaseClient

from fastapi import Response, HTTPException


async def create_new_api_key(
    api_key: CreateAPIKeyInput,
    supabase: SupabaseClient,
) -> Response:
    if api_key.role not in ["developer", "deployment"]:
        raise HTTPException(
            status_code=400, detail="Role must be 'developer' or 'deployment'"
        )

    upsert_response = (
        await supabase.table("api_keys")
        .upsert(
            {
                "nickname": api_key.nickname,
                "role": api_key.role,
            }
        )
        .execute()
    )

    return Response(content=upsert_response.data[0]["api_key"], status_code=201)


async def delete_api_key(
    api_key: DeleteAPIKeyInput,
    supabase: SupabaseClient,
) -> Response:
    delete_response = (
        await supabase
        .table("api_keys")
        .delete()
        .eq("api_key", api_key.api_key)
        .execute()
    )

    return Response(content=delete_response.data[0]["api_key"], status_code=200)

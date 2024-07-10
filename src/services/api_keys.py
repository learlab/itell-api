from fastapi import HTTPException, Response

from ..dependencies.supabase import SupabaseClient
from ..schemas.api_keys import AuthEntry, CreateAPIKeyInput, DeleteAPIKeyInput


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

    auth_entry = AuthEntry(**upsert_response.data[0])

    return Response(content=auth_entry.api_key, status_code=201)


async def delete_api_key(
    api_key: DeleteAPIKeyInput,
    supabase: SupabaseClient,
) -> Response:
    delete_response = (
        await supabase.table("api_keys")
        .delete()
        .eq("api_key", api_key.api_key)
        .execute()
    )

    auth_entry = AuthEntry(**delete_response.data[0])

    return Response(content=auth_entry.api_key, status_code=200)

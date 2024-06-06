import pytest

# Fixture that deletes the test_key if it exists
@pytest.fixture
async def delete_test_key(db):
    current_keys = (
        db.table("api_keys")
        .select("*")
        .eq("nickname", "test_key")
        .execute()
        .data
    )

    if len(current_keys) > 0:
        db.table("api_keys").delete().eq("nickname", "test_key").execute()

async def test_create_new_api_key(client, db, delete_test_key):
    current_keys = (
        db.table("api_keys")
        .select("*")
        .eq("nickname", "test_key")
        .execute()
        .data
    )

    assert len(current_keys) == 0

    response = await client.post(
        "/generate/api_key",
        json={
            "nickname": "test_key",
            "role": "developer",
        },
    )

    assert response.status_code == 201

    current_keys = (
        db.table("api_keys")
        .select("*")
        .eq("nickname", "test_key")
        .execute()
        .data
    )

    assert len(current_keys) == 1
    assert current_keys[0]["nickname"] == "test_key"
    assert current_keys[0]["role"] == "developer"
    assert "api_key" in current_keys[0]

async def test_delete_api_key(client, db):
    current_keys = (
        db.table("api_keys")
        .select("*")
        .eq("nickname", "test_key")
        .execute()
        .data
    )

    assert len(current_keys) == 1

    api_key = current_keys[0]["api_key"]


    response = await client.post(
        "/delete/api_key",
        json={
            "api_key": api_key
        },
    )

    assert response.status_code == 200

    current_keys = (
        db.table("api_keys")
        .select("*")
        .eq("nickname", "test_key")
        .execute()
        .data
    )

    assert len(current_keys) == 0
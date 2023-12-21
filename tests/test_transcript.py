async def test_generate_transcript(client):
    response = await client.post(
        "/generate/transcript",
        json={
            "url": "https://www.youtube.com/watch?v=Cqbleas1mmo",
            "start_time": 50,
            "end_time": 200,
        },
    )
    assert response.status_code == 200

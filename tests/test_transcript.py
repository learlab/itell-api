def test_generate_transcript(client):
    response = client.post(
        "/generate/transcript",
        json={
            "url": "https://www.youtube.com/watch?v=Cqbleas1mmo",
            "start_time": 50,
            "end_time": 200,
        },
    )
    print("Transcript:", response.json())
    assert response.status_code == 200

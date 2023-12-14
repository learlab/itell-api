def test_short_answer(client):
    response = client.post(
        "/score/answer",
        json={
            "textbook_name": "macroeconomics-2e",
            "chapter_index": 7,
            "section_index": 4,
            "subsection_index": 0,
            "answer": "The natural rate of unemployment.",
        },
    )
    print("Short answer test results:", response.json())
    return

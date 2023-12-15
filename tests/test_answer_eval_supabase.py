def test_short_answer_supabase(client):
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
    assert response.status_code == 200


def test_short_answer_missing_subsection_index(client):
    response = client.post(
        "/score/answer",
        json={
            "textbook_name": "macroeconomics-2e",
            "chapter_index": 7,
            "section_index": 4,
            "answer": "The natural rate of unemployment.",
        },
    )
    assert response.status_code == 422

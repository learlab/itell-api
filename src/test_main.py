from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_score_main():
    response = client.post(
        "/score",
        json={
            'source': 'The most important topic in economics is supply and demand.',
            'text': 'Economics is about supply and demand.',
        }
    )
    print(response.json())

def test_containment():
    response = client.post(
        "/score",
        json={
            'source': 'The most important topic in economics is supply and demand',
            'text': 'The most important topic in economics is supply and demand',
        }
    )
    assert response.json()['containment'] == 1.0

if __name__ == "__main__":
    test_read_main()
    test_score_main()
    test_containment()
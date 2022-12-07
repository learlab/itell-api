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
            'section_number': '01-1',
            'summary': 'Economics is about supply and demand.',
        }
    )
    print(response.json())

def test_containment():
    response = client.post(
        "/score",
        json={
            'section_number': '01-1',
            'summary': '''Think about it this way: In 2015 the labor force in the United States contained 
            over 158 million workers, according to the U.S. Bureau of Labor Statistics. 
            The total land area was 3,794,101 square miles. While these are certainly large numbers, 
            they are not infinite. Because these resources are limited, so are the numbers of goods 
            and services we produce with them. Combine this with the fact that human wants seem to be 
            virtually infinite, and you can see why scarcity is a problem.','''
        }
    )
    assert response.json()['containment'] > 0.9

if __name__ == "__main__":
    test_read_main()
    test_score_main()
    test_containment()
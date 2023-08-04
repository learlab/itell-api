from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

def test_read_gpu():
    response = client.get("/gpu")
    print('Read GPU:', response.json())

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200

def test_QA():
    response = client.post(
        "/qascore",
        json={
            'textbook_name': 'macroeconomics-2e',
            'chapter_index': 1, 
            'section_index': 1, 
            'subsection_index': 1, 
            'QA_response':'happy'
        }
    )
    print('QA test results:', response.json())


if __name__ == "__main__":
    test_read_main()
    test_read_gpu()
    test_QA()

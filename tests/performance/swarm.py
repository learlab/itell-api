# pip install locust
# python -m src.app
# locust -f tests/performance/swarm.py

import os
import random

import srsly
from locust import HttpUser, between, task


class PerformanceTests(HttpUser):
    wait_time = between(1, 3)
    host = "http://localhost:8001"
    headers = {
        "Content-Type": "application/json",
        "API-Key": os.getenv("ITELL_API_KEY"),
    }

    # CAUTION! This data may contain private information.
    chat_data = list(srsly.read_jsonl("tests/performance/data/chat.jsonl"))
    summ_data = list(srsly.read_jsonl("tests/performance/data/summary.jsonl"))
    cri_data = list(srsly.read_jsonl("tests/performance/data/cri.jsonl"))

    @task(1)
    def test_health(self):
        self.client.get("/")

    @task(2)
    def test_chat(self):
        sample = random.choice(self.chat_data)
        payload = {
            "page_slug": sample["page_slug"],
            "message": sample["message"],
            "history": sample["history"],
        }
        self.client.post("/chat", json=payload, headers=self.headers)

    @task(4)
    def test_score_summary_stairs(self):
        sample = random.choice(self.summ_data)
        payload = {
            "page_slug": sample["page_slug"],
            "summary": sample["summary"],
        }
        self.client.post("/score/summary/stairs", json=payload, headers=self.headers)

    @task(2)
    def test_chat_cri(self):
        sample = random.choice(self.cri_data)
        payload = {
            "page_slug": sample["page_slug"],
            "chunk_slug": sample["chunk_slug"],
            "student_response": sample["answer"],
        }
        self.client.post("/chat/CRI", json=payload, headers=self.headers)

    # @task(4)
    # def test_score_answer(self):
    #     sample = random.choice(self.cri_data)
    #     payload = {
    #         "page_slug": sample["page_slug"],
    #         "chunk_slug": sample["chunk_slug"],
    #         "student_response": sample["answer"],
    #     }
    #     self.client.post("/score/answer", json=payload, headers=self.headers)

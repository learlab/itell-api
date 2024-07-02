import datetime
import httpx
import asyncio
import os


async def save_streaming_response(response, file_path, start_time):
    print(response.headers["x-process-time"])


async def send_post_request(url, json_data, file_path):
    start_time = datetime.datetime.now()
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=json_data, timeout=None, headers={"API-Key": os.environ["ITELL_API_KEY"]})
        if response.status_code == 200:
            await save_streaming_response(response, file_path, start_time)
        else:
            print(f"Request failed with status code: {response.status_code}")


async def main(url, num_requests, body):
    tasks = [send_post_request(
        url, body, f"output/output_{i}.txt") for i in range(num_requests)]
    results = await asyncio.gather(*tasks)
    return results

url = "http://127.0.0.1:8001/chat"
num_requests = 20  # Number of concurrent requests to send

results = asyncio.run(main(url, num_requests, {
                      "page_slug": "emotional", "message": "What are emotions about?"}))

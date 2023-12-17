import httpx

class BaseClient(object):
    def __init__(self, host, port, timeout=10):
        self.host = host
        self.port = port
        self.timeout = timeout

    def log_request(self, request):
        print(f"Sending request to {request.url} with body {request.body}")
    
    def log_response(self, response):
        print(f"Received response {response.status_code} with body {response.content}")
        
    def connect(self):
        raise NotImplementedError

    def send(self, data):
        raise NotImplementedError

    def receive(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError
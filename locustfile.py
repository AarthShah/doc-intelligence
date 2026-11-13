from locust import HttpUser, task, between


class DocumentIntelligenceUser(HttpUser):
    """Locust user simulating document ingestion traffic."""
    
    wait_time = between(1, 3)

    @task(3)
    def ingest_document(self):
        """Send a POST request to the /ingest endpoint with a multipart/form-data file payload."""
        files = {
            "file": ("sample.txt", b"This is a sample document content used for load testing the ingestion endpoint.", "text/plain")
        }
        with self.client.post("/ingest", files=files, catch_response=True) as response:
            if response.status_code in (200, 201):
                response.success()
            else:
                response.failure(f"Failed with status code: {response.status_code}")

    @task(5)
    def search_documents(self):
        """Send a GET request to the /search endpoint with a sample query."""
        params = {"q": "sample document content"}
        with self.client.get("/search", params=params, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed with status code: {response.status_code}")

    @task(1)
    def test_rate_limit_burst(self):
        """Send a burst of requests to trigger the rate limiter."""
        params = {"q": "rate limit test"}
        for _ in range(10):
            with self.client.get("/search", params=params, catch_response=True) as response:
                if response.status_code in (200, 429):
                    response.success()
                else:
                    response.failure(f"Unexpected status code: {response.status_code}")

    @task(1)
    def test_rate_limit_high_frequency(self):
        """Send rapid requests to the rate-limited endpoint to verify 429 responses."""
        params = {"q": "rate limit high frequency"}
        for _ in range(20):
            with self.client.get("/search", params=params, catch_response=True) as response:
                if response.status_code in (200, 429):
                    response.success()
                else:
                    response.failure(f"Unexpected status code: {response.status_code}")

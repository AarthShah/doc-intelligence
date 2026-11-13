from locust import HttpUser, task, between


class DocumentIntelligenceUser(HttpUser):
    """Locust user simulating document ingestion traffic."""
    
    wait_time = between(1, 3)

    @task
    def ingest_document(self):
        """Send a POST request to the /ingest endpoint with a sample document payload."""
        payload = {
            "content": "This is a sample document content used for load testing the ingestion endpoint.",
            "metadata": {
                "source": "locust-load-test",
                "author": "perf-tester"
            }
        }
        with self.client.post("/ingest", json=payload, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed with status code: {response.status_code}")

from locust import HttpUser, task, between


class DocumentIntelligenceUser(HttpUser):
    """Locust user simulating document ingestion traffic."""
    
    wait_time = between(1, 3)

    @task
    def ingest_document(self):
        """Send a POST request to the /ingest endpoint with a multipart/form-data file payload."""
        files = {
            "file": ("sample.txt", b"This is a sample document content used for load testing the ingestion endpoint.", "text/plain")
        }
        with self.client.post("/ingest", files=files, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed with status code: {response.status_code}")

    @task
    def search_documents(self):
        """Send a GET request to the /search endpoint with a sample query."""
        params = {"q": "sample document content"}
        with self.client.get("/search", params=params, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed with status code: {response.status_code}")

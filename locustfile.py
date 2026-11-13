from locust import HttpUser, task, between


class DocumentIntelligenceUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def ingest_document(self):
        payload = {
            "content": "This is a sample document content used for load testing the ingestion endpoint.",
            "metadata": {
                "source": "locust-load-test",
                "author": "perf-tester"
            }
        }
        self.client.post("/ingest", json=payload)

import os
import requests
from typing import List, Optional
from doc_intelligence.models import LLMProvider


class HuggingFaceInferenceAPIProvider(LLMProvider):
    """
    HuggingFace Inference API embedding provider.
    """

    def __init__(self, model_name: str, api_key: Optional[str] = None):
        self.model_name = model_name
        self.api_key = api_key or os.getenv("HUGGINGFACE_API_KEY") or os.getenv("HF_TOKEN")
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model_name}"

    def embed(self, texts: List[str]) -> List[List[float]]:
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {"inputs": texts}
        response = requests.post(self.api_url, headers=headers, json=payload)
        
        if response.status_code != 200:
            raise RuntimeError(
                f"HuggingFace API request failed with status {response.status_code}: {response.text}"
            )

        data = response.json()
        
        # Handle cases where the output format might be a list of embeddings or nested lists
        if isinstance(data, list):
            # Some models return a list of floats directly if single input, or list of lists
            if data and isinstance(data[0], (int, float)):
                return [data]
            return data
        elif isinstance(data, dict) and "error" in data:
            raise RuntimeError(f"HuggingFace API error: {data['error']}")
        
        raise RuntimeError(f"Unexpected response format from HuggingFace API: {data}")

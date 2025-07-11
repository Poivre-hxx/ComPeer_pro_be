import requests
import os

class SiliconFlowLLM:
    def __init__(self):
        self.api_key = os.getenv("SILICON_API_KEY", "sk-cjktrxbohzgcvvcgkeppefasertnysxdmerrowgadqkciews")
        self.base_url = os.getenv("SILICON_API_BASE", "https://api.siliconflow.cn/v1")
        self.model_name = os.getenv("SILICON_MODEL", "meta-llama/Llama-3.3-70B-Instruct")

    def chat(self, messages):
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.7
        }
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
from typing import Any
from google.genai import Client


class Agent:
    def __init__(self, system: str = "", client: Client = None, model: str = "gemini-2.5-flash"):
        self.system = system
        self.messages = []
        self.model = model

        if(client is None):
            self.client = Client()
        else:
            self.client = client

        if self.system:
            self.messages.append({"role": "system", "content": self.system})

    def execute(self):
        prompt = ""
        for msg in self.messages:
            prompt += f"{msg['role']}: {msg['content']}\n"

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )
        return response.text

    def __call__(self, message: str) -> Any:
        self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result
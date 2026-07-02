from google import genai
from google.genai import types
from agents.react_agent import ReactAgent

class GeminiReactAgent(ReactAgent):
    def __init__(self, system_prompt: str, llm_model: str):
        super().__init__(system_prompt, llm_model)
        self.client = genai.Client()
        self.chat = self.__create_chat__()

    def __create_chat__(self):
        config = types.GenerateContentConfig(
            system_instruction=self.system_prompt,
        )
        chat = self.client.chats.create(
            model=self.llm_model,
            config=config
        )
        return chat

    def _generate_response(self, prompt: str) -> str:
        response = self.chat.send_message(prompt)
        return response.text.strip()
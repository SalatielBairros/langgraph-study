from openai import OpenAI
from agents.react_agent import ReactAgent

class LMStudioReactAgent(ReactAgent):
    def __init__(self, system_prompt: str, llm_model: str = "local-model", base_url: str = "http://127.0.0.1:1234/v1"):
        super().__init__(system_prompt, llm_model)
        # O LM Studio expõe um servidor local compatível com a API da OpenAI na porta 1234
        self.client = OpenAI(base_url=base_url, api_key="lm-studio")
        self.messages = []

    def _reset_history(self):
        # Reinicia o histórico de mensagens a cada nova chamada, mantendo apenas o system prompt
        self.messages = [
            {"role": "system", "content": self.system_prompt}
        ]

    def _generate_response(self, prompt: str) -> str:
        self.messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.llm_model,
            messages=self.messages,
            temperature=0.5
        )
        
        message = response.choices[0].message
        
        # Alguns servidores e APIs (como atualizações recentes do LM Studio) 
        # separam o pensamento no campo 'reasoning_content'
        response_text = message.content.strip() if message.content else ""
        reasoning_content = getattr(message, 'reasoning_content', None)
        
        if reasoning_content:
            response_text = f"<think>\n{reasoning_content.strip()}\n</think>\n\n{response_text}"
        
        # Adicionando a resposta do modelo no histórico
        self.messages.append({"role": "assistant", "content": response_text})

        return response_text

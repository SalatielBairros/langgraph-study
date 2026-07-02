import re
from abc import ABC, abstractmethod

class ReactAgent(ABC):
    def __init__(self, system_prompt: str, llm_model: str):
        self.system_prompt = system_prompt
        self.llm_model = llm_model

    @abstractmethod
    def _generate_response(self, prompt: str) -> str:
        pass

    def _reset_history(self):
        pass

    def run_react_agent(self, 
                        input: str, 
                        action_call: callable,
                        max_iterations: int = 5,
                        log_callback: callable = None) -> str:
        
        def log(msg: str):
            print(msg)
            if log_callback:
                log_callback(msg)

        self._reset_history()
        current_prompt = input

        for i in range(max_iterations):
            response_text = self._generate_response(current_prompt)

            log(f"### Iteração {i+1}")
            log(f"**Modelo pensou/respondeu:**\n```\n{response_text}\n```\n")

            if "Resposta: " in response_text:
                return response_text.replace("Resposta:", "").strip()

            match = re.search(r"Ação:\s*(\w+):\s*(.*)", response_text)

            if match:
                action_name = match.group(1).strip()
                action_arg = match.group(2).strip()

                observacao = action_call(action_name, action_arg)
                if observacao is None:
                    break

                current_prompt = f"Observação: {observacao}\nResposta:"

                log(f"**Executou ação:** `{action_name}({action_arg})`")
                log(f"**Observação:** {observacao}\n")

            else:
                return f"Resposta: {response_text}"
        
        return "Erro: Limite máximo de iterações atingido sem uma resposta final."

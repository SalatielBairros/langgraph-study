from dotenv import load_dotenv
import os

load_dotenv()

import argparse
from produto_service import ProdutoService
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.agents.middleware import HumanInTheLoopMiddleware 
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.tools import StructuredTool
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langgraph.types import Command

PROMPT_REACT = """
Você é um assistente especializado exclusivamente no catálogo e inventário de produtos.

Suas diretrizes de comportamento:
1. Responda apenas a perguntas estritamente relacionadas a produtos, estoque, preços e listagens do inventário.
2. Se o usuário fizer qualquer pergunta fora desse escopo (assuntos gerais, outros temas), informe educadamente que você só pode responder a dúvidas relacionadas a produtos.
3. Utilize as ferramentas disponíveis sempre que precisar buscar informações atualizadas para responder ao usuário.
4. Seja conciso e direto em suas respostas finais.

Ferramentas disponíveis para uso automático:
- consultar_estoque: Verifica a quantidade de um item.
- consultar_preco_produto: Verifica o preço unitário de um item.
- listar_produtos: Traz a lista geral em formato JSON (exige um limite numérico).
""".strip()

SYSTEM_PROMPT = SystemMessage(
    content=PROMPT_REACT
)

service = ProdutoService()

MODEL = ChatGoogleGenerativeAI(
    model="models/gemini-2.5-flash",
    temperature=0.5,
)

tools = [
    StructuredTool.from_function(
        func=service.consultar_estoque,
        name="consultar_estoque"
    ),
    StructuredTool.from_function(
        func=service.consultar_preco_produto,
        name="consultar_preco_produto"
    ),
    StructuredTool.from_function(
        func=service.listar_produtos,
        name="listar_produtos"
    ),
    StructuredTool.from_function(
        func=service.secret_discount,
        name="secret_discount"
    )
]

DB_PATH = "state_store.db"

def print_formated_ai_message(message: str | list):
    if type(message) is list:
        if 'text' in message[-1]:
            print(message[-1]['text'])
        else:
            print(message[-1])
    else:
        print(message)

def interactive_chat(app):
    # O thread_id fixo garante que o SQLite carregue o histórico desta mesma conversa
    config = {"configurable": {"thread_id": "interactive_session_001"}}
    
    print("Assistente de Produtos pronto! Digite sua pergunta.")
    
    while True:
        pergunta = input("\nO que deseja saber? (Digite 'sair' para encerrar): ")
        
        if pergunta.lower() == "sair":
            print("Encerrando o chat...")
            break

        inputs = {"messages": [HumanMessage(content=pergunta)]}
        
        last_message = []
        
        for event in app.stream(inputs, config=config):
            for key, value in event.items():
                if value and "messages" in value:
                    last_message = value['messages'][-1].content

        state = app.get_state(config)
        while state.interrupts:
            hitl_req = state.interrupts[0].value
            decisions = []
            for req in hitl_req.get("action_requests", []):
                if req.get("name") == "secret_discount":
                    confirmacao = input(f"\nAplicação do desconto secreto solicitada para o preço R$ {req['args'].get('preco')}. Deseja aprovar? (s/n): ")
                    if confirmacao.lower() in ["s", "sim", "y", "yes"]:
                        decisions.append({"type": "approve"})
                    else:
                        decisions.append({"type": "reject"})
                else:
                    decisions.append({"type": "approve"})
            
            for event in app.stream(Command(resume={"decisions": decisions}), config=config):
                for key, value in event.items():
                    if value and "messages" in value:
                        last_message = value['messages'][-1].content
            
            state = app.get_state(config)

        print_formated_ai_message(last_message)


def execute_agent(model: BaseChatModel | None):
    if model is None:
        raise Exception("Model não pode ser None")

    with SqliteSaver.from_conn_string(DB_PATH) as checkpointer:
        hitl_middleware = HumanInTheLoopMiddleware(
            interrupt_on={
                "secret_discount": {
                    "allowed_decisions": ["approve", "reject"]
                }
            }
        )

        app = create_agent(
            model=model,
            tools=tools,
            system_prompt=SYSTEM_PROMPT,
            checkpointer=checkpointer,
            middleware=[hitl_middleware]
        )

        interactive_chat(app)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Executa o Agente ReAct utilizando diferentes provedores.")
    parser.add_argument(
        "--mode", 
        type=str, 
        choices=["gemini", "lmstudio"], 
        default="lmstudio",
        help="Escolha o modo de execução: 'gemini' (Google GenAI), 'lmstudio' (Modelos Locais) ou 'modelos_gemini' (Listar os modelos do Gemini)"
    )

    args = parser.parse_args()

    model = None
    if args.mode == "gemini":
        model = ChatGoogleGenerativeAI(
            model="models/gemini-2.5-flash",
            temperature=0.5,
        )
    elif args.mode == "lmstudio":
        model = ChatOpenAI(
            base_url="http://localhost:1234/v1",
            model="google_gemma-4-26b-a4b-qat",
            temperature=0.5,
        )
        pass
    else:
        raise ValueError(f"Modo desconhecido: {args.mode}. Escolha entre 'gemini' ou 'lmstudio'.")
    
    execute_agent(model)
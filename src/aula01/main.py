import os
import argparse
from dotenv import load_dotenv
from services.produto_service import ProdutoService
from agents.gemini_react_agent import GeminiReactAgent
from agents.lmstudio_react_agent import LMStudioReactAgent
from agents.react_agent import ReactAgent
from services.gemini_service import GeminiService

load_dotenv()

os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")


PROMPT_REACT = """
    Você funciona em um ciclo de Pensamento, Ação, Pausa e Observação.
    Ao final do ciclo, você fornece uma Resposta.
    Use "Pensamento" para descrever seu raciocínio.
    Use "Ação" para executar ferramentas - e então retorne "PAUSA".
    A "Observação" será o resultado da ação executada.
    Ações disponíveis:
        - consultar_estoque: retorna a quantidade disponível de um item no inventário (ex: "consultar_estoque: teclado")
        - consultar_preco_produto: retorna o preço unitário de um produto (ex: "consultar_preco_produto: mouse gamer")
        - listar_produtos: retorna uma lista de todos os produtos disponíveis no inventário, com seus preços e quantidades em estoque, passando o número máximo de produtos a serem listados (ex: "listar_produtos: 10"). Essa lista é retornada em formato JSON.
    Use "Resposta" para fornecer a resposta final ao usuário.
    IMPORTANTE: Não responda nada que não seja sobre os produtos. Se a pergunta não for sobre produtos, informe que você só pode responder perguntas relacionadas a produtos.

    Exemplo:
    Pergunta: Quantos monitores temos em estoque?
    Pensamento: Devo consultar a ação consultar_estoque para saber a quantidade de monitores.
    Ação: consultar_estoque: monitor
    PAUSA

    Observação: Temos 75 monitores em estoque.
    Resposta: Há 75 monitores em estoque.
""".strip()

service = ProdutoService()

def execute_actions(name: str, arg: str) -> str | None:
    if name == "consultar_estoque":
        return service.consultar_estoque(arg)
    elif name == "consultar_preco_produto":
        return service.consultar_preco_produto(arg)
    elif name == "listar_produtos":
        try:
            max_items = int(arg)
            produtos = service.listar_produtos(max_items=max_items)
            return str(produtos)
        except ValueError:
            return "O argumento para listar_produtos deve ser um número inteiro."
    return None

def run_benchmark(react_agent: ReactAgent, provider_name: str):
    llm_model_name = react_agent.llm_model.replace("models/", "").replace("/", "-")
    
    os.makedirs("output", exist_ok=True)
    file_path = f"output/{provider_name}_{llm_model_name}.md"
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"# Execução: {provider_name} ({llm_model_name})\n\n")

        def log_to_file(msg: str):
            f.write(msg + "\n")

        pergunta_1 = "Quantos mouses gamers estão no inventário?"

        log_to_file(f"## PERGUNTA 1: {pergunta_1}\n")
        print("\n"+"="*50 + "\n")
        print(f"*** PERGUNTA 1: {pergunta_1}***")
        
        resposta_1 = react_agent.run_react_agent(pergunta_1, execute_actions, log_callback=log_to_file)
        
        log_to_file(f"**RESPOSTA FINAL:** {resposta_1}\n\n---\n")
        print(f"\n**RESPOSTA:** {resposta_1}\n")

        print("\n"+"="*50 + "\n")

        pergunta_2 = "Se eu vender 5 mouses gamers, quanto em valor total de dinheiro eu ainda terei em estoque para vender?"
        
        log_to_file(f"## PERGUNTA 2: {pergunta_2}\n")
        print(f"*** PERGUNTA 2: {pergunta_2}***")

        resposta_2 = react_agent.run_react_agent(pergunta_2, execute_actions, max_iterations=10, log_callback=log_to_file)
        
        log_to_file(f"**RESPOSTA FINAL:** {resposta_2}\n")
        print(f"\n**RESPOSTA:** {resposta_2}\n")

        print("\n"+"="*50 + "\n")

        pergunta_3 = "Qual o ítem mais caro individualmente e qual o item cujo total em estoque possui o maior valor?"
        
        log_to_file(f"## PERGUNTA 3: {pergunta_3}\n")
        print(f"*** PERGUNTA 3: {pergunta_3}***")

        resposta_3 = react_agent.run_react_agent(pergunta_3, execute_actions, max_iterations=15, log_callback=log_to_file)
        
        log_to_file(f"**RESPOSTA FINAL:** {resposta_3}\n")
        print(f"\n**RESPOSTA:** {resposta_3}\n")

def interactive_chat(react_agent: ReactAgent):
    while True:
        pergunta = input("\n O que deseja saber? (Digite 'sair' para encerrar): ")
        
        if pergunta.lower() == "sair":
            print("Encerrando o chat...")
            return

        react_agent.run_react_agent(pergunta, execute_actions)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Executa o Agente ReAct utilizando diferentes provedores.")
    it = True
    parser.add_argument(
        "--mode", 
        type=str, 
        choices=["gemini", "lmstudio", "modelos_gemini"], 
        default="lmstudio",
        help="Escolha o modo de execução: 'gemini' (Google GenAI), 'lmstudio' (Modelos Locais) ou 'modelos_gemini' (Listar os modelos do Gemini)"
    )

    parser.add_argument(
        "--benchmark",
        help="Executa o benchmark com as perguntas predefinidas.",
        action="store_true"
    )
    
    args = parser.parse_args()

    if args.mode == "modelos_gemini":
        gemini_service = GeminiService()
        gemini_service.get_avaliable_chat_models()
        it = False
    
    elif args.mode == "gemini":
        agent = GeminiReactAgent(
            system_prompt=PROMPT_REACT,
            llm_model="models/gemma-4-26b-a4b-it"
        )
    elif args.mode == "lmstudio":
        agent = LMStudioReactAgent(
            system_prompt=PROMPT_REACT,
            llm_model="google_gemma-4-26b-a4b-qat"
        )
    else:
        raise ValueError(f"Modo desconhecido: {args.mode}. Escolha entre 'gemini', 'lmstudio' ou 'modelos_gemini'.")

    if args.benchmark:
        run_benchmark(agent, args.mode)
    elif it:
        print(f"Executando o chat interativo com o provedor: {args.mode}")
        interactive_chat(agent)
    
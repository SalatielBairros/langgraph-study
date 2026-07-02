# Estudando LangGrapth

Material realizado através do curso da Alura: LangGraph: Orquestrando agentes e multiagentes. No entanto, as referências foram atualizadas, código organizado e implementações para execução local feitas.

## Rodando com LM Studio

O projeto agora possui suporte para rodar modelos locais através do LM Studio, que provê uma API compatível com a da OpenAI.

### Passos para configurar o LM Studio:
1. Faça o download e instale o [LM Studio](https://lmstudio.ai/).
2. Abra o LM Studio e baixe o modelo LLM da sua preferência (ex: Gemma, Llama 3, Qwen, etc.).
3. Vá para a aba **"Local Server"** (ícone de servidor com o símbolo de duas setas ou um "< >" no menu lateral esquerdo).
4. No painel que aparecer, certifique-se de carregar o modelo baixado na parte superior.
5. Inicie o servidor clicando em **"Start Server"**. Por padrão, ele irá rodar na porta `1234` com o endpoint `http://127.0.0.1:1234/v1`.
6. Instale a biblioteca `openai` no seu ambiente Python (caso ainda não possua):
   ```bash
   pip install openai
   ```

### Testando os modelos

No arquivo `src/main.py`, foi criado o método `run_lmstudio()`. 
O `if __name__ == "__main__":` já está configurado para chamar essa função.

Para testar, basta rodar o comando:
```bash
python src/main.py
```
O agente vai usar o LM Studio rodando em background para processar e acionar as ferramentas.
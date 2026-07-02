# Regras para commit e push do projeto

Toda vez que uma operação de commit for solicitada ou que arquivos forem versionados no repositório, o agente deve **obrigatoriamente** seguir este checklist rigoroso antes de executar `git commit` ou `git push`:

## 1. Verificação de Chaves e Credenciais
- Rode `git diff --cached` para inspecionar todo o código que está prestes a ser commitado.
- Confirme que nenhuma chave do Firebase, chaves de API, senhas ou strings contendo "AIzaSy..." ou tokens de Service Account estão sendo "staged".
- Certifique-se de que nenhum arquivo listado como segredo no `.gitignore` (ex: `.env`, `firebase-key.json`) foi acidentalmente forçado pro cache.

## 2. Verificação de Pastas Proibidas
- Avalie o resultado do comando `git status`.
- Assegure-se de que pastas de cache, dependências ou compilação NÃO estão no pacote do commit, por exemplo:
  - `node_modules/`
  - Pastas de build (como `dist/`, `build/`)
  - Pastas de bibliotecas do Python se virtuais (ex: `.venv/`, `__pycache__/`)
- Verifique arquivos que estejam já no controle de versão, mas tenham sido adicionados no `.gitignore`. Eles precisam ser removidos do projeto para começarem a ser ignorados.

## 3. Verificação de Caminhos
- Verifique nas adições de código (`git diff --cached`) se algum caminho de arquivo no estilo absoluto (`/Users/...`, `C:\...`) vazou no código.
- Todos os caminhos devem ser relativos ao repositório ou construídos dinamicamente (ex: `__dirname`, `os.path`).

## 4. Execução e Push
- Considere para o commit e a mensagem tudo o que está pendente de commit no projeto (e que não foi eliminado pelas avaliações anteriores). Não olhe apenas para a última coisa que foi feita, mas para tudo o que tem pendente.
- **Somente se todas as verificações acima passarem com sucesso**, execute o bump de versão usando o script, adicione os arquivos atualizados ao stage (`git add .`), e execute o `git commit -m "..."`.
- Após o commit, execute `git push` se solicitado, certificando-se de estar na branch correta.
- Em caso de falha em alguma verificação, aborte o commit, reverta o `git add` dos arquivos sensíveis (`git restore --staged <file>`) e corrija o problema relatando ao usuário.
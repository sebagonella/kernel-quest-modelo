# Kernel Quest — modelo de entrada no M03C

Ponto de partida para quem entra no curso [Kernel Quest](https://github.com/sebagonella/kernel-quest-curso) no **módulo M03C**, com o jogo já organizado em camadas (estado ao fim do M03B).

> **Começando do zero?** Não use este modelo: comece pelo M00A. Criar o projeto e o repositório com as próprias mãos é parte do que o M00A e o M00B ensinam, e este modelo já traz as respostas do M00A ao M03B.

## Antes de começar

O que os módulos anteriores ensinam a instalar, e onde está o passo a passo no curso:

- **Python 3.12 e VS Code** com a extensão Python: M00A.
- **Chave do Gemini** (Google AI Studio), **Git** e **GitHub CLI** autenticado (`gh auth login`): M00B.
- **Tiled** (editor de mapas): M02C. O M04A em diante pede mudanças nos mapas.

Vale ler os módulos M00A a M03B mesmo sem fazer os passos: o M03C supõe que você conhece o game loop, as cenas, os mapas do Tiled e as camadas Model, View e Controller.

## Como usar

O curso usa três repositórios: o [`kernel-quest-curso`](https://github.com/sebagonella/kernel-quest-curso) (o material, que você só lê), este modelo (só o ponto de partida) e o **seu**, criado a partir dele, onde você escreve. A seção "Seus repositórios e pastas" do README do curso mostra o mapa completo.

1. Clique em **"Use this template" > "Create a new repository"**. Chame o repositório de **`rpg-engine`** (os módulos usam esse nome) e deixe-o **privado**. Depois, clone o seu na sua pasta pessoal, trocando `SEU-USUARIO` pelo seu usuário do GitHub:
   ```bash
   cd ~                                 # Windows (PowerShell): cd $HOME
   gh repo clone SEU-USUARIO/rpg-engine
   cd rpg-engine
   ```
2. Crie a venv com Python 3.12 e instale as dependências:
   ```bash
   python3.12 -m venv .venv            # Windows: py -3.12 -m venv .venv
   source .venv/bin/activate           # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
   No Windows, se o PowerShell recusar o `activate` ("a execução de scripts foi desabilitada"), rode uma vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` e repita.
3. Copie o `.env.example` para `.env` e preencha a sua chave do Gemini e o seu nome (o M00B do curso explica como criar a chave).
4. Rode `python teste_conexao_gemini.py` e depois `python main.py`.
5. Traga os arquivos do curso. Cada módulo usa uma pasta `arquivos/MNN/` do repositório do curso, copiada para uma pasta `curso-arquivos/` na sua pasta pessoal, **fora** do projeto. Clone o curso uma vez e copie a pasta do M03C:
   ```powershell
   # PowerShell (Windows)
   git clone https://github.com/sebagonella/kernel-quest-curso.git $HOME\kernel-quest-curso
   New-Item -ItemType Directory -Force $HOME\curso-arquivos
   Copy-Item -Recurse -Force $HOME\kernel-quest-curso\arquivos\M03C $HOME\curso-arquivos\
   ```
   ```bash
   # bash (Linux)
   git clone https://github.com/sebagonella/kernel-quest-curso.git ~/kernel-quest-curso
   mkdir -p ~/curso-arquivos
   cp -r ~/kernel-quest-curso/arquivos/M03C ~/curso-arquivos/
   ```
   Nos módulos seguintes, o Ponto de partida de cada um traz o `git pull` do curso e a cópia da pasta nova.
6. Tem um mentor (o "Engenheiro Sênior" do curso)? Convide-o como colaborador: no seu repositório, Settings > Collaborators > Add people, com o usuário dele no GitHub. No M03C ele revisa o seu primeiro Pull Request. Sem mentor, o M03C mostra o caminho da autorrevisão.
7. Personalize antes de seguir: o nome do jogo (`NOME_JOGO` em `src/config.py`), as falas e personas (`src/models.py`) e os créditos da tela do jogo (a lista `CREDITOS` em `src/views.py`). O jogo é seu a partir daqui.
8. Siga para o M03C no repositório do curso.

Este README é seu: reescreva quando o jogo for ganhando a sua cara (o desafio do M03C pede uma seção de controles aqui).

## Licença

Código sob a licença MIT (`LICENSE`). Arte do pacote Ninja Adventure (CC0) e fonte Jersey 10 (OFL), com as licenças em `assets/`.

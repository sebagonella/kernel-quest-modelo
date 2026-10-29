# Kernel Quest — modelo de entrada no M03C

Ponto de partida para quem entra no curso [Kernel Quest](https://github.com/sebagonella/kernel-quest-curso) no **módulo M03C**, com o jogo já organizado em camadas (estado ao fim do M03B).

> **Começando do zero?** Não use este modelo: comece pelo M00A. Criar o projeto e o repositório com as próprias mãos é parte do que o M00A e o M00B ensinam, e este modelo já traz as respostas do M00A ao M03B.

## Como usar

1. Clique em **"Use this template" > "Create a new repository"**, dê um nome ao repositório (pode ser privado) e clone o seu.
2. Crie a venv com Python 3.12 e instale as dependências:
   ```bash
   python3.12 -m venv .venv            # Windows: py -3.12 -m venv .venv
   source .venv/bin/activate           # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Copie o `.env.example` para `.env` e preencha a sua chave do Gemini e o seu nome (o M00B do curso explica como criar a chave).
4. Rode `python teste_conexao_gemini.py` e depois `python main.py`.
5. Personalize antes de seguir: o nome do jogo (`NOME_JOGO` em `src/config.py`), as falas e personas (`src/models.py`) e os créditos (`assets/CREDITOS.md`). O jogo é seu a partir daqui.
6. Siga para o M03C no repositório do curso.

Este README é seu: reescreva quando o jogo for ganhando a sua cara (o desafio do M03C pede uma seção de controles aqui).

## Licença

Código sob a licença MIT (`LICENSE`). Arte do pacote Ninja Adventure (CC0) e fonte Jersey 10 (OFL), com as licenças em `assets/`.

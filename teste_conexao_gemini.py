"""
RPG Engine — teste de conexão com o Gemini.

Valida a chave, o modelo e a cota ANTES de colocarmos IA no jogo.
Uso:  python teste_conexao_gemini.py
"""
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai

from src.ia import explicar_erro  # a mesma tradução de erros que o jogo usa

PASTA_PROJETO = Path(__file__).resolve().parent
load_dotenv(PASTA_PROJETO / ".env")

CHAVE = os.getenv("GEMINI_API_KEY")
MODELO = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
TIMEOUT_MS = 30_000  # sem isso, uma rede travada deixaria o programa esperando para sempre


def main():
    if not CHAVE or CHAVE == "cole_sua_chave_aqui":
        print("[ERRO] GEMINI_API_KEY não configurada.")
        print("Copie .env.example para .env e cole sua chave do Google AI Studio.")
        sys.exit(1)

    cliente = genai.Client(api_key=CHAVE, http_options={"timeout": TIMEOUT_MS})
    print(f"[REDE] Testando o modelo {MODELO}...")
    inicio = time.perf_counter()
    try:
        interacao = cliente.interactions.create(
            model=MODELO,
            system_instruction=(
                "Você é o narrador de um RPG medieval. "
                "Responda em português, em uma única frase curta."
            ),
            input="Dê boas-vindas a um engenheiro júnior que acabou de montar sua bancada.",
            store=False,  # não guarda a interação para continuar a conversa depois
        )
    except Exception as erro:
        mensagem = explicar_erro(erro)
        if mensagem is None:
            raise  # erro de programação: mostra o traceback completo para corrigir
        print(f"[ERRO] {mensagem}")
        sys.exit(1)

    duracao = time.perf_counter() - inicio
    print(f"[OK] Resposta em {duracao:.1f} s:")
    print(interacao.output_text)


if __name__ == "__main__":
    main()

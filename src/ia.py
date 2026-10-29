"""
RPG Engine — a IA do jogo (Gemini).

Tudo o que fala com o Gemini mora aqui, atrás da classe ServicoIA: o main.py
cria um serviço e só chama responder(). Com IA_FALSA=1 no ambiente,
responder() devolve uma fala fixa, sem rede e sem gastar cota (útil para
testar e para a verificação automática).
"""
import os

from google import genai

# Erros de rede da Interactions API (o SDK não exporta essas classes publicamente).
ERROS_DE_CONEXAO = ("APIConnectionError", "APITimeoutError")

# Fala de teste da paginação (IA_FALSA=longa): exatamente 5 linhas na caixa de diálogo.
FALA_LONGA = (
    "(fala de teste) Esta fala existe para testar a caixa de diálogo. "
    "Ela tem cinco linhas: as três primeiras enchem a página 1, que mostra o contador 1/2 "
    "e a seta piscando. As duas últimas vão para a página 2, que termina com o quadrado "
    "de fim de fala."
)


def explicar_erro(erro):
    """Traduz o erro da API numa orientação prática. Devolve None se não for erro da API."""
    codigo = getattr(erro, "status_code", None) or getattr(erro, "code", None)
    if codigo == 429:
        return "Cota esgotada (429). Espere um minuto e tente de novo."
    if codigo in (400, 401, 403):
        return (f"Requisição recusada ({codigo}). Quase sempre é a chave: "
                "confira GEMINI_API_KEY no arquivo .env.")
    if codigo == 404:
        return "Modelo não encontrado (404). Confira GEMINI_MODEL no arquivo .env."
    if codigo:
        return f"A API respondeu com erro {codigo}: {erro}"
    if type(erro).__name__ in ERROS_DE_CONEXAO:
        return f"Sem conexão com a API (rede, proxy ou firewall): {erro}"
    return None  # não é erro da API: provavelmente um erro no nosso código


class ServicoIA:
    """O serviço de IA do jogo. A interface é uma só: responder(instrucao, fala) -> texto.

    Quem usa não sabe se a resposta veio do Gemini ou da IA falsa, nem como o
    cliente é criado. Por isso, no M04A, os testes trocam este serviço por um falso.
    """

    def __init__(self, modelo, timeout_ms):
        self.modelo = modelo
        self.timeout_ms = timeout_ms
        self.cliente = None  # criado só na primeira chamada de verdade

    def obter_cliente(self):
        """Cria o cliente do Gemini uma única vez e reaproveita nas próximas chamadas."""
        if self.cliente is None:
            # genai.Client() lê a chave da variável GEMINI_API_KEY (carregada do .env).
            self.cliente = genai.Client(http_options={"timeout": self.timeout_ms})
        return self.cliente

    def responder(self, instrucao, fala):
        """Pede ao Gemini a resposta do personagem descrito em `instrucao` para a `fala`."""
        if os.getenv("IA_FALSA") == "longa":
            return FALA_LONGA
        if os.getenv("IA_FALSA") == "1":
            return "(IA falsa) Arquitetura antes de feitiço, aprendiz. Volte com um plano."
        if not os.getenv("GEMINI_API_KEY"):
            return "[ERRO] GEMINI_API_KEY não configurada no arquivo .env."
        try:
            interacao = self.obter_cliente().interactions.create(
                model=self.modelo,
                system_instruction=instrucao,
                input=fala,
                store=False,  # cada fala é independente: não guardamos a conversa
            )
        except Exception as erro:
            mensagem = explicar_erro(erro)
            if mensagem is None:
                raise  # erro de programação: mostra o traceback completo para corrigir
            return f"[ERRO] {mensagem}"
        return interacao.output_text

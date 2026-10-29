"""
Verificação automática do jogo, sem janela (para o Claude Code e para o CI).

Roda o main.py em modo headless, executa N quadros, salva um print da tela
e encerra. Se o jogo quebrar antes, devolve erro (código de saída 1).

Uso:
    python ferramentas/verificar.py
    python ferramentas/verificar.py --quadros 300 --saida ../../curso/aluno/img/M01.png
    python ferramentas/verificar.py --teclas "10-80:right,90:space"
    python ferramentas/verificar.py --texto "100:Olá, Mago!" --teclas "101:return"
    python ferramentas/verificar.py --tempo-max 30     # falha se o jogo travar por mais de 30 s

Teclas:
    "30:space"     pressiona e solta no quadro 30
    "10-80:right"  segura do quadro 10 ao 80 (pygame.key.get_pressed enxerga;
                   get_just_pressed/get_just_released enxergam o início e o fim)
    Nomes válidos: os de pygame.key.key_code, por exemplo
    a..z, 0..9, space, return, escape, tab, backspace, up, down, left, right, f1..f12.
    ("enter" é a tecla do teclado numérico; para ENTER comum use "return".)

IA: por padrão define IA_FALSA=1, para o jogo usar respostas simuladas e não
gastar a cota do Gemini. Use --ia-real para chamar a API de verdade.

Funciona com qualquer módulo, inclusive com o loop assíncrono (asyncio),
porque intercepta pygame.display.flip() e pygame.display.update() em vez de
mudar o código do jogo. Um limite de tempo de relógio (--tempo-max, padrão
60 s) impede que um jogo travado prenda o CI.
O aluno recebe este arquivo pronto no M04 (CI); não precisa entendê-lo.
"""
import argparse
import os
import threading
import time
import runpy
import sys
import traceback
from pathlib import Path

PASTA_PROJETO = Path(__file__).resolve().parent.parent


class FimDaVerificacao(SystemExit):
    """Sinal usado para encerrar o jogo depois do último quadro."""


class FormatoInvalido(ValueError):
    """--teclas ou --texto escrito fora do formato."""


def interpretar_teclas(textos):
    """Converte ["10-80:right,90:space"] em [(10, 81, "right"), (90, 91, "space")]."""
    acoes = []
    for texto in textos:
        for item in filter(None, (parte.strip() for parte in texto.split(","))):
            try:
                quadros, nome = item.split(":", 1)
                inicio, _, fim = quadros.partition("-")
                inicio = int(inicio)
                fim = int(fim) + 1 if fim else inicio + 1
            except ValueError:
                raise FormatoInvalido(f'--teclas "{item}": use QUADRO:tecla ou INICIO-FIM:tecla, '
                                      'ex.: "30:space" ou "10-80:right"') from None
            acoes.append((inicio, fim, nome.strip().lower()))
    return acoes


def interpretar_textos(textos):
    """Converte ["100:Olá"] em {100: ["Olá"]}."""
    agenda = {}
    for texto in textos:
        try:
            quadro, conteudo = texto.split(":", 1)
            agenda.setdefault(int(quadro), []).append(conteudo)
        except ValueError:
            raise FormatoInvalido(f'--texto "{texto}": use QUADRO:texto, ex.: "100:Olá, Mago!"') from None
    return agenda


def main():
    parser = argparse.ArgumentParser(description="Roda o jogo sem janela e salva um print.")
    parser.add_argument("--quadros", type=int, default=120)
    parser.add_argument("--saida", default=str(PASTA_PROJETO / "ferramentas" / "saida" / "tela.png"))
    parser.add_argument("--teclas", action="append", default=[], help='ex.: "10-80:right,90:space"')
    parser.add_argument("--texto", action="append", default=[], help='ex.: "100:Olá, Mago!" (TEXTINPUT)')
    parser.add_argument("--script", default="main.py")
    parser.add_argument("--ia-real", action="store_true", help="chama o Gemini de verdade (gasta cota)")
    parser.add_argument("--tempo-max", type=float, default=60, help="segundos de relógio até desistir (padrão 60)")
    args = parser.parse_args()

    # Caminhos relativos valem a partir de onde o comando foi digitado.
    saida = Path(args.saida).resolve()
    script = Path(args.script)
    script = script if script.is_absolute() else (PASTA_PROJETO / script)

    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    if args.ia_real:
        os.environ.pop("IA_FALSA", None)  # vale mesmo se o shell exportou IA_FALSA=1
    else:
        os.environ.setdefault("IA_FALSA", "1")
    os.chdir(PASTA_PROJETO)
    sys.path.insert(0, str(PASTA_PROJETO))

    import pygame

    pygame.init()  # inofensivo: o jogo chama de novo; necessário para validar nomes de tecla
    try:
        acoes = interpretar_teclas(args.teclas)
        textos = interpretar_textos(args.texto)
    except FormatoInvalido as erro:
        print(f"[ERRO] {erro}")
        return 2
    try:
        acoes = [(inicio, fim, pygame.key.key_code(nome)) for inicio, fim, nome in acoes]
    except ValueError as erro:
        print(f"[ERRO] Nome de tecla inválido: {erro}. Veja os nomes válidos no início deste arquivo.")
        return 2

    saida.parent.mkdir(parents=True, exist_ok=True)
    flip_original = pygame.display.flip
    update_original = pygame.display.update
    get_pressed_original = pygame.key.get_pressed
    estado = {"quadro": 0, "seguradas": set(), "descidas": set(), "subidas": set()}

    class TeclasSimuladas:
        """Resultado de get_pressed() com as teclas seguradas pela verificação."""

        def __init__(self, real):
            self.real = real

        def __getitem__(self, tecla):
            return tecla in estado["seguradas"] or self.real[tecla]

    class TeclasDoQuadro(TeclasSimuladas):
        """Resultado de get_just_pressed()/get_just_released() com as teclas simuladas."""

        def __init__(self, real, chave):
            super().__init__(real)
            self.chave = chave

        def __getitem__(self, tecla):
            return tecla in estado[self.chave] or self.real[tecla]

    def get_pressed_simulado():
        return TeclasSimuladas(get_pressed_original())

    def postar_tecla(tipo, tecla):
        pygame.event.post(pygame.event.Event(tipo, key=tecla, mod=0, unicode="", scancode=0))

    def fim_de_quadro(original, *a, **kw):
        resultado = original(*a, **kw)
        estado["quadro"] += 1
        quadro = estado["quadro"]
        # Eventos e teclas seguradas valem para o próximo quadro do jogo.
        for inicio, fim, tecla in acoes:
            if quadro == inicio:
                postar_tecla(pygame.KEYDOWN, tecla)
            if quadro == fim:
                postar_tecla(pygame.KEYUP, tecla)
        estado["seguradas"] = {tecla for inicio, fim, tecla in acoes if inicio <= quadro < fim}
        estado["descidas"] = {tecla for inicio, _, tecla in acoes if inicio == quadro}
        estado["subidas"] = {tecla for _, fim, tecla in acoes if fim == quadro}
        for conteudo in textos.get(quadro, []):
            pygame.event.post(pygame.event.Event(pygame.TEXTINPUT, text=conteudo))
        if quadro >= args.quadros:
            pygame.image.save(pygame.display.get_surface(), saida)
            raise FimDaVerificacao(0)
        return resultado

    pygame.display.flip = lambda *a, **kw: fim_de_quadro(flip_original, *a, **kw)
    pygame.display.update = lambda *a, **kw: fim_de_quadro(update_original, *a, **kw)
    pygame.key.get_pressed = get_pressed_simulado
    for nome, chave in (("get_just_pressed", "descidas"), ("get_just_released", "subidas")):
        original = getattr(pygame.key, nome, None)  # só no pygame-ce 2.4+
        if original:
            setattr(pygame.key, nome, lambda original=original, chave=chave: TeclasDoQuadro(original(), chave))

    def vigiar_tempo():
        # Um jogo travado (loop sem flip, input() esperando) não pode prender o CI para sempre.
        time.sleep(args.tempo_max)
        print(f"[FALHOU] tempo esgotado: {args.tempo_max:.0f} s de relógio sem chegar ao "
              f"quadro {args.quadros} (parou no quadro {estado['quadro']}).", flush=True)
        os._exit(1)

    threading.Thread(target=vigiar_tempo, daemon=True).start()
    try:
        runpy.run_path(str(script), run_name="__main__")
    except FimDaVerificacao:
        print(f"[OK] {args.quadros} quadros sem erro. Print salvo em {saida}")
        return 0
    except SystemExit as saida_jogo:
        print(f"[FALHOU] O jogo encerrou no quadro {estado['quadro']} (código {saida_jogo.code}).")
        return 1
    except Exception:
        traceback.print_exc()
        print(f"[FALHOU] Exceção no quadro {estado['quadro']}.")
        return 1

    print(f"[FALHOU] O jogo terminou sozinho no quadro {estado['quadro']}.")
    return 1


if __name__ == "__main__":
    sys.exit(main())

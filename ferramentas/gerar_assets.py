"""
Gerador de assets em pixel art (sprites e cenários .png).

Uso (na pasta do projeto):
    python ferramentas/gerar_assets.py            # cria só o que ainda não existe
    python ferramentas/gerar_assets.py --forcar   # recria tudo (apaga arte trocada!)

Cria a pasta assets/ com imagens reais em .png. Elas são um ponto de
partida: qualquer arquivo pode ser trocado por arte livre (Kenney,
OpenGameArt) ou desenhada por você, desde que mantenha o mesmo nome.
Arquivos que já existem NÃO são sobrescritos, para não apagar a arte
que você escolheu.

Este script é FORNECIDO ao aluno pronto (sempre como arquivo inteiro):
ele roda, não precisa entendê-lo linha a linha agora.
"""
import argparse
from pathlib import Path

import pygame

PASTA_PROJETO = Path(__file__).resolve().parent.parent
PASTA_ASSETS = PASTA_PROJETO / "assets"
FORCAR = False
criados, mantidos = [], []


def salvar(superficie, nome_arquivo):
    destino = PASTA_ASSETS / nome_arquivo
    if destino.exists() and not FORCAR:
        mantidos.append(nome_arquivo)
        return
    pygame.image.save(superficie, destino)
    criados.append(nome_arquivo)


def criar_sprite_heroi():
    sup = pygame.Surface((48, 48), pygame.SRCALPHA)
    pygame.draw.rect(sup, (30, 80, 180), (14, 22, 20, 18), border_radius=3)   # túnica
    pygame.draw.rect(sup, (100, 60, 20), (14, 32, 20, 4))                      # cinto
    pygame.draw.rect(sup, (220, 180, 40), (22, 32, 4, 4))                      # fivela
    pygame.draw.rect(sup, (70, 45, 15), (15, 40, 7, 6))                        # botas
    pygame.draw.rect(sup, (70, 45, 15), (26, 40, 7, 6))
    pygame.draw.line(sup, (180, 190, 205), (10, 12), (36, 38), 3)              # espada
    pygame.draw.rect(sup, (245, 205, 165), (16, 10, 16, 13), border_radius=3)  # rosto
    pygame.draw.rect(sup, (30, 30, 40), (19, 15, 3, 3))                        # olhos
    pygame.draw.rect(sup, (30, 30, 40), (26, 15, 3, 3))
    pygame.draw.rect(sup, (150, 160, 175), (14, 4, 20, 9), border_radius=3)    # elmo
    pygame.draw.rect(sup, (100, 110, 125), (13, 11, 22, 3))
    salvar(sup, "player.png")


def criar_sprite_mago():
    sup = pygame.Surface((48, 48), pygame.SRCALPHA)
    pygame.draw.polygon(sup, (110, 35, 160), [(24, 18), (10, 45), (38, 45)])   # manto
    pygame.draw.line(sup, (240, 190, 40), (24, 20), (24, 45), 3)
    pygame.draw.rect(sup, (240, 200, 160), (17, 12, 14, 10))                   # rosto
    pygame.draw.polygon(sup, (225, 225, 235), [(15, 20), (33, 20), (24, 40)])  # barba
    pygame.draw.polygon(sup, (90, 25, 135), [(24, 1), (12, 14), (36, 14)])     # chapéu
    pygame.draw.ellipse(sup, (110, 35, 160), (8, 11, 32, 6))
    pygame.draw.line(sup, (120, 75, 30), (38, 12), (38, 46), 3)                # cajado
    pygame.draw.circle(sup, (255, 80, 220), (38, 10), 5)
    salvar(sup, "npc_mago.png")


def criar_sprite_mercador():
    sup = pygame.Surface((48, 48), pygame.SRCALPHA)
    pygame.draw.rect(sup, (130, 80, 35), (8, 16, 12, 22), border_radius=3)     # mochila
    pygame.draw.rect(sup, (45, 135, 65), (15, 22, 18, 18), border_radius=3)    # traje
    pygame.draw.rect(sup, (80, 50, 20), (15, 33, 18, 4))
    pygame.draw.rect(sup, (60, 40, 15), (16, 40, 6, 6))
    pygame.draw.rect(sup, (60, 40, 15), (26, 40, 6, 6))
    pygame.draw.rect(sup, (240, 195, 155), (17, 11, 14, 12), border_radius=2)  # rosto
    pygame.draw.rect(sup, (30, 30, 35), (20, 15, 3, 3))
    pygame.draw.rect(sup, (30, 30, 35), (26, 15, 3, 3))
    pygame.draw.polygon(sup, (35, 110, 50), [(14, 12), (24, 3), (34, 12)])     # capuz
    salvar(sup, "npc_mercador.png")


def criar_sprite_pinguim():
    sup = pygame.Surface((48, 48), pygame.SRCALPHA)
    pygame.draw.ellipse(sup, (25, 28, 35), (10, 6, 28, 38))                    # corpo
    pygame.draw.ellipse(sup, (245, 245, 250), (15, 15, 18, 25))                # barriga
    pygame.draw.circle(sup, (255, 255, 255), (19, 13), 3)                      # olhos
    pygame.draw.circle(sup, (255, 255, 255), (29, 13), 3)
    pygame.draw.circle(sup, (15, 15, 20), (19, 13), 1)
    pygame.draw.circle(sup, (15, 15, 20), (29, 13), 1)
    pygame.draw.polygon(sup, (255, 165, 20), [(19, 16), (29, 16), (24, 21)])   # bico
    pygame.draw.rect(sup, (180, 90, 40), (13, 21, 22, 5), border_radius=2)     # cachecol
    pygame.draw.rect(sup, (180, 90, 40), (26, 24, 5, 8), border_radius=1)
    pygame.draw.ellipse(sup, (255, 150, 15), (12, 40, 10, 6))                  # pés
    pygame.draw.ellipse(sup, (255, 150, 15), (26, 40, 10, 6))
    salvar(sup, "npc_tux.png")


def criar_sprite_guarda():
    sup = pygame.Surface((48, 48), pygame.SRCALPHA)
    pygame.draw.line(sup, (120, 80, 40), (40, 4), (40, 46), 3)                 # lança (cabo)
    pygame.draw.polygon(sup, (190, 195, 205), [(40, 0), (36, 8), (44, 8)])     # lança (ponta)
    pygame.draw.rect(sup, (140, 30, 35), (14, 22, 20, 18), border_radius=3)    # túnica
    pygame.draw.rect(sup, (160, 165, 175), (12, 22, 24, 6), border_radius=2)   # ombreiras
    pygame.draw.rect(sup, (60, 40, 20), (15, 40, 7, 6))                        # botas
    pygame.draw.rect(sup, (60, 40, 20), (26, 40, 7, 6))
    pygame.draw.rect(sup, (235, 195, 155), (16, 10, 16, 13), border_radius=3)  # rosto
    pygame.draw.rect(sup, (30, 30, 40), (19, 15, 3, 3))                        # olhos
    pygame.draw.rect(sup, (30, 30, 40), (26, 15, 3, 3))
    pygame.draw.rect(sup, (90, 60, 30), (19, 19, 10, 2))                       # bigode
    pygame.draw.rect(sup, (120, 125, 135), (14, 3, 20, 9), border_radius=4)    # capacete
    pygame.draw.rect(sup, (230, 190, 40), (22, 0, 4, 5))                       # penacho
    salvar(sup, "npc_guarda.png")


def criar_fundo_castelo():
    sup = pygame.Surface((800, 600))
    sup.fill((40, 40, 55))
    for x in range(0, 800, 50):                                                # ladrilhos
        for y in range(0, 600, 50):
            cor = (46, 46, 62) if (x // 50 + y // 50) % 2 == 0 else (36, 36, 50)
            pygame.draw.rect(sup, cor, (x, y, 50, 50))
            pygame.draw.rect(sup, (25, 25, 35), (x, y, 50, 50), 1)
    pygame.draw.rect(sup, (130, 25, 40), (150, 250, 650, 100))                # tapete
    pygame.draw.rect(sup, (210, 175, 50), (150, 255, 650, 90), 3)
    salvar(sup, "bg_castelo.png")


def criar_fundo_floresta():
    sup = pygame.Surface((800, 600))
    sup.fill((35, 85, 45))
    for x in range(0, 800, 50):                                                # grama
        for y in range(0, 600, 50):
            cor = (40, 95, 50) if (x // 50 + y // 50) % 2 == 0 else (32, 78, 40)
            pygame.draw.rect(sup, cor, (x, y, 50, 50))
    pygame.draw.rect(sup, (125, 90, 55), (0, 260, 800, 80))                    # estrada
    pygame.draw.rect(sup, (105, 75, 45), (0, 260, 800, 80), 4)
    salvar(sup, "bg_floresta.png")


def main():
    global FORCAR
    parser = argparse.ArgumentParser(description="Gera os assets do jogo em assets/.")
    parser.add_argument("--forcar", action="store_true", help="recria arquivos que já existem")
    FORCAR = parser.parse_args().forcar

    # Desenhar e salvar imagens não exige abrir janela nem iniciar o áudio.
    PASTA_ASSETS.mkdir(exist_ok=True)
    criar_sprite_heroi()
    criar_sprite_mago()
    criar_sprite_mercador()
    criar_sprite_pinguim()
    criar_sprite_guarda()
    criar_fundo_castelo()
    criar_fundo_floresta()
    print(f"[SUCESSO] Pasta {PASTA_ASSETS}")
    print(f"  criados: {', '.join(criados) or 'nenhum'}")
    print(f"  mantidos (já existiam): {', '.join(mantidos) or 'nenhum'}")


if __name__ == "__main__":
    main()

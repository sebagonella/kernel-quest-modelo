"""
RPG Engine — Módulo 03B: Camadas.

O jogo é o mesmo do M03A (menu, mapas do Tiled, moedas, HUD, diálogo com o
Gemini), agora separado em camadas dentro de src/:
  models.py       dados e regras, sem pygame (testável sem janela)
  views.py        desenho e som; só lê o Model
  controllers.py  teclado e coordenação; monta o Model a partir dos mapas
Este arquivo só monta as peças e roda o game loop.
"""
import pygame

from src.config import ALTURA, FPS, LARGURA, MODELO_IA, NOME_JOGO, TETO_DT, TIMEOUT_IA_MS
from src.controllers import Controle, carregar_cenas
from src.ia import ServicoIA
from src.models import Jogo
from src.views import Tela


def main():
    pygame.init()  # também liga o áudio (pygame.mixer), se houver dispositivo de som
    superficie = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption(NOME_JOGO)
    relogio = pygame.time.Clock()

    # Injeção de dependências: cada peça é criada aqui e entregue pronta a quem usa.
    jogo = Jogo(carregar_cenas())  # Model
    tela = Tela(superficie)  # View
    controle = Controle(jogo, tela, ServicoIA(MODELO_IA, TIMEOUT_IA_MS))  # Controller

    tempo = 0.0
    # Game loop: a cada volta, ler eventos, atualizar e desenhar (60 vezes por segundo).
    while controle.rodando:
        # tick() segura o ritmo em 60 FPS e devolve os milissegundos desde o último quadro.
        dt = relogio.tick(FPS) / 1000  # delta time: segundos desde o último quadro
        dt = min(dt, TETO_DT)  # depois de um congelamento (a IA pensando), nada de teletransporte
        tempo += dt
        for evento in pygame.event.get():
            controle.tratar_evento(evento)
        controle.atualizar(dt)
        tela.desenhar(jogo, controle, dt, tempo)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()

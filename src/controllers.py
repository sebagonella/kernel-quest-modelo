"""
RPG Engine — Controller: entrada e coordenação.

O Controller lê o teclado, pede ao Model que aplique as regras, chama a IA
e diz à View o que tocar. Ele também monta o Model a partir dos mapas do
Tiled. É a única camada que conhece as outras duas.
"""
import time

import pygame
import pytmx

from src.config import (
    ESCALA, IMAGEM_MOEDA, INTERVALO_MINIMO, LETRAS_POR_VOZ, NOME, PASTA_ASSETS, TAMANHO_MOEDA,
    TAMANHO_SPRITE, TAMANHO_TILE, VALOR_MOEDA, VELOCIDADE_ESCRITA,
)
from src.models import (
    INSTRUCAO_BROK, INSTRUCAO_CACADOR, INSTRUCAO_MAGO, INSTRUCAO_SENTINELA, NPC, Cena, Estado,
    Moeda, Retangulo, retangulo_no_centro,
)
from src.views import OPCOES_MENU, OPCOES_PAUSA


def ampliar(obj):
    """Retângulo de um objeto do Tiled (em pixels de 16×16) convertido para a tela (3×)."""
    return Retangulo(obj.x * ESCALA, obj.y * ESCALA, obj.width * ESCALA, obj.height * ESCALA)


def objetos(dados, camada):
    """Os objetos de uma camada do mapa; lista vazia se o mapa não tiver essa camada."""
    try:
        return list(dados.get_layer_by_name(camada))
    except ValueError:
        return []


def ler_cena(nome, mapa, npcs):
    """Os dados de assets/mapas/<mapa>.tmx que viram Model (as imagens ficam com a View)."""
    dados = pytmx.TiledMap(str(PASTA_ASSETS / "mapas" / f"{mapa}.tmx"))  # sem carregar imagens
    lado = TAMANHO_TILE * ESCALA
    area = Retangulo(0, 0, dados.width * lado, dados.height * lado)  # o mapa inteiro
    # Moedas: um ponto do Tiled por moeda. As propriedades "imagem" e "valor" do
    # objeto, se existirem, trocam os padrões: um tipo novo de moeda é só dado no mapa.
    lado_moeda = TAMANHO_MOEDA * ESCALA
    moedas = [Moeda(retangulo_no_centro((obj.x * ESCALA, obj.y * ESCALA), lado_moeda, lado_moeda),
                    obj.properties.get("valor", VALOR_MOEDA),
                    obj.properties.get("imagem", IMAGEM_MOEDA))
              for obj in objetos(dados, "moedas")]
    return Cena(
        nome, mapa, area, npcs, moedas,
        colisoes=[ampliar(obj) for obj in objetos(dados, "colisao")],
        portais=[(ampliar(obj), obj.properties["destino"]) for obj in objetos(dados, "portais")],
        # Ponto de chegada com o nome do mapa de onde o herói vem (ou "inicio").
        chegadas={obj.name: (obj.x * ESCALA, obj.y * ESCALA) for obj in objetos(dados, "chegadas")},
    )


def criar_npc(nome, sprite_id, centro, instrucao):
    """Um NPC com a caixa de 48×48 centrada em `centro` (pixels do mapa já ampliado)."""
    caixa = retangulo_no_centro(centro, TAMANHO_SPRITE, TAMANHO_SPRITE)
    return NPC(nome, sprite_id, caixa, instrucao)


def carregar_cenas():
    """O mundo: cada cena é um mapa; os NPCs ficam em pixels do mapa já ampliado."""
    return {
        "salao": ler_cena("Salão do Castelo", "salao", [
            criar_npc("Arquimago Solaris", "mago", (408, 132), INSTRUCAO_MAGO),
            criar_npc("Sentinela do Salão", "sentinela", (668, 182), INSTRUCAO_SENTINELA),
        ]),
        "floresta": ler_cena("Floresta", "floresta", [
            criar_npc("Mercador Brok", "brok", (696, 456), INSTRUCAO_BROK),
            criar_npc("Caçador Rurik", "cacador", (1080, 744), INSTRUCAO_CACADOR),
        ]),
        "masmorra": ler_cena("Entrada da Masmorra", "masmorra", []),
    }


class Controle:
    """O Controller: recebe o Model (jogo), a View (tela) e a IA prontos, e os coordena."""

    def __init__(self, jogo, tela, servico_ia):
        # Injeção de dependências: o Controller não cria nenhuma das três peças.
        self.jogo = jogo
        self.tela = tela
        self.servico_ia = servico_ia
        self.rodando = True
        self.escolha = 0  # a opção marcada no menu (índice da lista de opções)
        self.dialogo = None  # a fala na caixa, quando o estado é DIALOGO
        self.pedindo = None  # o NPC cuja fala vamos pedir à IA assim que "Pensando..." aparecer
        self.ultima_chamada = -INTERVALO_MINIMO  # permite a primeira chamada logo de cara
        tela.tocar_musica("titulo")

    def tratar_evento(self, evento):
        """Uma tecla, um efeito: a mesma tecla faz coisas diferentes em cada estado."""
        jogo = self.jogo
        if evento.type == pygame.QUIT:
            self.rodando = False
        if evento.type != pygame.KEYDOWN:
            return  # daqui para baixo, só teclas apertadas
        tecla = evento.key
        if jogo.estado in (Estado.MENU, Estado.PAUSA):
            opcoes = OPCOES_MENU if jogo.estado == Estado.MENU else OPCOES_PAUSA
            if tecla in (pygame.K_UP, pygame.K_w):
                self.escolha = (self.escolha - 1) % len(opcoes)  # de cima, dá a volta para baixo
            elif tecla in (pygame.K_DOWN, pygame.K_s):
                self.escolha = (self.escolha + 1) % len(opcoes)
            elif tecla == pygame.K_ESCAPE and jogo.estado == Estado.MENU:
                self.rodando = False  # ESC no menu principal fecha o jogo
            elif tecla == pygame.K_ESCAPE:
                self.tela.tocar("voltar")
                jogo.mudar_estado(Estado.EXPLORANDO)
            elif tecla == pygame.K_RETURN:
                self.tela.tocar("ok")
                opcao = opcoes[self.escolha]
                self.escolha = 0  # o próximo menu começa na primeira opção
                if opcao == "Sair":
                    self.rodando = False
                elif opcao == "Créditos":
                    jogo.mudar_estado(Estado.CREDITOS)
                elif opcao == "Novo jogo":
                    jogo.novo_jogo(carregar_cenas())  # mapas relidos: moedas de volta ao chão
                    self.tela.tocar_musica(jogo.cena.mapa)
                elif opcao == "Continuar":
                    jogo.mudar_estado(Estado.EXPLORANDO)
                elif opcao == "Menu principal":
                    jogo.mudar_estado(Estado.MENU)
                    self.tela.tocar_musica("titulo")
        elif jogo.estado == Estado.CREDITOS:
            if tecla in (pygame.K_ESCAPE, pygame.K_RETURN):
                self.tela.tocar("voltar")
                jogo.mudar_estado(Estado.MENU)
        elif jogo.estado == Estado.EXPLORANDO:
            perto = jogo.npc_perto()
            if tecla == pygame.K_ESCAPE:
                self.tela.tocar("ok")
                self.escolha = 0  # a pausa sempre abre em "Continuar"
                jogo.mudar_estado(Estado.PAUSA)
            elif tecla == pygame.K_SPACE and perto:
                if time.perf_counter() - self.ultima_chamada < INTERVALO_MINIMO:
                    return  # ESPAÇO apertado rápido demais: ignora
                # A caixa abre já com "Pensando..."; a chamada à IA vem em atualizar().
                self.dialogo = self.tela.novo_dialogo(perto, "Pensando...")
                self.pedindo = perto
                jogo.mudar_estado(Estado.DIALOGO)
        elif jogo.estado == Estado.DIALOGO and not self.pedindo:
            if tecla in (pygame.K_DOWN, pygame.K_RETURN, pygame.K_SPACE):
                if not self.dialogo.avancar():  # passou da última página: a conversa acabou
                    jogo.mudar_estado(Estado.EXPLORANDO)
            elif tecla == pygame.K_UP:
                self.dialogo.voltar()
            elif tecla == pygame.K_ESCAPE:
                jogo.mudar_estado(Estado.EXPLORANDO)

    def atualizar(self, dt):
        """Um quadro do mundo: teclas seguradas, regras do Model, máquina de escrever e IA."""
        jogo = self.jogo
        if jogo.estado in (Estado.MENU, Estado.CREDITOS):
            return  # nas telas de menu, o mundo fica parado
        # get_pressed() diz quais teclas estão seguradas agora.
        teclas = pygame.key.get_pressed()
        dx, dy = 0, 0  # direção do movimento neste quadro: -1, 0 ou 1 em cada eixo
        direcao = jogo.heroi.direcao
        if jogo.estado == Estado.EXPLORANDO:  # no diálogo e na pausa, o herói nem anda nem vira
            if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
                dx, direcao = -1, "esquerda"
            if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
                dx, direcao = 1, "direita"
            if teclas[pygame.K_UP] or teclas[pygame.K_w]:
                dy, direcao = -1, "cima"
            if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
                dy, direcao = 1, "baixo"
        jogo.mover_heroi(dx, dy, direcao, dt)

        if jogo.estado == Estado.EXPLORANDO:
            if jogo.coletar_moedas():
                self.tela.tocar("moeda")
            # Tocar num portal só começa a transição: o mapa troca quando a tela fica preta.
            jogo.tocar_portal()
        if jogo.estado == Estado.TRANSICAO and jogo.atualizar_transicao(dt):
            self.tela.tocar_musica(jogo.cena.mapa)  # cada mapa tem a música de mesmo nome

        if jogo.estado == Estado.DIALOGO:
            dialogo = self.dialogo
            antes = int(dialogo.letras)
            dialogo.letras += VELOCIDADE_ESCRITA * dt  # máquina de escrever
            if (int(dialogo.letras) // LETRAS_POR_VOZ > antes // LETRAS_POR_VOZ
                    and not dialogo.pagina_completa()):
                self.tela.tocar("voz")  # a "voz" do NPC: um som a cada LETRAS_POR_VOZ letras novas
            if self.pedindo and dialogo.pagina_completa():
                print(f"[REDE] {self.pedindo.nome} está pensando... "
                      "(o jogo congela até a resposta)")
                inicio = time.perf_counter()
                # Chamada BLOQUEANTE: o loop para aqui até a resposta chegar.
                fala = self.servico_ia.responder(
                    self.pedindo.instrucao, f"O aprendiz {NOME} se aproxima e cumprimenta você.")
                self.ultima_chamada = time.perf_counter()
                print(f"[{self.pedindo.nome}] ({self.ultima_chamada - inicio:.1f} s) {fala}")
                self.dialogo = self.tela.novo_dialogo(self.pedindo, fala)
                self.pedindo = None

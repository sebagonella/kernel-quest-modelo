"""
RPG Engine — View: tudo o que aparece na tela e sai no alto-falante.

A View carrega imagens, fontes e sons, e desenha o Model (o jogo) e o estado
da interface (menu, caixa de diálogo). Ela só LÊ: nunca muda posição, moedas
ou estado. Trocar o visual inteiro do jogo seria trocar só este arquivo.
"""
import math
import platform
import sys

import pygame
import pytmx
from pytmx.util_pygame import load_pygame

from src.config import (
    ALTURA, COLUNA, COR_APAGADA, COR_CAIXA, COR_DESTAQUE, COR_FAIXA, COR_FUNDO, COR_PAINEL,
    COR_TEXTO, COR_VEU, ESCALA, ESCALA_CAIXA, ESCALA_HEROI_MENU, FONTE_PIXEL, IMAGEM_MOEDA,
    LARGURA, LARGURA_TEXTO, LINHAS_POR_PAGINA, MODELO_IA, NOME, NOME_JOGO, PASTA_ASSETS,
    PISCA_POR_SEGUNDO, QUADROS_ANDAR, QUADROS_MOEDA, RESPIRACAO_ALTURA, RESPIRACAO_VELOCIDADE,
    TAMANHO_FONTE, TAMANHO_FONTE_FALA, TAMANHO_FONTE_JOGO, TAMANHO_FONTE_TITULO, TAMANHO_MOEDA,
    TAMANHO_TILE, TEMPO_QUADRO, TEMPO_QUADRO_MOEDA, VOLUME_VOZ,
)
from src.models import Estado

OPCOES_MENU = ["Novo jogo", "Créditos", "Sair"]
OPCOES_PAUSA = ["Continuar", "Menu principal"]

CREDITOS = [
    "Arte, músicas e sons: pacote Ninja Adventure",
    "de Pixel-boy e AAA (licença CC0)",
    "Fonte: Jersey 10, de Sarah Cadigan-Fried (licença OFL)",
    "Falas dos personagens: Google Gemini",
]

# Cache de imagens: nome do arquivo -> imagem já carregada. Cada .png sai do disco uma vez só.
imagens_carregadas = {}


def carregar_imagem(nome_arquivo):
    """Carrega um .png da pasta assets/ (só na primeira vez) ou explica de onde ele vem."""
    if nome_arquivo in imagens_carregadas:
        return imagens_carregadas[nome_arquivo]  # já está na memória: nada de disco
    caminho = PASTA_ASSETS / nome_arquivo
    if not caminho.exists():
        print(f"[ERRO] Arquivo não encontrado: {caminho}")
        print("Copie para assets/ a pasta assets/ que veio com os arquivos do módulo.")
        sys.exit(1)
    imagem = pygame.image.load(caminho).convert_alpha()
    imagens_carregadas[nome_arquivo] = imagem
    return imagem


def carregar_som(nome_arquivo, volume=1.0):
    """Carrega um efeito de assets/sons/. Sem dispositivo de áudio, devolve None."""
    if not pygame.mixer.get_init():
        return None
    som = pygame.mixer.Sound(PASTA_ASSETS / "sons" / nome_arquivo)
    som.set_volume(volume)  # de 0.0 (mudo) a 1.0 (volume do arquivo)
    return som


def escrever(tela, fonte, texto, cor, centro_y, centro_x=LARGURA // 2):
    """Desenha um texto centralizado em (centro_x, centro_y); sem centro_x, no meio da tela."""
    imagem = fonte.render(texto, False, cor)  # False: sem suavização, pixel nítido
    tela.blit(imagem, imagem.get_rect(center=(centro_x, centro_y)))


def desenhar_menu(tela, fonte, opcoes, escolha, topo):
    """Uma opção por linha, a partir de topo; a escolhida fica dourada e entre setas."""
    for i, opcao in enumerate(opcoes):
        if i == escolha:
            escrever(tela, fonte, f"> {opcao} <", COR_DESTAQUE, topo + i * 50)
        else:
            escrever(tela, fonte, opcao, COR_TEXTO, topo + i * 50)


def quebrar_linhas(texto, fonte, largura_max):
    """Word wrap: junta palavras numa linha enquanto couberem em largura_max pixels."""
    linhas = []
    atual = ""
    for palavra in texto.split():
        tentativa = f"{atual} {palavra}".strip()
        if fonte.size(tentativa)[0] <= largura_max or not atual:
            atual = tentativa  # cabe (ou é a primeira palavra da linha): continua nesta linha
        else:
            linhas.append(atual)  # não cabe: fecha a linha e começa outra com a palavra
            atual = palavra
    linhas.append(atual)
    return linhas


def recortar_quadros(folha, colunas, linhas):
    """Fatia uma folha de sprites em quadros de TAMANHO_TILE, já ampliados ESCALA vezes.

    Devolve uma lista por coluna: quadros[coluna][linha].
    """
    quadros = []
    for coluna in range(colunas):
        lista = []
        for linha in range(linhas):
            # subsurface() é uma "janela" sobre um pedaço da folha, sem copiar pixels.
            recorte = folha.subsurface((coluna * TAMANHO_TILE, linha * TAMANHO_TILE,
                                        TAMANHO_TILE, TAMANHO_TILE))
            lista.append(pygame.transform.scale_by(recorte, ESCALA))
        quadros.append(lista)
    return quadros


class Dialogo:
    """Uma fala na caixa: quem fala, as páginas de até 3 linhas e quantas letras já apareceram."""

    def __init__(self, npc, texto, fonte):
        self.npc = npc
        self.fonte = fonte
        linhas = quebrar_linhas(texto, fonte, LARGURA_TEXTO)
        # Fatias de 3 em 3 linhas: [l0, l1, l2], [l3, l4, l5], ...
        self.paginas = [linhas[i:i + LINHAS_POR_PAGINA]
                        for i in range(0, len(linhas), LINHAS_POR_PAGINA)]
        self.pagina = 0
        self.letras = 0.0  # máquina de escrever: quantas letras da página já estão visíveis

    def letras_da_pagina(self):
        return sum(len(linha) for linha in self.paginas[self.pagina])

    def pagina_completa(self):
        return self.letras >= self.letras_da_pagina()

    def ultima_pagina(self):
        return self.pagina == len(self.paginas) - 1

    def avancar(self):
        """Completa a página, vai para a próxima ou, na última, encerra (devolve False)."""
        if not self.pagina_completa():
            self.letras = self.letras_da_pagina()  # pula a máquina de escrever
        elif not self.ultima_pagina():
            self.pagina += 1
            self.letras = 0.0
        else:
            return False
        return True

    def voltar(self):
        if self.pagina > 0:
            self.pagina -= 1
            self.letras = self.letras_da_pagina()  # página já lida aparece inteira

    def desenhar(self, tela, caixa, retrato, tempo):
        x, y = (LARGURA - caixa.get_width()) // 2, ALTURA - caixa.get_height() - 20
        tela.blit(caixa, (x, y))
        tela.blit(retrato, (x + 18, y + 37))
        tela.blit(self.fonte.render(self.npc.nome, False, COR_TEXTO), (x + 22, y + 2))
        # Cada linha mostra só as letras que já "chegaram"; o resto fica para os próximos quadros.
        resta = int(self.letras)
        for i, linha in enumerate(self.paginas[self.pagina]):
            visivel = self.fonte.render(linha[:resta], False, COR_CAIXA)
            tela.blit(visivel, (x + 135, y + 40 + i * 30))
            resta = max(resta - len(linha), 0)
        direita, base = x + caixa.get_width() - 32, y + caixa.get_height() - 32
        if len(self.paginas) > 1:  # contador "1/2" só quando a fala tem mais de uma página
            contador = self.fonte.render(f"{self.pagina + 1}/{len(self.paginas)}", False, COR_CAIXA)
            tela.blit(contador, (direita + 14 - contador.get_width(), y + 38))
        if not self.pagina_completa():
            return  # ainda escrevendo: nenhum indicador
        if not self.ultima_pagina():
            if int(tempo * PISCA_POR_SEGUNDO) % 2:  # ▼ pisca: tem continuação
                pygame.draw.polygon(tela, COR_CAIXA, [(direita, base), (direita + 14, base),
                                                      (direita + 7, base + 9)])
        else:
            pygame.draw.rect(tela, COR_CAIXA, (direita + 2, base, 10, 10))  # ■ a fala terminou


class Tela:
    """A View do jogo: carrega a arte e os sons uma vez e desenha o Model a cada quadro."""

    def __init__(self, superficie):
        self.superficie = superficie
        # Jersey 10: fonte pixel (licença OFL) que viaja junto com o jogo, em assets/fontes/.
        self.fonte_jogo = pygame.font.Font(FONTE_PIXEL, TAMANHO_FONTE_JOGO)
        self.fonte_titulo = pygame.font.Font(FONTE_PIXEL, TAMANHO_FONTE_TITULO)
        self.fonte = pygame.font.Font(FONTE_PIXEL, TAMANHO_FONTE)
        self.fonte_fala = pygame.font.Font(FONTE_PIXEL, TAMANHO_FONTE_FALA)
        # Arte do pacote Ninja Adventure: 16×16 pixels, ampliada para ficar visível.
        self.heroi_menu = pygame.transform.scale_by(carregar_imagem("personagens/heroi.png"),
                                                    ESCALA_HEROI_MENU)
        self.painel = pygame.Surface((360, 170), pygame.SRCALPHA)
        self.painel.fill(COR_PAINEL)  # preto translúcido
        self.faixa = pygame.Surface((LARGURA, 40), pygame.SRCALPHA)
        self.faixa.fill(COR_FAIXA)
        self.veu = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        self.veu.fill(COR_VEU)  # escurece o mundo atrás do menu de pausa
        # Preta; a transparência muda na transição entre mapas.
        self.escuridao = pygame.Surface((LARGURA, ALTURA))
        self.caixa = pygame.transform.scale_by(carregar_imagem("interface/caixa_dialogo.png"),
                                               ESCALA_CAIXA)
        # Sons pelo nome: o Controller pede tocar("moeda") e não precisa saber de arquivos.
        self.sons = {
            "ok": carregar_som("menu_ok.wav"),
            "voltar": carregar_som("menu_voltar.wav"),
            "voz": carregar_som("voz.wav", VOLUME_VOZ),
            "moeda": carregar_som("moeda.wav"),
        }
        # Herói: 4 direções × 4 quadros andando e 1 quadro por direção parado.
        self.quadros_andar = recortar_quadros(carregar_imagem("personagens/heroi/andar.png"),
                                              len(COLUNA), QUADROS_ANDAR)
        self.quadros_parado = recortar_quadros(carregar_imagem("personagens/heroi/parado.png"),
                                               len(COLUNA), 1)
        self.sombra = pygame.transform.scale_by(carregar_imagem("personagens/sombra.png"), ESCALA)
        self.quadro = 0  # animação da caminhada: é da tela, não do jogo
        self.tempo_quadro = 0.0
        # Caches da View: cada mapa, NPC e tipo de moeda é preparado uma vez só.
        self.mapas = {}  # mapa -> (fundo, árvores)
        self.npcs = {}  # sprite_id -> (quadros parados, retrato)
        self.moedas = {}  # imagem -> quadros girando
        # Ícone do HUD: o primeiro quadro da moeda.
        self.icone_moeda = self.quadros_moeda(IMAGEM_MOEDA)[0]

    def tocar(self, nome):
        """Toca um efeito, se houver áudio (o som é None quando não há)."""
        som = self.sons[nome]
        if som:
            som.play()

    def tocar_musica(self, nome):
        """Troca a música de fundo por assets/musicas/<nome>.ogg, em loop. Sem áudio, segue mudo."""
        if pygame.mixer.get_init():
            pygame.mixer.music.load(PASTA_ASSETS / "musicas" / f"{nome}.ogg")
            pygame.mixer.music.play(-1)  # -1 = repetir para sempre

    def novo_dialogo(self, npc, texto):
        """A caixa de diálogo é da interface: quebra o texto com a fonte da fala."""
        return Dialogo(npc, texto, self.fonte_fala)

    def mapa(self, nome):
        """Fundo e árvores de assets/mapas/<nome>.tmx, montados na primeira vez que aparecem."""
        if nome not in self.mapas:
            dados = load_pygame(str(PASTA_ASSETS / "mapas" / f"{nome}.tmx"))
            # Camadas de tiles: desenhadas uma única vez numa imagem do tamanho do mapa.
            chao = pygame.Surface((dados.width * TAMANHO_TILE, dados.height * TAMANHO_TILE))
            for camada in dados.visible_layers:
                if isinstance(camada, pytmx.TiledTileLayer):
                    for x, y, imagem in camada.tiles():
                        chao.blit(imagem, (x * TAMANHO_TILE, y * TAMANHO_TILE))
            fundo = pygame.transform.scale_by(chao, ESCALA)  # scale_by não borra o pixel
            # Árvores: objetos de tile, com imagem; a View só as desenha (a colisão é do Model).
            arvores = []
            if "arvores" in [camada.name for camada in dados.layers]:
                for obj in dados.get_layer_by_name("arvores"):
                    rect = pygame.Rect(obj.x * ESCALA, obj.y * ESCALA,
                                       obj.width * ESCALA, obj.height * ESCALA)
                    arvores.append((rect, pygame.transform.scale_by(obj.image, ESCALA)))
            self.mapas[nome] = (fundo, arvores)
        return self.mapas[nome]

    def sprite_npc(self, sprite_id):
        """Quadros parados e retrato de personagens/<sprite_id>/."""
        if sprite_id not in self.npcs:
            folha = carregar_imagem(f"personagens/{sprite_id}/parado.png")
            # Retrato de 38×38 ampliado na mesma escala da caixa de diálogo.
            retrato = carregar_imagem(f"personagens/{sprite_id}/retrato.png")
            self.npcs[sprite_id] = (recortar_quadros(folha, len(COLUNA), 1),
                                    pygame.transform.scale_by(retrato, ESCALA_CAIXA))
        return self.npcs[sprite_id]

    def quadros_moeda(self, imagem):
        """Os 4 quadros de uma folha de moeda (10×10 cada), ampliados."""
        if imagem not in self.moedas:
            folha = carregar_imagem(imagem)  # 4 quadros de 10×10 lado a lado
            self.moedas[imagem] = [pygame.transform.scale_by(
                folha.subsurface((i * TAMANHO_MOEDA, 0, TAMANHO_MOEDA, TAMANHO_MOEDA)), ESCALA)
                for i in range(QUADROS_MOEDA)]
        return self.moedas[imagem]

    def desenhar(self, jogo, controle, dt, tempo):
        """Desenha o quadro inteiro a partir do Model (jogo) e da interface (controle)."""
        tela = self.superficie
        if jogo.estado == Estado.MENU:
            # O herói "respira": sobe e desce seguindo uma onda (seno).
            respiracao = math.sin(tempo * RESPIRACAO_VELOCIDADE) * RESPIRACAO_ALTURA
            tela.fill(COR_FUNDO)  # fundo escuro: o título fica legível
            escrever(tela, self.fonte_jogo, NOME_JOGO, COR_DESTAQUE, 70)
            centro_heroi = (LARGURA // 2, 210 + respiracao)
            tela.blit(self.heroi_menu, self.heroi_menu.get_rect(center=centro_heroi))
            escrever(tela, self.fonte_titulo, f"Bem-vindo, {NOME}!", COR_DESTAQUE, 315)
            tela.blit(self.painel, self.painel.get_rect(center=(LARGURA // 2, 430)))
            desenhar_menu(tela, self.fonte, OPCOES_MENU, controle.escolha, 380)
            sistema = (f"IA: {MODELO_IA}  ·  Python {platform.python_version()}"
                       f"  ·  {platform.system()}")
            escrever(tela, self.fonte_fala, sistema, COR_APAGADA, 530)
            escrever(tela, self.fonte_fala, "Setas: escolher  ·  ENTER: confirmar  ·  ESC: sair",
                     COR_APAGADA, 565)
            return

        if jogo.estado == Estado.CREDITOS:
            tela.fill(COR_FUNDO)
            escrever(tela, self.fonte_jogo, "Créditos", COR_DESTAQUE, 90)
            escrever(tela, self.fonte_titulo, f"{NOME_JOGO}, um jogo de {NOME}", COR_TEXTO, 200)
            for i, linha in enumerate(CREDITOS):
                escrever(tela, self.fonte, linha, COR_TEXTO, 280 + i * 45)
            escrever(tela, self.fonte_fala, "ENTER ou ESC: voltar ao menu", COR_APAGADA, 545)
            return

        cena, heroi = jogo.cena, jogo.heroi
        # Animação por tempo: troca de quadro a cada TEMPO_QUADRO segundos andando.
        if heroi.andando:
            self.tempo_quadro += dt
            if self.tempo_quadro >= TEMPO_QUADRO:
                self.tempo_quadro -= TEMPO_QUADRO
                self.quadro = (self.quadro + 1) % QUADROS_ANDAR  # depois do último volta ao 0
            imagem_heroi = self.quadros_andar[COLUNA[heroi.direcao]][self.quadro]
        else:
            imagem_heroi = self.quadros_parado[COLUNA[heroi.direcao]][0]

        # Câmera: o herói no meio da tela, sem mostrar nada além das bordas do mapa.
        # int(): pixel inteiro; com casas decimais, chão e sprites arredondam diferente e tremem.
        fundo, arvores = self.mapa(cena.mapa)
        centro_x, centro_y = heroi.caixa.centro
        camera_x = int(min(max(centro_x - LARGURA // 2, 0), fundo.get_width() - LARGURA))
        camera_y = int(min(max(centro_y - ALTURA // 2, 0), fundo.get_height() - ALTURA))

        # Desenhar em camadas: o que é desenhado depois cobre o que veio antes.
        # Tudo o que é do mundo é desenhado deslocado pela câmera (- camera_x, - camera_y).
        # Camada 1, o chão do mapa.
        tela.blit(fundo, (-camera_x, -camera_y))
        # Camada 2, as entidades. Primeiro as sombras, que ficam no chão.
        for caixa in [npc.caixa for npc in cena.npcs] + [heroi.caixa]:
            tela.blit(self.sombra, self.sombra.get_rect(center=(caixa.centro[0] - camera_x,
                                                                caixa.base - 3 - camera_y)))
        # Depois árvores, moedas, NPCs e herói, em ordem de profundidade: quem tem a base
        # mais acima na tela é desenhado antes; quem está mais abaixo fica na frente.
        # Cada item: (x, y, base, imagem).
        sprites = [(rect.x, rect.y, rect.bottom, imagem) for rect, imagem in arvores]
        for npc in cena.npcs:
            quadros, _ = self.sprite_npc(npc.sprite_id)
            imagem = quadros[COLUNA[npc.direcao]][0]
            sprites.append((npc.caixa.x, npc.caixa.y, npc.caixa.base, imagem))
        for moeda in cena.moedas:
            quadros = self.quadros_moeda(moeda.imagem)
            imagem = quadros[int(tempo / TEMPO_QUADRO_MOEDA) % QUADROS_MOEDA]
            sprites.append((moeda.caixa.x, moeda.caixa.y, moeda.caixa.base, imagem))
        sprites.append((heroi.caixa.x, heroi.caixa.y, heroi.caixa.base, imagem_heroi))
        for x, y, _, imagem in sorted(sprites, key=lambda sprite: sprite[2]):
            tela.blit(imagem, (x - camera_x, y - camera_y))

        # Camada 3, a interface: sempre por cima do mundo.
        tela.blit(self.faixa, (0, 0))
        escrever(tela, self.fonte, cena.nome, COR_TEXTO, 20)
        # HUD: ícone da moeda e o total da bolsa, no canto esquerdo da faixa.
        tela.blit(self.icone_moeda, (12, 5))
        tela.blit(self.fonte.render(str(heroi.moedas), False, COR_DESTAQUE), (50, 3))
        perto = jogo.npc_perto()
        if jogo.estado == Estado.EXPLORANDO and perto:
            escrever(tela, self.fonte, "ESPAÇO para falar", COR_DESTAQUE,
                     perto.caixa.y - 15 - camera_y, perto.caixa.centro[0] - camera_x)
        elif jogo.estado == Estado.DIALOGO:
            _, retrato = self.sprite_npc(controle.dialogo.npc.sprite_id)
            controle.dialogo.desenhar(tela, self.caixa, retrato, tempo)
        elif jogo.estado == Estado.PAUSA:
            tela.blit(self.veu, (0, 0))
            escrever(tela, self.fonte_jogo, "Pausa", COR_DESTAQUE, 220)
            tela.blit(self.painel, self.painel.get_rect(center=(LARGURA // 2, 375)))
            desenhar_menu(tela, self.fonte, OPCOES_PAUSA, controle.escolha, 350)
        if jogo.escuro:  # a transição cobre tudo, inclusive a interface
            self.escuridao.set_alpha(int(jogo.escuro * 255))
            tela.blit(self.escuridao, (0, 0))

"""
RPG Engine — configuração do jogo.

Tudo o que é ajuste (tamanhos, velocidades, tempos, caminhos, nomes) mora aqui.
O main.py só usa estes nomes: para mudar o jogo, você mexe neste arquivo,
não na lógica. Os segredos continuam no .env, que nunca vai para o Git.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# Caminhos sempre a partir deste arquivo: o jogo roda de qualquer pasta.
PASTA_PROJETO = Path(__file__).resolve().parent.parent  # src/ fica dentro do projeto
PASTA_ASSETS = PASTA_PROJETO / "assets"
FONTE_PIXEL = PASTA_ASSETS / "fontes" / "Jersey10-Regular.ttf"

# Lê o arquivo .env e carrega as variáveis (a chave do Gemini fica só lá).
load_dotenv(PASTA_PROJETO / ".env")
NOME = os.getenv("NOME_ENGENHEIRO", "Engenheiro")
MODELO_IA = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
NOME_JOGO = "Kernel Quest"  # o nome que você escolheu para o jogo

# Janela e ritmo
LARGURA, ALTURA = 800, 600
FPS = 60
TETO_DT = 0.1  # maior dt aceito: depois de um congelamento (a IA pensando), nada de teletransporte
TAMANHO_TILE = 16  # tiles e sprites do pacote têm 16×16 pixels
ESCALA = 3  # tiles e sprites de 16×16 aparecem 3× maiores (48 px)
TAMANHO_SPRITE = TAMANHO_TILE * ESCALA  # herói e NPCs ocupam 48×48 na tela
ESCALA_CAIXA = 2.6  # caixa de diálogo e retrato: a 3× a caixa passaria dos 800 px da janela
ESCALA_HEROI_MENU = 8  # o herói grande do menu principal

# Cores (vermelho, verde, azul)
COR_TEXTO = (240, 240, 240)
COR_DESTAQUE = (255, 215, 0)
COR_CAIXA = (60, 40, 40)  # texto escuro sobre o papel claro da caixa de diálogo
COR_APAGADA = (160, 160, 170)  # textos de ajuda, no rodapé das telas
COR_FUNDO = (24, 20, 32)  # fundo escuro do menu e dos créditos
# Com um 4º número, o alpha: de 0 (invisível) a 255 (opaco).
COR_PAINEL = (10, 10, 20, 190)
COR_FAIXA = (10, 10, 20, 210)
COR_VEU = (10, 10, 20, 160)  # escurece o mundo atrás do menu de pausa

# Fontes (Jersey 10), em pixels
TAMANHO_FONTE_JOGO = 96
TAMANHO_FONTE_TITULO = 48
TAMANHO_FONTE = 32
TAMANHO_FONTE_FALA = 28

# Menu principal: o herói "respira" subindo e descendo
RESPIRACAO_VELOCIDADE = 3
RESPIRACAO_ALTURA = 6  # pixels para cima e para baixo

# Herói
VELOCIDADE = 200  # pixels por SEGUNDO (multiplicada por dt, vale em qualquer FPS)
TEMPO_QUADRO = 0.15  # segundos que cada quadro da caminhada fica na tela
QUADROS_ANDAR = 4  # quadros da caminhada por direção (linhas de andar.png)
# Ordem das colunas nas folhas do pacote (andar.png e parado.png).
COLUNA = {"baixo": 0, "cima": 1, "esquerda": 2, "direita": 3}

# Moedas
TAMANHO_MOEDA = 10  # cada quadro de itens/moeda.png tem 10×10 pixels
QUADROS_MOEDA = 4
TEMPO_QUADRO_MOEDA = 0.12  # a moeda gira mais rápido que o herói anda
# Padrões de cada moeda; um objeto do Tiled pode trocar com as propriedades "imagem" e "valor".
IMAGEM_MOEDA = "itens/moeda.png"
VALOR_MOEDA = 1

# IA
TIMEOUT_IA_MS = 30_000  # sem isso, uma rede travada deixaria o jogo esperando para sempre
INTERVALO_MINIMO = 2.0  # segundos entre duas chamadas à IA (reduz o risco do erro 429)
ALCANCE_CONVERSA = 100  # pixels somados ao NPC (50 de cada lado) para dar para falar com ele

# Caixa de diálogo
LARGURA_TEXTO = 580  # largura máxima de uma linha na caixa de diálogo, em pixels
LINHAS_POR_PAGINA = 3
VELOCIDADE_ESCRITA = 40  # letras por segundo da máquina de escrever
PISCA_POR_SEGUNDO = 3  # quantas vezes por segundo o ▼ acende ou apaga
LETRAS_POR_VOZ = 6  # a "voz" do NPC toca a cada 6 letras novas
VOLUME_VOZ = 0.3  # baixinho: toca muitas vezes por fala

# Transição entre mapas
DURACAO_ESCURECER = 0.3  # segundos para a tela escurecer (e outros tantos para clarear)

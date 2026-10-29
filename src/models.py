"""
RPG Engine — Model: os dados e as regras do jogo.

Nada de pygame aqui, só Python. O Model sabe onde cada coisa está e o que
acontece quando o herói anda, pega uma moeda ou toca num portal, mas não
sabe desenhar, tocar som nem ler o teclado. Por isso dá para testá-lo sem
abrir janela (M04A).
"""
from dataclasses import dataclass, field
from enum import Enum, auto

from src.config import (
    ALCANCE_CONVERSA, DURACAO_ESCURECER, IMAGEM_MOEDA, TAMANHO_SPRITE, VALOR_MOEDA, VELOCIDADE,
)


class Estado(Enum):
    """Os estados do jogo: em cada um, as teclas fazem uma coisa diferente."""
    MENU = auto()
    EXPLORANDO = auto()
    DIALOGO = auto()
    PAUSA = auto()
    CREDITOS = auto()
    TRANSICAO = auto()  # a tela escurece, o mapa troca no escuro e a tela clareia


# Para onde cada estado pode ir. Qualquer mudança fora desta tabela é bug.
TRANSICOES = {
    Estado.MENU: {Estado.EXPLORANDO, Estado.CREDITOS},
    Estado.EXPLORANDO: {Estado.DIALOGO, Estado.PAUSA, Estado.TRANSICAO},
    Estado.DIALOGO: {Estado.EXPLORANDO},
    Estado.PAUSA: {Estado.EXPLORANDO, Estado.MENU},
    Estado.CREDITOS: {Estado.MENU},
    Estado.TRANSICAO: {Estado.EXPLORANDO},
}


# Dados do mundo: as personas dos NPCs (texto puro, então moram no Model).
# Formato comum a todas as personas: cabe em até 3 páginas da caixa de diálogo.
FORMATO = ("Responda em português, em texto simples (sem Markdown), "
           "em até 4 frases curtas, com no máximo 50 palavras no total.")

# Instrução de sistema: quem o Mago é. Vai separada da fala do jogador.
INSTRUCAO_MAGO = (
    "Você é o Arquimago Solaris, mentor exigente e seco num castelo medieval sombrio. "
    "Trata magia como arquitetura e cobra método do aprendiz, com ironia rara e sem insultar. "
    "Sempre lembra o aprendiz do Cristal de Kernel, guardado no fundo da masmorra. "
    + FORMATO
)
INSTRUCAO_SENTINELA = (
    "Você é a Sentinela do Salão, veterana de guerra lacônica e pragmática. "
    "Já viu aprendizes demais morrerem por pressa e mede cada um pelo que faz. "
    + FORMATO
)
INSTRUCAO_BROK = (
    "Você é Brok, mercador da floresta: frio, calculista e educado na medida do lucro. "
    "Não dá desconto, não vende fiado e lembra cada dívida, mas esconde uma dívida sua com o castelo. "
    + FORMATO
)
INSTRUCAO_CACADOR = (
    "Você é Rurik, caçador da floresta: rude no trato e paciente na espreita. "
    "Vende ao Brok o gel dos slimes que caça e sabe que ele paga menos do que vale. "
    "Conhece as trilhas até a masmorra, mas não ensina nada de graça. "
    + FORMATO
)


@dataclass
class Retangulo:
    """Posição e tamanho em pixels do mapa (já ampliado), como um pygame.Rect, mas sem pygame."""
    x: float
    y: float
    largura: float
    altura: float

    @property
    def base(self):
        return self.y + self.altura

    @property
    def centro(self):
        return (self.x + self.largura / 2, self.y + self.altura / 2)

    def colide(self, outro):
        """True se os dois se sobrepõem (só encostar a borda não conta)."""
        return (self.x < outro.x + outro.largura and outro.x < self.x + self.largura
                and self.y < outro.y + outro.altura and outro.y < self.y + self.altura)

    def ampliado(self, margem):
        """Um retângulo maior com o mesmo centro: margem / 2 a mais de cada lado."""
        return Retangulo(self.x - margem / 2, self.y - margem / 2,
                         self.largura + margem, self.altura + margem)


def retangulo_no_centro(centro, largura, altura):
    """O retângulo de largura × altura com o meio em `centro` (x, y)."""
    return Retangulo(centro[0] - largura / 2, centro[1] - altura / 2, largura, altura)


@dataclass
class Heroi:
    """O herói: onde está, para onde olha e o que carrega."""
    caixa: Retangulo
    sprite_id: str = "heroi"  # a View escolhe a imagem por este nome
    direcao: str = "baixo"
    andando: bool = False
    moedas: int = 0
    inventario: list = field(default_factory=list)  # a loja (M03C) e a Chave (M06B) usam


@dataclass
class NPC:
    """Um personagem: nome, sprite, posição e instrução de sistema (a persona)."""
    nome: str
    sprite_id: str
    caixa: Retangulo
    instrucao: str
    direcao: str = "baixo"

    @property
    def area_conversa(self):
        """Perto o bastante para falar: a caixa do NPC alargada nos quatro lados."""
        return self.caixa.ampliado(ALCANCE_CONVERSA)


@dataclass
class Moeda:
    """Uma moeda no chão: onde está, quanto vale e qual imagem a View usa."""
    caixa: Retangulo
    valor: int = VALOR_MOEDA
    imagem: str = IMAGEM_MOEDA


@dataclass
class Cena:
    """Um lugar do mundo: os dados que vieram do mapa do Tiled e os NPCs."""
    nome: str
    mapa: str  # nome do arquivo .tmx, sem extensão; a música tem o mesmo nome
    area: Retangulo  # o mapa inteiro: o herói não sai daqui
    npcs: list
    moedas: list
    colisoes: list  # [Retangulo]
    portais: list  # [(Retangulo, nome do mapa de destino)]
    chegadas: dict  # nome do mapa de origem (ou "inicio") -> centro (x, y)


class Jogo:
    """O jogo inteiro: as cenas, a cena atual, o herói, o estado e as regras."""

    def __init__(self, cenas):
        self.cenas = cenas
        self.cena = cenas["salao"]
        self.heroi = Heroi(Retangulo(0, 0, TAMANHO_SPRITE, TAMANHO_SPRITE))
        self.estado = Estado.MENU  # o jogo começa no menu principal
        self.escuro = 0.0  # 0 = tela normal, 1 = tela preta (transição entre mapas)
        self.indo_para = None  # o mapa de destino enquanto a tela escurece

    def mudar_estado(self, novo):
        """Muda de estado só se a tabela TRANSICOES permitir; senão, avisa e fica onde está."""
        if novo not in TRANSICOES[self.estado]:
            print(f"[BLOQUEADO] {self.estado.name} -> {novo.name}: fora da tabela de transições")
            return
        print(f"[ESTADO] {self.estado.name} -> {novo.name}")
        self.estado = novo

    def novo_jogo(self, cenas):
        """Começa do zero: mapas relidos (moedas de volta ao chão), bolsa e inventário vazios."""
        self.cenas = cenas
        self.cena = cenas["salao"]
        self.heroi.moedas = 0
        self.heroi.inventario = []
        self.posicionar_heroi("inicio")
        self.mudar_estado(Estado.EXPLORANDO)

    def posicionar_heroi(self, chegada):
        """Põe o herói no ponto de chegada da cena atual com esse nome."""
        centro_x, centro_y = self.cena.chegadas[chegada]
        caixa = self.heroi.caixa
        caixa.x, caixa.y = centro_x - caixa.largura / 2, centro_y - caixa.altura / 2

    def npc_perto(self):
        """O NPC ao alcance da conversa, se houver (basta o primeiro)."""
        for npc in self.cena.npcs:
            if self.heroi.caixa.colide(npc.area_conversa):
                return npc
        return None

    def mover_heroi(self, dx, dy, direcao, dt):
        """Anda dx, dy (-1, 0 ou 1) por dt segundos, sem atravessar obstáculos nem sair do mapa.

        Um eixo de cada vez: se bater num obstáculo, desfaz só o eixo que colidiu
        (assim o herói ainda desliza ao longo dele no outro eixo).
        """
        heroi = self.heroi
        heroi.andando = bool(dx or dy)
        if heroi.andando:
            heroi.direcao = direcao
        caixa = heroi.caixa
        obstaculos = self.cena.colisoes + [npc.caixa for npc in self.cena.npcs]
        caixa.x += dx * VELOCIDADE * dt
        if any(caixa.colide(obstaculo) for obstaculo in obstaculos):
            caixa.x -= dx * VELOCIDADE * dt
        caixa.y += dy * VELOCIDADE * dt
        if any(caixa.colide(obstaculo) for obstaculo in obstaculos):
            caixa.y -= dy * VELOCIDADE * dt
        # Mantém o herói dentro do mapa.
        area = self.cena.area
        caixa.x = min(max(caixa.x, area.x), area.x + area.largura - caixa.largura)
        caixa.y = min(max(caixa.y, area.y), area.y + area.altura - caixa.altura)

    def coletar_moedas(self):
        """Pega as moedas que o herói toca; devolve quantas pegou (o Controller toca o som)."""
        pegas = 0
        for moeda in self.cena.moedas[:]:  # uma cópia: a lista muda dentro do for
            if self.heroi.caixa.colide(moeda.caixa):
                self.cena.moedas.remove(moeda)
                self.heroi.moedas += moeda.valor
                pegas += 1
        return pegas

    def tocar_portal(self):
        """Se o herói toca um portal, começa a transição para o destino dele."""
        for portal, destino in self.cena.portais:
            if self.heroi.caixa.colide(portal):
                self.indo_para = destino
                self.mudar_estado(Estado.TRANSICAO)
                return

    def atualizar_transicao(self, dt):
        """Escurece, troca o mapa no preto e clareia. Devolve True no quadro da troca do mapa."""
        if self.indo_para:
            self.escuro = min(self.escuro + dt / DURACAO_ESCURECER, 1.0)  # escurecendo
            if self.escuro == 1.0:  # tela preta: troca o mapa sem o jogador ver
                origem = self.cena.mapa
                self.cena = self.cenas[self.indo_para]
                self.posicionar_heroi(origem)  # o ponto com o nome de onde ele veio
                self.indo_para = None
                return True
        else:
            self.escuro = max(self.escuro - dt / DURACAO_ESCURECER, 0.0)  # clareando
            if self.escuro == 0.0:
                self.mudar_estado(Estado.EXPLORANDO)
        return False

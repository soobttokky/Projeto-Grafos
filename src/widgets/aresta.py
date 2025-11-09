from PyQt5.QtWidgets import QGraphicsPathItem, QGraphicsTextItem
from PyQt5.QtGui import QPainterPath, QPen, QColor, QFont
from PyQt5.QtCore import Qt, QPointF


class ItemAresta(QGraphicsPathItem):
    def __init__(self, no_origem, no_destino, peso, scene=None):
        super().__init__()
        self.no_origem = no_origem
        self.no_destino = no_destino
        self.peso = peso
        self.e_reciproca = False  # Indica se há uma aresta recíproca (destino para origem)
        self.item_texto_aresta = None  # Referência para o item de texto do peso
        self.cena = scene  # Referência à cena para adicionar/remover o texto

        self.setZValue(-1)  # Desenha as arestas abaixo dos nós
        self.setPen(QPen(QColor(0, 0, 0), 2))  # Caneta padrão preta, 2px de espessura

        self.atualizar_posicao()

    def atualizar_posicao(self):
        path = QPainterPath()
        p1 = self.no_origem.pos()
        p2 = self.no_destino.pos()

        # Calcular a direção da aresta
        dx = p2.x() - p1.x()
        dy = p2.y() - p1.y()
        dist = (dx ** 2 + dy ** 2) ** 0.5

        if dist == 0:  # Evita divisão por zero se os nós estiverem sobrepostos
            return

        # Calcular a posição do texto no meio da aresta
        mid_x = (p1.x() + p2.x()) / 2
        mid_y = (p1.y() + p2.y()) / 2

        # Offset para o texto da aresta
        offset_x = -dy / dist * 10  # 10 é um valor arbitrário para o offset
        offset_y = dx / dist * 10

        # Ajuste para arestas recíprocas (se desejar visualmente distintas)
        # Se for reciproca, move a linha para o lado
        if self.e_reciproca:
            line_offset_x = -dy / dist * 5
            line_offset_y = dx / dist * 5
            p1 += QPointF(line_offset_x, line_offset_y)
            p2 += QPointF(line_offset_x, line_offset_y)
            mid_x += line_offset_x
            mid_y += line_offset_y

        path.moveTo(p1)
        path.lineTo(p2)

        # Adicionar ponta de seta (seta para grafos direcionados)
        tamanho_seta = 15
        angulo = Qt.convertFromNativeGesture(p2 - p1).angle()

        # Calcula a posição da ponta da seta para que não sobreponha o nó de destino
        # (reduzindo o comprimento da linha para terminar antes do centro do nó)
        reducao_x = (self.no_destino.boundingRect().width() / 2) * (dx / dist)
        reducao_y = (self.no_destino.boundingRect().height() / 2) * (dy / dist)
        p2_ajustado = QPointF(p2.x() - reducao_x, p2.y() - reducao_y)

        # Desenha a seta na ponta ajustada
        path.moveTo(p2_ajustado)
        path.lineTo(p2_ajustado - QPointF(tamanho_seta * (dx / dist) + tamanho_seta * (dy / dist),
                                          tamanho_seta * (dy / dist) - tamanho_seta * (dx / dist)))
        path.moveTo(p2_ajustado)
        path.lineTo(p2_ajustado - QPointF(tamanho_seta * (dx / dist) - tamanho_seta * (dy / dist),
                                          tamanho_seta * (dy / dist) + tamanho_seta * (dx / dist)))

        self.setPath(path)

        # Atualizar a posição do texto do peso
        if self.item_texto_aresta:
            self.item_texto_aresta.setPos(mid_x + offset_x - self.item_texto_aresta.boundingRect().width() / 2,
                                          mid_y + offset_y - self.item_texto_aresta.boundingRect().height() / 2)

    def adicionar_texto_a_cena(self, cena):
        # AQUI É A MUDANÇA IMPORTANTE:
        # Se o texto da aresta for um item separado, ele deve ser adicionado à cena explicitamente.
        # Mas para garantir que ele seja removido quando a aresta for,
        # e para que ele se mova junto, é melhor torná-lo filho da aresta.
        # No entanto, QGraphicsPathItem não é um QGraphicsObject, então não tem `childrenBoundingRect`.
        # Manter como item separado mas gerenciar sua remoção.
        if self.item_texto_aresta is None:
            self.item_texto_aresta = QGraphicsTextItem(str(self.peso))
            self.item_texto_aresta.setFont(QFont("Arial", 10))
            self.item_texto_aresta.setDefaultTextColor(QColor(0, 0, 0))
            # Ajustar Z-value para que o texto fique acima da linha da aresta, mas abaixo dos nós
            self.item_texto_aresta.setZValue(0)  # Acima da aresta (-1), abaixo dos nós (1)
            cena.addItem(self.item_texto_aresta)
        self.atualizar_posicao()  # Garante que o texto seja posicionado corretamente

    def paint(self, painter, option, widget):
        painter.setPen(self.pen())
        painter.drawPath(self.path())
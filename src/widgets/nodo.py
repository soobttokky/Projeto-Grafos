from PyQt5.QtWidgets import QGraphicsEllipseItem, QGraphicsTextItem
from PyQt5.QtGui import QBrush, QColor, QPen, QFont
from PyQt5.QtCore import Qt, QRectF

class ItemNo(QGraphicsEllipseItem):
    def __init__(self, rotulo, parent=None):
        super().__init__(-20, -20, 40, 40, parent) # x, y, width, height (centrado)
        self.rotulo = rotulo
        self.arestas = [] # Lista de arestas conectadas a este nó
        self.setBrush(QBrush(QColor(255, 255, 255))) # Fundo branco
        self.setPen(QPen(QColor(0, 0, 0), 2)) # Borda preta, 2px de espessura
        self.setFlags(QGraphicsEllipseItem.ItemIsMovable | QGraphicsEllipseItem.ItemIsSelectable)
        self.setZValue(1) # Desenha os nós acima das arestas

        # Adicionar o texto do rótulo como um item filho
        self.item_texto = QGraphicsTextItem(self.rotulo, self)
        self.item_texto.setFont(QFont("Arial", 10, QFont.Bold))
        self.item_texto.setDefaultTextColor(QColor(0, 0, 0))
        self.item_texto.setPos(-self.item_texto.boundingRect().width() / 2,
                               -self.item_texto.boundingRect().height() / 2)

    def adicionar_aresta(self, aresta):
        if aresta not in self.arestas:
            self.arestas.append(aresta)

    def remover_aresta(self, aresta):
        if aresta in self.arestas:
            self.arestas.remove(aresta)

    def itemChange(self, change, value):
        if change == QGraphicsEllipseItem.ItemPositionHasChanged and self.scene():
            for aresta in self.arestas:
                aresta.atualizar_posicao()
        return super().itemChange(change, value)

    def paint(self, painter, option, widget):
        # Desenha a elipse do nó
        painter.setBrush(self.brush())
        painter.setPen(self.pen())
        painter.drawEllipse(self.rect())

        # O texto do rótulo é um item filho, então ele é desenhado automaticamente.
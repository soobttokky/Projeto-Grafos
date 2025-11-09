from PyQt5.QtCore import QObject, pyqtSignal, QPointF
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsItem, QInputDialog, QMessageBox
from PyQt5.QtGui import QColor, QTransform

from src.widgets.nodo import ItemNo
from src.widgets.aresta import ItemAresta


class VisualizadorGrafo(QObject):
    grafoAlterado = pyqtSignal()

    def __init__(self, cena: QGraphicsScene):
        super().__init__()
        self.cena = cena
        self.nos = {}  # Dicionário para armazenar nós (rótulo: ItemNo)
        self.arestas = []  # Lista para armazenar arestas (ItemAresta)
        self.no_selecionado = None
        self.modo_adicao_aresta = False
        self.origem_adicao_aresta = None
        self.posicao_clique_inicial = None  # Para arrastar a cena

        self.cena.setSceneRect(-self.cena.width() / 2, -self.cena.height() / 2, self.cena.width(), self.cena.height())

    def adicionar_no(self, rotulo, x, y):
        if rotulo in self.nos:
            return None  # Nó com este rótulo já existe

        novo_no = ItemNo(rotulo)
        novo_no.setPos(x, y)
        self.cena.addItem(novo_no)
        self.nos[rotulo] = novo_no
        self.grafoAlterado.emit()
        return novo_no

    def adicionar_aresta(self, rotulo_origem, rotulo_destino, peso=1, e_reciproca=False):
        no_origem = self.nos.get(rotulo_origem)
        no_destino = self.nos.get(rotulo_destino)

        if not no_origem or not no_destino:
            return None  # Nó(s) não encontrado(s)

        # Verificar se a aresta já existe (evitar duplicatas)
        for aresta_existente in self.arestas:
            if (aresta_existente.no_origem == no_origem and aresta_existente.no_destino == no_destino):
                return None  # Aresta já existe

        nova_aresta = ItemAresta(no_origem, no_destino, peso, self.cena)
        self.arestas.append(nova_aresta)
        no_origem.adicionar_aresta(nova_aresta)
        no_destino.adicionar_aresta(nova_aresta)  # Adiciona ao destino também para facilitar a exclusão

        self.cena.addItem(nova_aresta)
        nova_aresta.adicionar_texto_a_cena(self.cena)  # Adiciona o texto ao scene (se for filho da cena)

        if e_reciproca:
            self.adicionar_aresta(rotulo_destino, rotulo_origem, peso,
                                  False)  # Adiciona a recíproca sem ser recíproca novamente

        self.grafoAlterado.emit()
        return nova_aresta

    def deletar_aresta(self, aresta_para_deletar):
        if aresta_para_deletar not in self.arestas:
            return

        # Remover a aresta dos nós de origem e destino
        if aresta_para_deletar in aresta_para_deletar.no_origem.arestas:
            aresta_para_deletar.no_origem.arestas.remove(aresta_para_deletar)
        if aresta_para_deletar in aresta_para_deletar.no_destino.arestas:
            aresta_para_deletar.no_destino.arestas.remove(aresta_para_deletar)

        # Remover texto da cena (se for um item separado)
        if aresta_para_deletar.item_texto_aresta and aresta_para_deletar.item_texto_aresta.scene():
            self.cena.removeItem(aresta_para_deletar.item_texto_aresta)

        # Remover a aresta da cena
        if aresta_para_deletar.scene():
            self.cena.removeItem(aresta_para_deletar)

        # Remover do controle do grafo
        self.arestas.remove(aresta_para_deletar)

        # Se houver uma aresta recíproca, atualiza sua geometria se ela ainda existir
        # A lógica de aresta recíproca deve ser mais robusta.
        # Se você está usando `e_reciproca` para criar um par (A->B, B->A),
        # a remoção de uma não deve automaticamente remover a outra, mas apenas
        # se o conceito for de uma "borda dupla" visual.
        # Para um grafo simples com arestas direcional separadas:
        # Quando A->B é excluído, B->A não é afetado.
        # Se você quer um "par" lógico:
        # for outra_aresta in self.arestas:
        #     if outra_aresta.no_origem == aresta_para_deletar.no_destino and \
        #        outra_aresta.no_destino == aresta_para_deletar.no_origem:
        #         outra_aresta.e_reciproca = False # Ou você deleta a outra também
        #         outra_aresta.atualizar_posicao()
        #         break

        self.grafoAlterado.emit()

    def deletar_no(self, no_para_deletar):
        """Deleta um nó e todas as arestas conectadas a ele."""
        if no_para_deletar.rotulo not in self.nos:
            return

        # Coletar todas as arestas conectadas a este nó ANTES de tentar deletá-las.
        # Iteramos sobre self.arestas (a lista principal) para garantir que
        # pegamos todas as arestas, independentemente da direção.
        arestas_para_remover = []
        for aresta in list(self.arestas):  # Criar uma cópia para evitar problemas de iteração
            if aresta.no_origem == no_para_deletar or aresta.no_destino == no_para_deletar:
                arestas_para_remover.append(aresta)

        # Deletar todas as arestas conectadas ao nó
        for aresta in arestas_para_remover:
            self.deletar_aresta(aresta)

        # Agora que todas as arestas conectadas foram removidas, podemos remover o nó com segurança.
        del self.nos[no_para_deletar.rotulo]
        if no_para_deletar.item_texto and no_para_deletar.item_texto.scene():
            self.cena.removeItem(no_para_deletar.item_texto)  # Remover o texto do nó
        if no_para_deletar.scene():
            self.cena.removeItem(no_para_deletar)  # Remover o próprio nó

        if self.no_selecionado == no_para_deletar:
            self.no_selecionado = None

        self.grafoAlterado.emit()

    def limpar_selecao_no(self):
        if self.no_selecionado:
            self.no_selecionado.setBrush(QColor(255, 255, 255))  # Cor original
            self.no_selecionado = None

    def mousePressEvent(self, event):
        item = self.cena.itemAt(event.scenePos(), QTransform())

        if self.modo_adicao_aresta:
            if isinstance(item, ItemNo):
                if self.origem_adicao_aresta is None:
                    self.origem_adicao_aresta = item
                    item.setBrush(QColor(255, 165, 0))  # Laranja para origem
                else:
                    destino = item
                    # Perguntar o peso
                    peso, ok = QInputDialog.getInt(None, "Peso da Aresta",
                                                   f"Entre com o peso da aresta de {self.origem_adicao_aresta.rotulo} para {destino.rotulo}:",
                                                   1, 1, 1000, 1)
                    if ok:
                        self.adicionar_aresta(self.origem_adicao_aresta.rotulo, destino.rotulo, peso)
                        resposta = QMessageBox.question(None, "Aresta Recíproca",
                                                        f"Deseja adicionar uma aresta de {destino.rotulo} para {self.origem_adicao_aresta.rotulo} com o mesmo peso?",
                                                        QMessageBox.Yes | QMessageBox.No)
                        if resposta == QMessageBox.Yes:
                            self.adicionar_aresta(destino.rotulo, self.origem_adicao_aresta.rotulo, peso)
                    self.origem_adicao_aresta.setBrush(QColor(255, 255, 255))  # Voltar à cor original
                    self.origem_adicao_aresta = None
                    self.modo_adicao_aresta = False
            else:
                # Clicou fora de um nó no modo de adição de aresta
                if self.origem_adicao_aresta:
                    self.origem_adicao_aresta.setBrush(QColor(255, 255, 255))  # Voltar à cor original
                    self.origem_adicao_aresta = None
                self.modo_adicao_aresta = False

        elif event.button() == 1:  # Botão esquerdo
            if item and isinstance(item, ItemNo):
                self.limpar_selecao_no()
                self.no_selecionado = item
                self.no_selecionado.setBrush(QColor(173, 216, 230))  # Azul claro para selecionado
                self.posicao_clique_inicial = event.scenePos()
            else:
                self.limpar_selecao_no()
                self.posicao_clique_inicial = event.screenPos()  # Para arrastar a cena
                self.cena.views()[0].setDragMode(self.cena.views()[0].ScrollHandDrag)


        elif event.button() == 2:  # Botão direito (selecionar aresta para exclusão)
            if item and isinstance(item, ItemAresta):
                resposta = QMessageBox.question(None, "Deletar Aresta",
                                                f"Deseja deletar a aresta de {item.no_origem.rotulo} para {item.no_destino.rotulo} (Peso: {item.peso})?",
                                                QMessageBox.Yes | QMessageBox.No)
                if resposta == QMessageBox.Yes:
                    self.deletar_aresta(item)
            elif item and isinstance(item, ItemNo):
                resposta = QMessageBox.question(None, "Deletar Nó",
                                                f"Deseja deletar o nó '{item.rotulo}' e todas as arestas conectadas a ele?",
                                                QMessageBox.Yes | QMessageBox.No)
                if resposta == QMessageBox.Yes:
                    self.deletar_no(item)

    def mouseMoveEvent(self, event):
        if self.no_selecionado and event.buttons() == 1:  # Arrastando o nó selecionado
            nova_posicao = event.scenePos()
            self.no_selecionado.setPos(nova_posicao)
            for aresta in self.no_selecionado.arestas:
                aresta.atualizar_posicao()
            self.grafoAlterado.emit()
        elif event.buttons() == 1 and self.posicao_clique_inicial is not None and not self.no_selecionado:
            # Arrastando a cena
            view = self.cena.views()[0]
            delta = event.screenPos() - self.posicao_clique_inicial
            h_bar = view.horizontalScrollBar()
            v_bar = view.verticalScrollBar()
            h_bar.setValue(h_bar.value() - delta.x())
            v_bar.setValue(v_bar.value() - delta.y())
            self.posicao_clique_inicial = event.screenPos()

    def mouseReleaseEvent(self, event):
        if self.posicao_clique_inicial is not None and not self.no_selecionado:
            # Parar de arrastar a cena
            self.cena.views()[0].setDragMode(self.cena.views()[0].NoDrag)
            self.posicao_clique_inicial = None

    def keyPressEvent(self, event):
        if event.key() == 16777223 and self.no_selecionado:  # Tecla Delete
            resposta = QMessageBox.question(None, "Deletar Nó",
                                            f"Deseja deletar o nó '{self.no_selecionado.rotulo}' e todas as arestas conectadas a ele?",
                                            QMessageBox.Yes | QMessageBox.No)
            if resposta == QMessageBox.Yes:
                self.deletar_no(self.no_selecionado)

    def mostrar_matriz_adjacencia(self):
        if not self.nos:
            QMessageBox.information(None, "Matriz de Adjacência", "O grafo está vazio.")
            return

        rotulos_ordenados = sorted(self.nos.keys())
        n = len(rotulos_ordenados)
        matriz = [[0] * n for _ in range(n)]

        # Preencher a matriz com os pesos das arestas
        for aresta in self.arestas:
            try:
                i = rotulos_ordenados.index(aresta.no_origem.rotulo)
                j = rotulos_ordenados.index(aresta.no_destino.rotulo)
                matriz[i][j] = aresta.peso
            except ValueError:
                # Isso não deveria acontecer se o grafo for consistente, mas é uma proteção
                print(
                    f"Erro: Nó da aresta {aresta.no_origem.rotulo}->{aresta.no_destino.rotulo} não encontrado na lista ordenada.")

        # Construir a string da matriz para exibição
        matriz_str = "Matriz de Adjacência:\n\n"
        # Cabeçalho das colunas
        matriz_str += "    " + " ".join(f"{r:<3}" for r in rotulos_ordenados) + "\n"
        matriz_str += "   " + "-" * (4 * n) + "\n"

        for i, rotulo_origem in enumerate(rotulos_ordenados):
            row_str = f"{rotulo_origem:<3}| "
            for j in range(n):
                row_str += f"{matriz[i][j]:<3} "
            matriz_str += row_str + "\n"

        QMessageBox.information(None, "Matriz de Adjacência", matriz_str)

    def mostrar_lista_adjacencia(self):
        if not self.nos:
            QMessageBox.information(None, "Lista de Adjacência", "O grafo está vazio.")
            return

        lista_adj_str = "Lista de Adjacência:\n\n"
        rotulos_ordenados = sorted(self.nos.keys())

        for rotulo_no in rotulos_ordenados:
            no = self.nos[rotulo_no]
            vizinhos = []
            # Percorre todas as arestas do grafo para encontrar as que saem do nó atual
            for aresta in self.arestas:
                if aresta.no_origem == no:
                    vizinhos.append(f"{aresta.no_destino.rotulo}({aresta.peso})")

            if vizinhos:
                lista_adj_str += f"{rotulo_no}: {', '.join(vizinhos)}\n"
            else:
                lista_adj_str += f"{rotulo_no}: \n"

        QMessageBox.information(None, "Lista de Adjacência", lista_adj_str)
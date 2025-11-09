# src/janela_principal.py

from PyQt5.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene, \
    QToolBar, QAction, QInputDialog, QMessageBox, QWidget, QVBoxLayout
from PyQt5.QtGui import QIcon, QTransform
from PyQt5.QtCore import Qt, QPointF

# Certifique-se de que estes imports estejam corretos
from grafo import VisualizadorGrafo
# Se você moveu as funções para 'algoritmos_grafo.py', use:
from algoritmos_grafo import construir_grafo_nx_da_matriz, obter_todas_rotas, obter_caminho_mais_curto, \
    obter_caminho_mais_longo_seguro  # Importa funções de algoritmos de grafo.


# Caso contrário, se as manteve em 'grafo.py', remova as duas linhas acima
# e mantenha apenas:
# from grafo import VisualizadorGrafo, construir_grafo_nx_da_matriz, obter_todas_rotas, obter_caminho_mais_curto, \
#     obter_caminho_mais_longo_seguro

class JanelaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visualizador de Grafos")
        self.setGeometry(100, 100, 1000, 700)  # x, y, width, height

        # 1. Crie a QGraphicsScene primeiro
        self.cena = QGraphicsScene(self)  # Pass self as parent
        self.cena.setSceneRect(0, 0, 980, 680)  # Definir um retângulo para a cena (opcional, pode ser ajustado)

        # 2. Crie a QGraphicsView e associe-a à cena
        self.view = QGraphicsView(self.cena, self)
        self.setCentralWidget(self.view)

        # 3. Agora, passe a cena para o VisualizadorGrafo
        self.visualizador_grafo = VisualizadorGrafo(self.cena)  # <--- AQUI ESTÁ A CORREÇÃO

        # Conectar os eventos de mouse e teclado da View ao VisualizadorGrafo
        self.view.mousePressEvent = self.visualizador_grafo.mousePressEvent
        self.view.mouseMoveEvent = self.visualizador_grafo.mouseMoveEvent
        self.view.mouseReleaseEvent = self.visualizador_grafo.mouseReleaseEvent
        self.view.keyPressEvent = self.visualizador_grafo.keyPressEvent

        # Resto do seu __init__ (menu, toolbar, etc.)
        self.criar_menu()
        self.criar_toolbar()
        self.configurar_ui()

        # Conectar sinal para atualizar a interface quando o grafo mudar
        self.visualizador_grafo.grafoAlterado.connect(self.atualizar_interface)

    def criar_menu(self):
        menu_bar = self.menuBar()

        # Menu Arquivo
        menu_arquivo = menu_bar.addMenu("Arquivo")
        acao_sair = menu_arquivo.addAction("Sair")
        acao_sair.triggered.connect(self.close)

        # Menu Grafo
        menu_grafo = menu_bar.addMenu("Grafo")
        acao_limpar = menu_grafo.addAction("Limpar Grafo")
        acao_limpar.triggered.connect(self.limpar_grafo)
        acao_mostrar_matriz = menu_grafo.addAction("Mostrar Matriz de Adjacência")
        acao_mostrar_matriz.triggered.connect(self.visualizador_grafo.mostrar_matriz_adjacencia)
        acao_mostrar_lista = menu_grafo.addAction("Mostrar Lista de Adjacência")
        acao_mostrar_lista.triggered.connect(self.visualizador_grafo.mostrar_lista_adjacencia)

        # Menu Algoritmos
        menu_algoritmos = menu_bar.addMenu("Algoritmos")
        acao_todas_rotas = menu_algoritmos.addAction("Todas as Rotas")
        acao_todas_rotas.triggered.connect(self.encontrar_todas_rotas)
        acao_caminho_curto = menu_algoritmos.addAction("Caminho Mais Curto")
        acao_caminho_curto.triggered.connect(self.encontrar_caminho_mais_curto)
        acao_caminho_longo = menu_algoritmos.addAction("Caminho Mais Longo Seguro")
        acao_caminho_longo.triggered.connect(self.encontrar_caminho_mais_longo_seguro)

    def criar_toolbar(self):
        toolbar = self.addToolBar("Ferramentas")

        # Ação para adicionar nó
        acao_adicionar_no = QAction(QIcon(":/icons/node.png"), "Adicionar Nó", self)
        acao_adicionar_no.triggered.connect(self.adicionar_no)
        toolbar.addAction(acao_adicionar_no)

        # Ação para adicionar aresta
        acao_adicionar_aresta = QAction(QIcon(":/icons/edge.png"), "Adicionar Aresta", self)
        acao_adicionar_aresta.triggered.connect(self.preparar_adicao_aresta)
        toolbar.addAction(acao_adicionar_aresta)

        # Ação para deletar (agora com a tecla DELETE no mousePressEvent)
        # acao_deletar = QAction(QIcon(":/icons/delete.png"), "Deletar", self)
        # acao_deletar.triggered.connect(self.deletar_selecionado) # Este método precisaria ser adaptado
        # toolbar.addAction(acao_deletar)

    def configurar_ui(self):
        # A cena já está configurada no __init__
        pass

    def adicionar_no(self):
        rotulo, ok = QInputDialog.getText(self, "Adicionar Nó", "Entre com o rótulo do nó:")
        if ok and rotulo:
            if rotulo in self.visualizador_grafo.nos:
                QMessageBox.warning(self, "Nó Existente", f"Um nó com o rótulo '{rotulo}' já existe.")
                return
            # Posição inicial para o novo nó (centralizado na vista)
            # Converte as coordenadas do centro da vista para coordenadas da cena
            centro_view = self.view.mapToScene(self.view.viewport().rect().center())
            self.visualizador_grafo.adicionar_no(rotulo, centro_view.x(), centro_view.y())
            self.atualizar_interface()

    def preparar_adicao_aresta(self):
        self.visualizador_grafo.modo_adicao_aresta = True
        QMessageBox.information(self, "Adicionar Aresta",
                                "Clique em dois nós para criar uma aresta. O primeiro nó será a origem.")
        self.visualizador_grafo.limpar_selecao_no()  # Limpa qualquer seleção existente

    def limpar_grafo(self):
        resposta = QMessageBox.question(self, "Limpar Grafo", "Tem certeza que deseja limpar todo o grafo?",
                                        QMessageBox.Yes | QMessageBox.No)
        if resposta == QMessageBox.Yes:
            # Iterar sobre uma cópia para evitar problemas de modificação durante a iteração
            for rotulo in list(self.visualizador_grafo.nos.keys()):
                self.visualizador_grafo.deletar_no(self.visualizador_grafo.nos[rotulo])
            self.atualizar_interface()

    def encontrar_todas_rotas(self):
        rotulos_nos = list(self.visualizador_grafo.nos.keys())
        if len(rotulos_nos) < 2:
            QMessageBox.information(self, "Erro", "São necessários pelo menos dois nós para encontrar rotas.")
            return

        origem, ok_origem = QInputDialog.getItem(self, "Origem", "Selecione o nó de origem:", rotulos_nos, 0, False)
        if not ok_origem: return

        destino, ok_destino = QInputDialog.getItem(self, "Destino", "Selecione o nó de destino:", rotulos_nos, 0, False)
        if not ok_destino: return

        if origem == destino:
            QMessageBox.warning(self, "Erro", "Origem e destino não podem ser o mesmo nó para esta operação.")
            return

        # Construir o grafo NetworkX a partir do seu VisualizadorGrafo
        matriz_adj = self._obter_matriz_adjacencia_para_nx()
        grafo_nx = construir_grafo_nx_da_matriz(matriz_adj, rotulos_nos)

        todas_rotas = obter_todas_rotas(grafo_nx, origem, destino)
        if todas_rotas:
            rotas_str = "Rotas encontradas:\n"
            for rota in todas_rotas:
                rotas_str += " -> ".join(rota) + "\n"
            QMessageBox.information(self, "Todas as Rotas", rotas_str)
        else:
            QMessageBox.information(self, "Todas as Rotas", f"Nenhuma rota encontrada de {origem} para {destino}.")

    def encontrar_caminho_mais_curto(self):
        rotulos_nos = list(self.visualizador_grafo.nos.keys())
        if len(rotulos_nos) < 2:
            QMessageBox.information(self, "Erro",
                                    "São necessários pelo menos dois nós para encontrar o caminho mais curto.")
            return

        origem, ok_origem = QInputDialog.getItem(self, "Origem", "Selecione o nó de origem:", rotulos_nos, 0, False)
        if not ok_origem: return

        destino, ok_destino = QInputDialog.getItem(self, "Destino", "Selecione o nó de destino:", rotulos_nos, 0, False)
        if not ok_destino: return

        if origem == destino:
            QMessageBox.warning(self, "Erro", "Origem e destino não podem ser o mesmo nó para esta operação.")
            return

        matriz_adj = self._obter_matriz_adjacencia_para_nx()
        grafo_nx = construir_grafo_nx_da_matriz(matriz_adj, rotulos_nos)

        caminho, peso_total = obter_caminho_mais_curto(grafo_nx, origem, destino)
        if caminho:
            QMessageBox.information(self, "Caminho Mais Curto",
                                    f"Caminho: {' -> '.join(caminho)}\nPeso Total: {peso_total}")
        else:
            QMessageBox.information(self, "Caminho Mais Curto",
                                    f"Nenhum caminho encontrado de {origem} para {destino}.")

    def encontrar_caminho_mais_longo_seguro(self):
        rotulos_nos = list(self.visualizador_grafo.nos.keys())
        if len(rotulos_nos) < 2:
            QMessageBox.information(self, "Erro",
                                    "São necessários pelo menos dois nós para encontrar o caminho mais longo.")
            return

        origem, ok_origem = QInputDialog.getItem(self, "Origem", "Selecione o nó de origem:", rotulos_nos, 0, False)
        if not ok_origem: return

        destino, ok_destino = QInputDialog.getItem(self, "Destino", "Selecione o nó de destino:", rotulos_nos, 0, False)
        if not ok_destino: return

        if origem == destino:
            QMessageBox.warning(self, "Erro", "Origem e destino não podem ser o mesmo nó para esta operação.")
            return

        matriz_adj = self._obter_matriz_adjacencia_para_nx()
        grafo_nx = construir_grafo_nx_da_matriz(matriz_adj, rotulos_nos)

        caminho, peso_total = obter_caminho_mais_longo_seguro(grafo_nx, origem, destino)
        if caminho:
            QMessageBox.information(self, "Caminho Mais Longo Seguro",
                                    f"Caminho: {' -> '.join(caminho)}\nPeso Total: {peso_total}")
        else:
            QMessageBox.information(self, "Caminho Mais Longo Seguro",
                                    f"Nenhum caminho encontrado de {origem} para {destino}.")

    def _obter_matriz_adjacencia_para_nx(self):
        """Retorna a matriz de adjacência e rótulos dos nós na ordem correta para NetworkX."""
        rotulos_ordenados = sorted(self.visualizador_grafo.nos.keys())
        n = len(rotulos_ordenados)
        matriz = [[0] * n for _ in range(n)]

        for aresta in self.visualizador_grafo.arestas:
            try:
                i = rotulos_ordenados.index(aresta.no_origem.rotulo)
                j = rotulos_ordenados.index(aresta.no_destino.rotulo)
                matriz[i][j] = aresta.peso
            except ValueError:
                print(
                    f"Erro ao construir matriz para NX: Nó da aresta {aresta.no_origem.rotulo}->{aresta.no_destino.rotulo} não encontrado.")
        return matriz

    def atualizar_interface(self):
        # Esta função pode ser usada para qualquer atualização visual necessária
        # após alterações no grafo (por exemplo, redesenhar, atualizar status bar, etc.)
        self.view.viewport().update()  # Força o redesenho da view
        # print("Grafo Alterado! Interface atualizada.") # Para depuração
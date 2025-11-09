import networkx as nx


def construir_grafo_nx_da_matriz(matriz_adjacencia, rotulos_nos):
    """
    Constrói um grafo NetworkX a partir de uma matriz de adjacência.
    """
    G = nx.DiGraph()
    for i, rotulo in enumerate(rotulos_nos):
        G.add_node(rotulo)

    for i in range(len(rotulos_nos)):
        for j in range(len(rotulos_nos)):
            peso = matriz_adjacencia[i][j]
            if peso != 0:  # Assume 0 significa nenhuma aresta
                G.add_edge(rotulos_nos[i], rotulos_nos[j], weight=peso)
    return G


def obter_todas_rotas(grafo_nx, inicio, fim):
    """
    Retorna todas as rotas entre dois nós em um grafo NetworkX.
    """
    if inicio not in grafo_nx or fim not in grafo_nx:
        return []
    try:
        return list(nx.all_simple_paths(grafo_nx, source=inicio, target=fim))
    except nx.NetworkXNoPath:
        return []


def obter_caminho_mais_curto(grafo_nx, inicio, fim):
    """
    Retorna o caminho mais curto entre dois nós em um grafo NetworkX.
    """
    if inicio not in grafo_nx or fim not in grafo_nx:
        return None, None
    try:
        caminho = nx.shortest_path(grafo_nx, source=inicio, target=fim, weight='weight')
        custo = nx.shortest_path_length(grafo_nx, source=inicio, target=fim, weight='weight')
        return caminho, custo
    except nx.NetworkXNoPath:
        return None, None


def obter_caminho_mais_longo_seguro(grafo_nx, inicio, fim):
    """
    Retorna o caminho mais longo entre dois nós em um grafo NetworkX (pode ser complexo para grafos com ciclos).
    Para grafos acíclicos (DAGs), pode-se usar algoritmos de caminho crítico.
    Para grafos gerais, isso é NP-difícil. Esta é uma implementação simplificada ou placeholder.
    """
    if inicio not in grafo_nx or fim not in grafo_nx:
        return None, None

    # Exemplo simples para caminhos sem ciclos. Para caminhos mais longos em grafos gerais,
    # uma heurística ou algoritmo mais complexo seria necessário.
    longest_path = None
    longest_cost = -1

    for path in nx.all_simple_paths(grafo_nx, source=inicio, target=fim):
        current_cost = sum(grafo_nx[u][v]['weight'] for u, v in zip(path[:-1], path[1:]))
        if current_cost > longest_cost:
            longest_cost = current_cost
            longest_path = path

    return longest_path, longest_cost
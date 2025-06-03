class Node:
    def __init__(self, posicao, parente=None):
        self.posicao = posicao
        self.parente = parente
        self.g = 0  # Custo do caminho do início até este nó
        self.h = 0  # Heurística (estimativa do custo até o objetivo)
        self.f = 0  # Custo total (g + h)
        self.tem_fruta = False

    def __eq__(self, other):
        return self.posicao == other.posicao

    def __lt__(self, other):
        return self.f < other.f

    def __hash__(self):
        return hash((self.posicao, self.tem_fruta))

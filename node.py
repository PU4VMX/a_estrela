class Node:
    def __init__(self, position, parent=None):
        self.position = position
        self.parent = parent
        self.g = 0  # Custo do caminho do início até este nó
        self.h = 0  # Heurística (estimativa do custo até o objetivo)
        self.f = 0  # Custo total (g + h)
        self.has_fruta = False

    def __eq__(self, other):
        return self.position == other.position

    def __lt__(self, other):
        return self.f < other.f

    def __hash__(self):
        return hash((self.position, self.has_fruta))

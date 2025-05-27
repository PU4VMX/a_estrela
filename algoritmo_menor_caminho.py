import pygame
import heapq
import os
import sys

# Inicialização do Pygame
pygame.init()

# Configurações da tela
CELL_SIZE = 80
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 580
INFO_PANEL_HEIGHT = 100

# Cores para fallback
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
SKY_BLUE = (135, 206, 235)
MAGENTA = (255, 0, 255)  # Para assets faltantes


class AssetLoader:
    def __init__(self):
        self.assets = {}
        self.load_assets()

    def load_assets(self):
        """Carrega todos os assets gráficos"""
        assets_path = os.path.join(os.path.dirname(__file__), "assets")

        # Cria a pasta assets se não existir
        if not os.path.exists(assets_path):
            os.makedirs(assets_path)
            print(
                f"Pasta 'assets' criada em {assets_path}. Adicione seus arquivos PNG lá."
            )

        # Carrega cada asset individualmente
        self.assets["tux"] = [
            self.load_image("tux.png", assets_path),
            self.load_image("tux2.png", assets_path),
        ]
        self.assets["barreira"] = self.load_image("barreira.png", assets_path)
        self.assets["chegada"] = self.load_image("chegada.png", assets_path)
        self.assets["fruta"] = self.load_image("fruta.png", assets_path)
        self.assets["ponte"] = self.load_image("ponte.png", assets_path)
        self.assets["wallpaper"] = self.load_image(
            "wallpaper.png", assets_path, (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        self.assets["vazio"] = self.load_image("vazio.png", assets_path)

    def load_image(self, filename, assets_path, size=(CELL_SIZE, CELL_SIZE)):
        """
        Carrega uma imagem do disco e a redimensiona
        Retorna uma surface pygame com fallback se o arquivo não existir
        """
        try:
            path = os.path.join(assets_path, filename)
            if not os.path.exists(path):
                raise FileNotFoundError(f"Arquivo {filename} não encontrado")

            image = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(image, size)
        except Exception as e:
            print(f"Erro ao carregar {filename}: {e}")
            return self.create_fallback_surface(filename, size)

    def create_fallback_surface(self, filename, size):
        """Cria uma surface de fallback quando um asset não é encontrado"""
        surface = pygame.Surface(size)
        surface.fill(MAGENTA)  # Cor destacada para indicar asset faltante

        # Adiciona o nome do arquivo faltante
        font = pygame.font.SysFont("Arial", 12)
        text = font.render(filename.split(".")[0], True, BLACK)
        text_rect = text.get_rect(center=(size[0] // 2, size[1] // 2))
        surface.blit(text, text_rect)

        return surface


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


class TuxGame:
    def __init__(self, grid):
        self.original_grid = [row.copy() for row in grid]  # Salva o mapa original
        self.grid = [row.copy() for row in self.original_grid]

        self.rows = len(grid)
        self.cols = len(grid[0]) if self.rows > 0 else 0

        # ⚠️ Configure a tela primeiro
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tux Pathfinder - A* Algorithm")

        # ✅ Só depois carregue os assets
        self.asset_loader = AssetLoader()

        # Configuração da janela
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tux Pathfinder - A* Algorithm")

        # Fonte para UI
        self.font = pygame.font.SysFont("Arial", 16)
        self.big_font = pygame.font.SysFont("Arial", 24)

        # Estado do jogo
        self.reset_game()

        # Configuração da câmera
        self.camera_x = 0
        self.camera_y = 0

        # Animação
        self.animation_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.animation_delay = 200  # ms entre frames de animação

        # Controle automático
        self.auto_step_delay = 300  # ms entre passos do algoritmo
        self.last_step_time = pygame.time.get_ticks()

    def reset_game(self):
        """Reinicia o estado do jogo para o início"""
        self.grid = [row.copy() for row in self.original_grid] 
        self.start, self.end = self.find_character_and_exit()
        self.path = []
        self.visited = []
        self.current_node = None
        self.open_list = []
        self.closed_list = set()
        self.fruta_acquired = False
        self.animation_path = []
        self.animation_index = 0
        self.state = "searching"  # Estados: "searching", "showing_path", "animating"
        
        # Novos atributos para visualização do processo
        self.open_positions = set()  # Posições na lista aberta
        self.closed_positions = set()  # Posições na lista fechada
        self.current_neighbors = []  # Vizinhos sendo avaliados no momento
        self.evaluation_step = 0  # Passo atual da avaliação
        self.node_costs = {}  # Dicionário para armazenar custos dos nós

        # Inicializa a lista aberta com o nó inicial
        start_node = Node(self.start)
        start_node.g = 0
        start_node.h = self.heuristic(self.start, self.end)
        start_node.f = start_node.g + start_node.h
        heapq.heappush(self.open_list, start_node)
        self.open_positions.add(self.start)
        self.node_costs[self.start] = {'g': start_node.g, 'h': start_node.h, 'f': start_node.f}

    def find_character_and_exit(self):
        """Localiza as posições inicial (C) e final (S) no grid"""
        start = end = None
        for i in range(self.rows):
            for j in range(self.cols):
                if self.grid[i][j] == "C":
                    start = (i, j)
                elif self.grid[i][j] == "S":
                    end = (i, j)

        if start is None or end is None:
            raise ValueError(
                "Mapa inválido: 'C' (início) ou 'S' (fim) não encontrados no grid."
            )

        return start, end

    def heuristic(self, a, b):
        """Distância de Manhattan entre dois pontos"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def a_star_step(self):
        """Executa um passo do algoritmo A*"""
        if not self.open_list and not self.path and self.state == "searching":
            return False  # Nenhum caminho encontrado

        current_time = pygame.time.get_ticks()

        # Fase de busca com visualização em tempo real
        if self.open_list and self.state == "searching":
            # Diminui a velocidade para melhor visualização
            if current_time - self.last_step_time < 1200:  # 1200ms entre passos
                return True
                
            current_node = heapq.heappop(self.open_list)
            self.current_node = current_node
            
            # Remove da lista aberta e adiciona à fechada
            self.open_positions.discard(current_node.position)
            self.closed_list.add((current_node.position, current_node.has_fruta))
            self.closed_positions.add(current_node.position)
            self.visited.append(current_node.position)

            # Verifica se chegamos ao objetivo
            if current_node.position == self.end:
                self.reconstruct_path(current_node)
                self.state = "showing_path"
                self.last_step_time = current_time
                return True

            # Explora os vizinhos e mostra o processo
            self.explore_neighbors_visual(current_node)
            self.last_step_time = current_time
            return True

        # Fase de exibição do caminho encontrado
        elif self.state == "showing_path" and current_time - self.last_step_time > 2000:
            self.state = "animating"
            self.animation_path = self.path.copy()
            self.animation_index = 0
            self.last_step_time = current_time
            return True

        # Fase de animação do movimento
        elif self.state == "animating":
            if current_time - self.last_step_time > self.auto_step_delay:
                if self.animation_index < len(self.animation_path) - 1:
                    self.animation_index += 1
                    self.last_step_time = current_time
                    self.update_character_position()
                    return True
                elif (
                    current_time - self.last_step_time > 3000
                ):  # Espera 3s após terminar
                    self.reset_game()
                    return True

        return False

    def reconstruct_path(self, node):
        """Reconstrói o caminho do final até o início"""
        path = []
        current = node
        while current is not None:
            path.append(current.position)
            current = current.parent
        self.path = path[::-1]

    def explore_neighbors_visual(self, current_node):
        """Explora todos os vizinhos do nó atual com visualização"""
        movements = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Cima, baixo, esquerda, direita
        self.current_neighbors = []

        for movement in movements:
            neighbor_pos = (
                current_node.position[0] + movement[0],
                current_node.position[1] + movement[1],
            )

            # Verifica se está dentro dos limites do grid
            if not (
                0 <= neighbor_pos[0] < self.rows and 0 <= neighbor_pos[1] < self.cols
            ):
                continue

            # Verifica se é uma barreira e se não tem a fruta mágica
            cell_value = self.grid[neighbor_pos[0]][neighbor_pos[1]]
            if cell_value == "B" and not current_node.has_fruta:
                continue

            # Cria o novo nó
            neighbor_node = Node(neighbor_pos, current_node)
            neighbor_node.has_fruta = current_node.has_fruta

            # Verifica se é uma fruta mágica
            if cell_value == "F":
                neighbor_node.has_fruta = True

            # Ignora se já estiver na lista fechada
            if (neighbor_node.position, neighbor_node.has_fruta) in self.closed_list:
                continue

            # Calcula os custos
            neighbor_node.g = current_node.g + 1
            if cell_value == "A":  # Semi-barreira tem custo extra
                neighbor_node.g += 1

            neighbor_node.h = self.heuristic(neighbor_node.position, self.end)
            neighbor_node.f = neighbor_node.g + neighbor_node.h

            # Armazena os custos para visualização
            self.node_costs[neighbor_pos] = {
                'g': neighbor_node.g, 
                'h': neighbor_node.h, 
                'f': neighbor_node.f
            }

            # Adiciona aos vizinhos sendo avaliados
            self.current_neighbors.append(neighbor_pos)

            # Adiciona à lista aberta se não estiver lá ou se tiver um custo menor
            if not any(
                open_node.position == neighbor_node.position
                and open_node.has_fruta == neighbor_node.has_fruta
                and open_node.f <= neighbor_node.f
                for open_node in self.open_list
            ):
                heapq.heappush(self.open_list, neighbor_node)
                self.open_positions.add(neighbor_pos)

    def explore_neighbors(self, current_node):
        """Explora todos os vizinhos do nó atual"""
        movements = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Cima, baixo, esquerda, direita

        for movement in movements:
            neighbor_pos = (
                current_node.position[0] + movement[0],
                current_node.position[1] + movement[1],
            )

            # Verifica se está dentro dos limites do grid
            if not (
                0 <= neighbor_pos[0] < self.rows and 0 <= neighbor_pos[1] < self.cols
            ):
                continue

            # Verifica se é uma barreira e se não tem a fruta mágica
            cell_value = self.grid[neighbor_pos[0]][neighbor_pos[1]]
            if cell_value == "B" and not current_node.has_fruta:
                continue

            # Cria o novo nó
            neighbor_node = Node(neighbor_pos, current_node)
            neighbor_node.has_fruta = current_node.has_fruta

            # Verifica se é uma fruta mágica
            if cell_value == "F":
                neighbor_node.has_fruta = True

            # Ignora se já estiver na lista fechada
            if (neighbor_node.position, neighbor_node.has_fruta) in self.closed_list:
                continue

            # Calcula os custos
            neighbor_node.g = current_node.g + 1
            if cell_value == "A":  # Semi-barreira tem custo extra
                neighbor_node.g += 1

            neighbor_node.h = self.heuristic(neighbor_node.position, self.end)
            neighbor_node.f = neighbor_node.g + neighbor_node.h

            # Adiciona à lista aberta se não estiver lá ou se tiver um custo menor
            if not any(
                open_node.position == neighbor_node.position
                and open_node.has_fruta == neighbor_node.has_fruta
                and open_node.f <= neighbor_node.f
                for open_node in self.open_list
            ):
                heapq.heappush(self.open_list, neighbor_node)

    def update_character_position(self):
        """Atualiza a posição do personagem no grid durante a animação"""
        if self.animation_index > 0:
            old_pos = self.animation_path[self.animation_index - 1]
            new_pos = self.animation_path[self.animation_index]
            self.grid[old_pos[0]][old_pos[1]] = "_"
            self.grid[new_pos[0]][new_pos[1]] = "C"
            self.start = new_pos

    def update_camera(self):
        """Atualiza a posição da câmera para seguir o personagem"""
        if self.state == "animating" and self.animation_path:
            target_x = (
                self.animation_path[self.animation_index][1] * CELL_SIZE
                - SCREEN_WIDTH // 2
            )
            target_y = (
                self.animation_path[self.animation_index][0] * CELL_SIZE
                - SCREEN_HEIGHT // 2
            )

            # Suaviza o movimento da câmera
            self.camera_x += (target_x - self.camera_x) * 0.1
            self.camera_y += (target_y - self.camera_y) * 0.1

            # Limita aos limites do mapa
            max_x = max(0, self.cols * CELL_SIZE - SCREEN_WIDTH)
            max_y = max(0, self.rows * CELL_SIZE - (SCREEN_HEIGHT - INFO_PANEL_HEIGHT))

            self.camera_x = max(0, min(self.camera_x, max_x))
            self.camera_y = max(0, min(self.camera_y, max_y))

    def draw(self):
        """Renderiza todo o jogo"""
        # Desenha o fundo
        self.screen.blit(self.asset_loader.assets["wallpaper"], (0, 0))

        # Atualiza a animação do personagem
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update > self.animation_delay:
            self.animation_frame = (self.animation_frame + 1) % 2
            self.last_update = current_time

        # Desenha o grid com offset da câmera
        for row in range(self.rows):
            for col in range(self.cols):
                self.draw_cell(row, col)

        # Desenha o painel de informações
        self.draw_info_panel()

    def draw_cell(self, row, col):
        """Desenha uma célula individual do grid"""
        screen_x = col * CELL_SIZE - self.camera_x
        screen_y = row * CELL_SIZE - self.camera_y

        # Verifica se a célula está visível na tela
        if not (
            -CELL_SIZE <= screen_x <= SCREEN_WIDTH
            and -CELL_SIZE <= screen_y <= SCREEN_HEIGHT - INFO_PANEL_HEIGHT
        ):
            return

        # Desenha o tile de fundo
        self.screen.blit(self.asset_loader.assets["vazio"], (screen_x, screen_y))

        # Visualização do processo de busca A*
        position = (row, col)
        
        # Destaca posições na lista fechada (já avaliadas)
        if position in self.closed_positions and self.state == "searching":
            highlight = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            highlight.fill((255, 0, 0, 100))  # Vermelho semi-transparente
            self.screen.blit(highlight, (screen_x, screen_y))
        
        # Destaca posições na lista aberta (candidatas)
        elif position in self.open_positions and self.state == "searching":
            highlight = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            highlight.fill((0, 255, 0, 100))  # Verde semi-transparente
            self.screen.blit(highlight, (screen_x, screen_y))
        
        # Destaca vizinhos sendo avaliados no momento
        if position in self.current_neighbors and self.state == "searching":
            highlight = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            highlight.fill((255, 255, 0, 150))  # Amarelo mais opaco
            self.screen.blit(highlight, (screen_x, screen_y))
        
        # Destaca o nó atual sendo processado
        if (self.current_node and position == self.current_node.position and 
            self.state == "searching"):
            highlight = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            highlight.fill((0, 0, 255, 150))  # Azul mais opaco
            self.screen.blit(highlight, (screen_x, screen_y))

        # Desenha os elementos do jogo
        cell_value = self.grid[row][col]

        if cell_value == "B":
            self.screen.blit(self.asset_loader.assets["barreira"], (screen_x, screen_y))
        elif cell_value == "A":
            self.screen.blit(self.asset_loader.assets["ponte"], (screen_x, screen_y))
        elif cell_value == "F":
            self.screen.blit(self.asset_loader.assets["fruta"], (screen_x, screen_y))
        elif cell_value == "S":
            self.screen.blit(self.asset_loader.assets["chegada"], (screen_x, screen_y))
        elif cell_value == "C":
            # Animação de caminhada
            tux_sprite = self.asset_loader.assets["tux"][self.animation_frame]
            self.screen.blit(tux_sprite, (screen_x, screen_y))

        # Mostra custos calculados em tempo real
        if position in self.node_costs and self.state == "searching":
            costs = self.node_costs[position]
            font_small = pygame.font.SysFont("Arial", 10)
            
            # Mostra G (custo do caminho)
            g_text = font_small.render(f"G:{costs['g']}", True, BLACK)
            self.screen.blit(g_text, (screen_x + 2, screen_y + 2))
            
            # Mostra H (heurística)
            h_text = font_small.render(f"H:{costs['h']}", True, BLACK)
            self.screen.blit(h_text, (screen_x + 2, screen_y + 15))
            
            # Mostra F (total)
            f_text = font_small.render(f"F:{costs['f']}", True, BLACK)
            self.screen.blit(f_text, (screen_x + 2, screen_y + 28))

        # Destaca o caminho encontrado
        if (row, col) in self.path and self.state in ["showing_path", "animating"]:
            highlight = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            highlight.fill((0, 0, 255, 128))
            self.screen.blit(highlight, (screen_x, screen_y))

    def draw_info_panel(self):
        """Desenha o painel de informações na parte inferior da tela"""
        panel_rect = pygame.Rect(
            0, SCREEN_HEIGHT - INFO_PANEL_HEIGHT, SCREEN_WIDTH, INFO_PANEL_HEIGHT
        )
        pygame.draw.rect(self.screen, GRAY, panel_rect)
        pygame.draw.rect(self.screen, BLACK, panel_rect, 2)

        # Status do jogo
        if self.state == "searching":
            status_text = f"Buscando... Nós: Abertos({len(self.open_positions)}) | Fechados({len(self.closed_positions)})"
            if self.current_node:
                current_pos = self.current_node.position
                status_text += f" | Atual: ({current_pos[0]},{current_pos[1]})"
        elif self.state == "showing_path":
            status_text = f"Caminho encontrado! Custo total: {len(self.path) - 1} passos"
        elif self.state == "animating":
            status_text = f"Executando caminho... Passo {self.animation_index + 1}/{len(self.animation_path)}"
        else:
            status_text = "Preparando..."

        text_surface = self.font.render(status_text, True, BLACK)
        self.screen.blit(text_surface, (10, SCREEN_HEIGHT - INFO_PANEL_HEIGHT + 10))

        # Legenda das cores
        legend_y = SCREEN_HEIGHT - INFO_PANEL_HEIGHT + 35
        legend_items = [
            (BLUE, "Atual"),
            (GREEN, "Aberto"),
            (RED, "Fechado"), 
            (YELLOW, "Vizinhos")
        ]
        
        x_offset = 10
        for color, label in legend_items:
            # Desenha quadrado colorido
            pygame.draw.rect(self.screen, color, (x_offset, legend_y, 15, 15))
            pygame.draw.rect(self.screen, BLACK, (x_offset, legend_y, 15, 15), 1)
            
            # Desenha texto
            label_surface = self.font.render(label, True, BLACK)
            self.screen.blit(label_surface, (x_offset + 20, legend_y))
            x_offset += 80

        # Instruções
        instr_text = "R: Reiniciar | ESC: Sair"
        instr_surface = self.font.render(instr_text, True, BLACK)
        self.screen.blit(instr_surface, (10, SCREEN_HEIGHT - INFO_PANEL_HEIGHT + 60))

    def run(self):
        """Loop principal do jogo"""
        clock = pygame.time.Clock()
        running = True

        while running:
            # Processa eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        running = False

            # Atualiza a lógica do jogo
            self.a_star_step()
            self.update_camera()

            # Renderiza tudo
            self.draw()
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()


def create_default_map():
    """Cria um mapa de exemplo mais complexo para demonstrar melhor o algoritmo A*"""
    return [
        ["C", "_", "_", "_", "B", "_"],
        ["_", "B", "_", "_", "_", "_"],
        ["_", "_", "F", "_", "_", "_"],
        ["_", "_", "_", "B", "B", "_"],
        ["_", "_", "_", "A", "_", "_"],
        ["_", "_", "_", "_", "_", "S"],
    ]


if __name__ == "__main__":
    # Verifica se a pasta assets existe
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
        print(f"Diretório 'assets' criado em {assets_dir}")
        print("Por favor, adicione seus arquivos PNG lá:")
        print("- tux.png, tux2.png (personagem)")
        print("- barreira.png (barreiras)")
        print("- chegada.png (saída)")
        print("- fruta.png (fruta mágica)")
        print("- ponte.png (semi-barreiras)")
        print("- wallpaper.png (fundo)")
        print("- vazio.png (espaço vazio)")

    # Inicia o jogo
    game_map = create_default_map()
    game = TuxGame(game_map)
    game.run()

import os

import pygame

from constantes import BLACK, CELL_SIZE, MAGENTA, SCREEN_HEIGHT, SCREEN_WIDTH


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
            self.load_image("walk-0.png", assets_path),
            self.load_image("walk_transition-0.png", assets_path),
            self.load_image("walk-1.png", assets_path),
            self.load_image("walk_transition-0.png", assets_path),
            self.load_image("walk-2.png", assets_path),
            self.load_image("walk_transition-0.png", assets_path),
            self.load_image("walk-3.png", assets_path),
            self.load_image("walk_transition-0.png", assets_path),
            self.load_image("walk-4.png", assets_path),
            self.load_image("walk_transition-0.png", assets_path),
            self.load_image("walk-5.png", assets_path),
            self.load_image("walk_transition-0.png", assets_path),
            self.load_image("walk-6.png", assets_path),
            self.load_image("walk_transition-0.png", assets_path),
            self.load_image("walk-7.png", assets_path),
            self.load_image("walk_transition-0.png", assets_path),
        ]
        self.assets["barreira"] =[ 
            self.load_image("attacking-0.png", assets_path),
            self.load_image("charging-0.png", assets_path),
            ]
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

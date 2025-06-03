import os

import pygame

from constantes import (
    PRETO,
    TAMANHO_CELULA,
    ALTURA_TELA,
    LARGURA_TELA,
    MAGENTA,
)


class CarregadorElementos:
    def __init__(self):
        self.elementos = {}
        self.carregar_elementos()

    def carregar_elementos(self):
        """Carrega todos os elementos gráficos"""
        elementos_path = os.path.join(os.path.dirname(__file__), "elementos")

        # Cria a pasta elementos se não existir
        if not os.path.exists(elementos_path):
            os.makedirs(elementos_path)
            print(
                f"Pasta 'elementos' criada em {elementos_path}. Adicione seus arquivos PNG lá."
            )

        # Carrega cada asset individualmente
        self.elementos["tux"] = [
            self.load_image("walk-0.png", elementos_path),
            self.load_image("walk_transition-0.png", elementos_path),
            self.load_image("walk-1.png", elementos_path),
            self.load_image("walk_transition-0.png", elementos_path),
            self.load_image("walk-2.png", elementos_path),
            self.load_image("walk_transition-0.png", elementos_path),
            self.load_image("walk-3.png", elementos_path),
            self.load_image("walk_transition-0.png", elementos_path),
            self.load_image("walk-4.png", elementos_path),
            self.load_image("walk_transition-0.png", elementos_path),
            self.load_image("walk-5.png", elementos_path),
            self.load_image("walk_transition-0.png", elementos_path),
            self.load_image("walk-6.png", elementos_path),
            self.load_image("walk_transition-0.png", elementos_path),
            self.load_image("walk-7.png", elementos_path),
            self.load_image("walk_transition-0.png", elementos_path),
        ]
        self.elementos["barreira"] = [
            self.load_image("attacking-0.png", elementos_path),
            self.load_image("charging-0.png", elementos_path),
        ]
        self.elementos["chegada"] = self.load_image("chegada.png", elementos_path)
        self.elementos["fruta"] = self.load_image("fruta.png", elementos_path)
        self.elementos["ponte"] = self.load_image("ponte.png", elementos_path)
        self.elementos["wallpaper"] = self.load_image(
            "wallpaper.png", elementos_path, (LARGURA_TELA, ALTURA_TELA)
        )
        self.elementos["vazio"] = self.load_image("vazio.png", elementos_path)

    def load_image(
        self, filename, elementos_path, size=(TAMANHO_CELULA, TAMANHO_CELULA)
    ):
        """
        Carrega uma imagem do disco e a redimensiona
        Retorna uma surface pygame com fallback se o arquivo não existir
        """
        try:
            path = os.path.join(elementos_path, filename)
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
        text = font.render(filename.split(".")[0], True, PRETO)
        text_rect = text.get_rect(center=(size[0] // 2, size[1] // 2))
        surface.blit(text, text_rect)

        return surface

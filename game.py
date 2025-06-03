import pygame
import heapq


from constantes import (
    PRETO,
    AZUL,
    TAMANHO_CELULA,
    CINZA,
    VERDE,
    ALTURA_PAINEL_INFO,
    VERMELHO,
    ALTURA_TELA,
    LARGURA_TELA,
    AMARELO,
)
from interface_grafica import CarregadorElementos
from node import Node

pygame.init()


class JogoTux:
    def __init__(self, grid):
        # Salva o mapa original
        self.grid_original = [linha.copy() for linha in grid]
        self.grid = [linha.copy() for linha in self.grid_original]

        self.linhas = len(grid)
        self.colunas = len(grid[0]) if self.linhas > 0 else 0

        # Configura a tela primeiro
        self.tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
        pygame.display.set_caption("A* Menor Caminho - Tux")
        pygame.display.set_icon(pygame.image.load("elementos/tux.png"))
        pygame.mixer.music.load(
            "elementos/sons_supertux/data/music/retro/fortress_old.ogg"
        )
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

        # Só depois carrega os elementos
        self.carregador_elementos = CarregadorElementos()

        # Configuração da janela
        self.tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))

        pygame.display.set_caption("A* Menor Caminho - Tux")

        # Fonte para UI
        self.fonte = pygame.font.SysFont("Arial", 16)
        self.fonte_grande = pygame.font.SysFont("Arial", 24)

        # Estado do jogo
        self.reiniciar_jogo()

        # Configuração da câmera
        self.camera_x = 0
        self.camera_y = 0

        # Animação
        self.frame_animacao = 0
        self.ultima_atualizacao = pygame.time.get_ticks()
        self.delay_animacao = 200  # ms entre frames de animação

        # Controle automático
        self.delay_passo_auto = 300  # ms entre passos do algoritmo
        self.ultimo_tempo_passo = pygame.time.get_ticks()

    def reiniciar_jogo(self):
        """Reinicia o estado do jogo para o início"""
        self.grid = [linha.copy() for linha in self.grid_original]
        self.inicio, self.fim = self.encontrar_personagem_e_saida()
        self.caminho = []
        self.visitados = []
        self.no_atual = None
        self.lista_aberta = []
        self.lista_fechada = set()
        self.fruta_obtida = False
        self.caminho_animacao = []
        self.indice_animacao = 0
        self.estado = "buscando"  # Estados: "buscando", "mostrando_caminho", "animando"

        # Novos atributos para visualização do processo
        self.posicoes_abertas = set()  # Posições na lista aberta
        self.posicoes_fechadas = set()  # Posições na lista fechada
        self.vizinhos_atuais = []  # Vizinhos sendo avaliados no momento
        self.passo_avaliacao = 0  # Passo atual da avaliação
        self.custos_nos = {}  # Dicionário para armazenar custos dos nós

        # Inicializa a lista aberta com o nó inicial
        no_inicial = Node(self.inicio)
        no_inicial.g = 0
        no_inicial.h = self.heuristica(self.inicio, self.fim)
        no_inicial.f = no_inicial.g + no_inicial.h
        heapq.heappush(self.lista_aberta, no_inicial)
        self.posicoes_abertas.add(self.inicio)
        self.custos_nos[self.inicio] = {
            "g": no_inicial.g,
            "h": no_inicial.h,
            "f": no_inicial.f,
        }

    def encontrar_personagem_e_saida(self):
        """Localiza as posições inicial (C) e final (S) no grid"""
        inicio = fim = None
        for i in range(self.linhas):
            for j in range(self.colunas):
                if self.grid[i][j] == "C":
                    inicio = (i, j)
                elif self.grid[i][j] == "S":
                    fim = (i, j)

        if inicio is None or fim is None:
            raise ValueError(
                "Mapa inválido: 'C' (início) ou 'S' (fim) não encontrados no grid."
            )

        return inicio, fim

    def heuristica(self, a, b):
        """Distância de Manhattan entre dois pontos"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def passo_a_estrela(self):
        """Executa um passo do algoritmo A*"""
        if not self.lista_aberta and not self.caminho and self.estado == "buscando":
            return False  # Nenhum caminho encontrado

        tempo_atual = pygame.time.get_ticks()

        # Fase de busca com visualização em tempo real
        if self.lista_aberta and self.estado == "buscando":
            # Diminui a velocidade para melhor visualização
            if tempo_atual - self.ultimo_tempo_passo < 1200:  # 1200ms entre passos
                return True

            no_atual = heapq.heappop(self.lista_aberta)
            self.no_atual = no_atual

            # Remove da lista aberta e adiciona à fechada
            self.posicoes_abertas.discard(no_atual.posicao)
            self.lista_fechada.add((no_atual.posicao, no_atual.tem_fruta))
            self.posicoes_fechadas.add(no_atual.posicao)
            self.visitados.append(no_atual.posicao)

            # Verifica se chegamos ao objetivo
            if no_atual.posicao == self.fim:
                self.reconstruir_caminho(no_atual)
                self.estado = "mostrando_caminho"
                self.ultimo_tempo_passo = tempo_atual
                return True

            # Explora os vizinhos e mostra o processo
            self.explorar_vizinhos_visual(no_atual)
            self.ultimo_tempo_passo = tempo_atual
            return True

        # Fase de exibição do caminho encontrado
        elif (
            self.estado == "mostrando_caminho"
            and tempo_atual - self.ultimo_tempo_passo > 2000
        ):
            self.estado = "animando"
            self.caminho_animacao = self.caminho.copy()
            self.indice_animacao = 0
            self.ultimo_tempo_passo = tempo_atual
            return True

        # Fase de animação do movimento
        elif self.estado == "animando":
            if tempo_atual - self.ultimo_tempo_passo > self.delay_passo_auto:
                if self.indice_animacao < len(self.caminho_animacao) - 1:
                    self.indice_animacao += 1
                    self.ultimo_tempo_passo = tempo_atual
                    self.atualizar_posicao_personagem()
                    return True
                elif (
                    tempo_atual - self.ultimo_tempo_passo > 3000
                ):  # Espera 3s após terminar
                    self.reiniciar_jogo()
                    return True

        return False

    def reconstruir_caminho(self, node):
        """Reconstrói o caminho do final até o início"""
        caminho = []
        atual = node
        while atual is not None:
            caminho.append(atual.posicao)
            atual = atual.parente
        self.caminho = caminho[::-1]

    def explorar_vizinhos_visual(self, no_atual):
        """Explora todos os vizinhos do nó atual com visualização"""
        movimentos = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
        ]  # Cima, baixo, esquerda, direita
        self.vizinhos_atuais = []

        for movimento in movimentos:
            pos_vizinho = (
                no_atual.posicao[0] + movimento[0],
                no_atual.posicao[1] + movimento[1],
            )

            # Verifica se está dentro dos limites do grid
            if not (
                0 <= pos_vizinho[0] < self.linhas and 0 <= pos_vizinho[1] < self.colunas
            ):
                continue

            # Verifica se é uma barreira e se não tem a fruta mágica
            valor_celula = self.grid[pos_vizinho[0]][pos_vizinho[1]]
            if valor_celula == "B" and not no_atual.tem_fruta:
                continue

            # Cria o novo nó
            no_vizinho = Node(pos_vizinho, no_atual)
            no_vizinho.tem_fruta = no_atual.tem_fruta

            # Verifica se é uma fruta mágica
            if valor_celula == "F":
                no_vizinho.tem_fruta = True

            # Ignora se já estiver na lista fechada
            if (no_vizinho.posicao, no_vizinho.tem_fruta) in self.lista_fechada:
                continue

            # Calcula os custos
            no_vizinho.g = no_atual.g + 1
            if valor_celula == "A":  # Semi-barreira tem custo extra
                no_vizinho.g += 1

            no_vizinho.h = self.heuristica(no_vizinho.posicao, self.fim)
            no_vizinho.f = no_vizinho.g + no_vizinho.h

            # Armazena os custos para visualização
            self.custos_nos[pos_vizinho] = {
                "g": no_vizinho.g,
                "h": no_vizinho.h,
                "f": no_vizinho.f,
            }

            # Adiciona aos vizinhos sendo avaliados
            self.vizinhos_atuais.append(pos_vizinho)

            # Adiciona à lista aberta se não estiver lá ou se tiver um custo menor
            if not any(
                no_aberto.posicao == no_vizinho.posicao
                and no_aberto.tem_fruta == no_vizinho.tem_fruta
                and no_aberto.f <= no_vizinho.f
                for no_aberto in self.lista_aberta
            ):
                heapq.heappush(self.lista_aberta, no_vizinho)
                self.posicoes_abertas.add(pos_vizinho)

    def explorar_vizinhos(self, no_atual):
        """Explora todos os vizinhos do nó atual"""
        movimentos = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
        ]  # Cima, baixo, esquerda, direita

        for movimento in movimentos:
            pos_vizinho = (
                no_atual.posicao[0] + movimento[0],
                no_atual.posicao[1] + movimento[1],
            )

            # Verifica se está dentro dos limites do grid
            if not (
                0 <= pos_vizinho[0] < self.linhas and 0 <= pos_vizinho[1] < self.colunas
            ):
                continue

            # Verifica se é uma barreira e se não tem a fruta mágica
            valor_celula = self.grid[pos_vizinho[0]][pos_vizinho[1]]
            if valor_celula == "B" and not no_atual.tem_fruta:
                continue

            # Cria o novo nó
            no_vizinho = Node(pos_vizinho, no_atual)
            no_vizinho.tem_fruta = no_atual.tem_fruta

            # Verifica se é uma fruta mágica
            if valor_celula == "F":
                no_vizinho.tem_fruta = True

            # Ignora se já estiver na lista fechada
            if (no_vizinho.posicao, no_vizinho.tem_fruta) in self.lista_fechada:
                continue

            # Calcula os custos
            no_vizinho.g = no_atual.g + 1
            if valor_celula == "A":  # Semi-barreira tem custo extra
                no_vizinho.g += 1

            no_vizinho.h = self.heuristica(no_vizinho.posicao, self.fim)
            no_vizinho.f = no_vizinho.g + no_vizinho.h

            # Adiciona à lista aberta se não estiver lá ou se tiver um custo menor
            if not any(
                no_aberto.posicao == no_vizinho.posicao
                and no_aberto.tem_fruta == no_vizinho.tem_fruta
                and no_aberto.f <= no_vizinho.f
                for no_aberto in self.lista_aberta
            ):
                heapq.heappush(self.lista_aberta, no_vizinho)

    def reproduz_som(self, posicao):
        """Reproduz o som correspondente à posição do personagem"""

        switcher = {
            "_": "elementos/sons_supertux/data/sounds/bigjump.wav",
            "F": "elementos/sons_supertux/data/sounds/coin.wav",
            "A": "elementos/sons_supertux/data/sounds/trampoline.wav",
            "B": "elementos/sons_supertux/data/sounds/metal_hit.ogg",
            "S": "elementos/sons_supertux/data/sounds/tada.ogg",
        }
        som = switcher.get(posicao, None)
        if som:
            pygame.mixer.Sound(som).play()

    def atualizar_posicao_personagem(self):
        """Atualiza a posição do personagem no grid durante a animação"""
        if self.indice_animacao > 0:
            pos_antiga = self.caminho_animacao[self.indice_animacao - 1]
            pos_nova = self.caminho_animacao[self.indice_animacao]
            posicao_atual = self.grid[pos_nova[0]][pos_nova[1]]
            self.reproduz_som(posicao_atual)

            self.grid[pos_antiga[0]][pos_antiga[1]] = "_"
            self.grid[pos_nova[0]][pos_nova[1]] = "C"
            self.inicio = pos_nova

    def atualizar_camera(self):
        """Atualiza a posição da câmera para seguir o personagem"""
        if self.estado == "animando" and self.caminho_animacao:
            alvo_x = (
                self.caminho_animacao[self.indice_animacao][1] * TAMANHO_CELULA
                - LARGURA_TELA // 2
            )
            alvo_y = (
                self.caminho_animacao[self.indice_animacao][0] * TAMANHO_CELULA
                - ALTURA_TELA // 2
            )

            # Suaviza o movimento da câmera
            self.camera_x += (alvo_x - self.camera_x) * 0.1
            self.camera_y += (alvo_y - self.camera_y) * 0.1

            # Limita aos limites do mapa
            max_x = max(0, self.colunas * TAMANHO_CELULA - LARGURA_TELA)
            max_y = max(
                0, self.linhas * TAMANHO_CELULA - (ALTURA_TELA - ALTURA_PAINEL_INFO)
            )

            self.camera_x = max(0, min(self.camera_x, max_x))
            self.camera_y = max(0, min(self.camera_y, max_y))

    def desenhar(self):
        """Renderiza todo o jogo"""
        # Desenha o fundo
        self.tela.blit(self.carregador_elementos.elementos["wallpaper"], (0, 0))

        # Atualiza a animação do personagem
        tempo_atual = pygame.time.get_ticks()
        if tempo_atual - self.ultima_atualizacao > self.delay_animacao:
            self.frame_animacao = (self.frame_animacao + 1) % 2
            self.ultima_atualizacao = tempo_atual

        # Desenha o grid com offset da câmera
        for linha in range(self.linhas):
            for coluna in range(self.colunas):
                self.desenhar_celula(linha, coluna)

        # Desenha o painel de informações
        self.desenhar_painel_info()

    def desenhar_celula(self, linha, coluna):
        """Desenha uma célula individual do grid"""
        tela_x = coluna * TAMANHO_CELULA - self.camera_x
        tela_y = linha * TAMANHO_CELULA - self.camera_y

        # Verifica se a célula está visível na tela
        if not (
            -TAMANHO_CELULA <= tela_x <= LARGURA_TELA
            and -TAMANHO_CELULA <= tela_y <= ALTURA_TELA - ALTURA_PAINEL_INFO
        ):
            return

        # Desenha o tile de fundo
        self.tela.blit(self.carregador_elementos.elementos["vazio"], (tela_x, tela_y))

        # Visualização do processo de busca A*
        posicao = (linha, coluna)

        # Destaca posições na lista fechada (já avaliadas)
        if posicao in self.posicoes_fechadas and self.estado == "buscando":
            destaque = pygame.Surface((TAMANHO_CELULA, TAMANHO_CELULA), pygame.SRCALPHA)
            destaque.fill((255, 0, 0, 100))  # Vermelho semi-transparentee
            self.tela.blit(destaque, (tela_x, tela_y))

        # Destaca posições na lista aberta (candidatas)
        elif posicao in self.posicoes_abertas and self.estado == "buscando":
            destaque = pygame.Surface((TAMANHO_CELULA, TAMANHO_CELULA), pygame.SRCALPHA)
            destaque.fill((0, 255, 0, 100))  # Verde semi-transparentee
            self.tela.blit(destaque, (tela_x, tela_y))

        # Destaca vizinhos sendo avaliados no momento
        if posicao in self.vizinhos_atuais and self.estado == "buscando":
            destaque = pygame.Surface((TAMANHO_CELULA, TAMANHO_CELULA), pygame.SRCALPHA)
            destaque.fill((255, 255, 0, 150))  # Amarelo mais opaco
            self.tela.blit(destaque, (tela_x, tela_y))

        # Destaca o nó atual sendo processado
        if (
            self.no_atual
            and posicao == self.no_atual.posicao
            and self.estado == "buscando"
        ):
            destaque = pygame.Surface((TAMANHO_CELULA, TAMANHO_CELULA), pygame.SRCALPHA)
            destaque.fill((0, 0, 255, 150))  # Azul mais opaco
            self.tela.blit(destaque, (tela_x, tela_y))

        # Desenha os elementos do jogo
        valor_celula = self.grid[linha][coluna]

        if valor_celula == "B":
            # animação de barreira
            sprite_barreira = self.carregador_elementos.elementos["barreira"][
                self.frame_animacao
            ]
            self.tela.blit(sprite_barreira, (tela_x, tela_y))
        elif valor_celula == "A":
            self.tela.blit(
                self.carregador_elementos.elementos["ponte"], (tela_x, tela_y)
            )
        elif valor_celula == "F":
            self.tela.blit(
                self.carregador_elementos.elementos["fruta"], (tela_x, tela_y)
            )
        elif valor_celula == "S":
            self.tela.blit(
                self.carregador_elementos.elementos["chegada"], (tela_x, tela_y)
            )
        elif valor_celula == "C":
            # Animação de caminhada
            sprite_tux = self.carregador_elementos.elementos["tux"][self.frame_animacao]
            self.tela.blit(sprite_tux, (tela_x, tela_y))

        # Mostra custos calculados em tempo real
        if posicao in self.custos_nos and self.estado == "buscando":
            custos = self.custos_nos[posicao]
            fonte_pequena = pygame.font.SysFont("Arial", 10)

            # Mostra G (custo do caminho)
            texto_g = fonte_pequena.render(f"G:{custos['g']}", True, PRETO)
            self.tela.blit(texto_g, (tela_x + 2, tela_y + 2))

            # Mostra H (heurística)
            texto_h = fonte_pequena.render(f"H:{custos['h']}", True, PRETO)
            self.tela.blit(texto_h, (tela_x + 2, tela_y + 15))

            # Mostra F (total)
            texto_f = fonte_pequena.render(f"F:{custos['f']}", True, PRETO)
            self.tela.blit(texto_f, (tela_x + 2, tela_y + 28))

        # Destaca o caminho encontrado
        if (linha, coluna) in self.caminho and self.estado in [
            "mostrando_caminho",
            "animando",
        ]:
            destaque = pygame.Surface((TAMANHO_CELULA, TAMANHO_CELULA), pygame.SRCALPHA)
            destaque.fill((0, 0, 255, 128))
            self.tela.blit(destaque, (tela_x, tela_y))

    def desenhar_painel_info(self):
        """Desenha o painel de informações na parte inferior da tela"""
        retangulo_painel = pygame.Rect(
            0, ALTURA_TELA - ALTURA_PAINEL_INFO, LARGURA_TELA, ALTURA_PAINEL_INFO
        )
        pygame.draw.rect(self.tela, CINZA, retangulo_painel)
        pygame.draw.rect(self.tela, PRETO, retangulo_painel, 2)

        # Status do jogo
        if self.estado == "buscando":
            texto_status = f"Buscando... Nós: Abertos({len(self.posicoes_abertas)}) | Fechados({len(self.posicoes_fechadas)})"
            if self.no_atual:
                pos_atual = self.no_atual.posicao
                texto_status += f" | Atual: ({pos_atual[0]},{pos_atual[1]})"
        elif self.estado == "mostrando_caminho":
            texto_status = (
                f"Caminho encontrado! Custo total: {len(self.caminho) - 1} passos"
            )
        elif self.estado == "animando":
            texto_status = f"Executando caminho... Passo {self.indice_animacao + 1}/{len(self.caminho_animacao)}"
        else:
            texto_status = "Preparando..."

        superficie_texto = self.fonte.render(texto_status, True, PRETO)
        self.tela.blit(superficie_texto, (10, ALTURA_TELA - ALTURA_PAINEL_INFO + 10))

        # Legenda das cores
        y_legenda = ALTURA_TELA - ALTURA_PAINEL_INFO + 35
        itens_legenda = [
            (AZUL, "Atual"),
            (VERDE, "Aberto"),
            (VERMELHO, "Fechado"),
            (AMARELO, "Vizinhos"),
        ]

        x_offset = 10
        for cor, rotulo in itens_legenda:
            # Desenha quadrado colorido
            pygame.draw.rect(self.tela, cor, (x_offset, y_legenda, 15, 15))
            pygame.draw.rect(self.tela, PRETO, (x_offset, y_legenda, 15, 15), 1)

            # Desenha texto
            superficie_rotulo = self.fonte.render(rotulo, True, PRETO)
            self.tela.blit(superficie_rotulo, (x_offset + 20, y_legenda))
            x_offset += 100

        # Legenda de custos
        y_legenda += 22
        legenda_custos = [
            ("G: Custo do caminho", PRETO, 0),
            ("H: Heurística", PRETO, 200),
            ("F: Total (G + H)", PRETO, 340),
        ]

        # Desenha a legenda de custos
        for texto, cor, pos_x in legenda_custos:
            superficie_custo = self.fonte.render(texto, True, cor)
            self.tela.blit(superficie_custo, (10 + pos_x, y_legenda))

        # Instruções
        texto_instrucoes = "R: Reiniciar | ESC: Sair"
        superficie_instrucoes = self.fonte.render(texto_instrucoes, True, PRETO)
        self.tela.blit(
            superficie_instrucoes, (10, ALTURA_TELA - ALTURA_PAINEL_INFO + 80)
        )

    def executar(self):
        """Loop principal do jogo"""
        relogio = pygame.time.Clock()
        executando = True

        while executando:
            # Processa eventos
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    executando = False
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_r:
                        self.reiniciar_jogo()
                    elif evento.key == pygame.K_ESCAPE:
                        executando = False

            # Atualiza a lógica do jogo
            self.passo_a_estrela()
            self.atualizar_camera()

            # Renderiza tudo
            self.desenhar()
            pygame.display.flip()
            relogio.tick(60)

        pygame.quit()

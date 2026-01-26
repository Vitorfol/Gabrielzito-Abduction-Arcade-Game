"""
Módulo principal do loop de jogo.
Contém a lógica de renderização e orquestração da atualização do jogo.
"""
import pygame
from raster import drawPolygon, paintPolygon, rect_to_polygon, paintTexturedEllipse, paintTexturedPolygon
from entities.world import World
from enums.difficulty import Difficulty
import constants as const

class GameLoop:
    """
    Controlador principal da sessão de jogo ativa.
    
    Atua como a camada de 'View' e 'Controller', orquestrando a atualização 
    da lógica física (delegada para a classe World) e gerenciando a 
    pipeline de renderização dos polígonos na tela.
    """
    
    def __init__(self, width, height, difficulty: Difficulty):
        """
        Inicializa uma nova sessão de jogo.
        
        Args:
            width (int): Largura da tela
            height (int): Altura da tela
            difficulty (Difficulty): Instância da classe Difficulty
        """
        self.width = width
        self.height = height

        if not isinstance(difficulty, Difficulty):
            raise TypeError("difficulty must be a Difficulty instance")

        self.difficulty = difficulty

        print(f"Iniciando jogo com: {self.difficulty.name}")
        
        # Instancia o 'Modelo' do jogo (Física e Estado)
        # TODO: Passar parâmetros de dificuldade para World (num_prizes, prize_speed)
        self.world = World(width, height)

        # Carrega texturas e converte para MATRIZES (Regra de Performance)
        self.load_textures()
        
        # Flags de Debug Visual
        self.show_hitbox = True
        
    def handle_input(self, event):
        """
        Processa eventos discretos de input.
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.world.handle_input_trigger()
            elif event.key == pygame.K_ESCAPE:
                return "BACK_TO_MENU"
        return None
    
    def update(self, keys):
        """
        Avança um frame na simulação do jogo.
        """
        self.world.update(keys)
    
    def render(self, screen):
        """
        Renderiza o frame atual. Limpa a tela e desenha as entidades.
        Usa PixelArray para cumprir a regra de "Set Pixel" com performance.
        """
        screen.fill(const.COLOR_BG_DARK)

        # LOCK da superfície para acesso direto à memória (MUITO mais rápido que set_at)
        with pygame.PixelArray(screen) as px_array:
            
            # UFO (Corpo + Borda) - ELIPSE
            ufo_hitbox = self.world.ufo.get_ellipse_hitbox()
            ufo_center = ufo_hitbox['center']
            ufo_rx = ufo_hitbox['rx']
            ufo_ry = ufo_hitbox['ry']
            
            # Pinta o interior com a textura (Passando Matriz e Array)
            # Nota: Você precisa atualizar paintTexturedEllipse em raster.py para aceitar px_array
            paintTexturedEllipse(
                px_array, self.width, self.height, 
                ufo_center, ufo_rx, ufo_ry, 
                self.ufo_matrix, self.ufo_w, self.ufo_h
            )

            # Cabo (Passamos o px_array para o sub-metodo)
            self.render_cable(px_array)

            # Garra (Muda baseada no estado aberto/fechado)
            #Get the geometry
            claw_rect = self.world.claw.get_rect()
            cx, cy, cw, ch = claw_rect

            # Escolhe a textura da garra com base no estado
            if self.world.claw.is_closed:
                # Define vertices with UV Mapping (X, Y, U, V)
                # U goes from 0 to texture_width (self.claw_w)
                # V goes from 0 to texture_height (self.claw_h)
                vertices_claw = [
                    (cx,      cy,      0,           0),            # Top-Left
                    (cx + cw, cy,      self.claw_w, 0),            # Top-Right
                    (cx + cw, cy + ch, self.claw_w, self.claw_h),  # Bottom-Right
                    (cx,      cy + ch, 0,           self.claw_h)   # Bottom-Left
                ]

                # Call the textured polygon function with the correct 4-tuple vertices
                paintTexturedPolygon(
                    px_array, self.width, self.height, 
                    vertices_claw,  # Passing the new list with UVs
                    self.claw_matrix, self.claw_w, self.claw_h, 
                    'standard'
                )
            else:
                # Define vertices with UV Mapping (X, Y, U, V)
                vertices_claw_open = [
                    (cx,      cy,      0,               0),                  # Top-Left
                    (cx + cw, cy,      self.claw_open_w, 0),                 # Top-Right
                    (cx + cw, cy + ch, self.claw_open_w, self.claw_open_h),  # Bottom-Right
                    (cx,      cy + ch, 0,               self.claw_open_h)    # Bottom-Left
                ]

                # Call the textured polygon function with the correct 4-tuple vertices
                paintTexturedPolygon(
                    px_array, self.width, self.height, 
                    vertices_claw_open,  # Passing the new list with UVs
                    self.claw_open_matrix, self.claw_open_w, self.claw_open_h, 
                    'standard'
                )

            # Prêmios não capturados
            for prize in self.world.prizes:
                if not prize.captured:
                    half = prize.size // 2
                    p_x = prize.x
                    p_y = prize.y

                    # Vértices do prêmio
                    vertices_prize = [
                        (p_x - half, p_y - half, 0,  0),                # Topo Esq
                        (p_x + half, p_y - half, self.prize_w, 0),      # Topo Dir
                        (p_x + half, p_y + half, self.prize_w, self.prize_h), # Base Dir
                        (p_x - half, p_y + half, 0,  self.prize_h)      # Base Esq
                    ]
                    
                    # Chama a versão otimizada com Matriz
                    paintTexturedPolygon(
                        px_array, self.width, self.height, 
                        vertices_prize, 
                        self.prize_matrix, self.prize_w, self.prize_h, 
                        'standard'
                    )

    def render_cable(self, px_array):
        """
        Renderiza o cabo do UFO com textura repetida (Tiling).
        Recebe px_array ao invés de screen.
        """
        cable_rect = self.world.cable.get_rect() # Retorna (x, y, w, h)
        cx, cy, cw, ch = cable_rect

        # Mapeamento UV para repetição:
        # U vai de 0 a tex_w (largura da imagem)
        # V vai de 0 a ch (altura DO CABO)
        
        vertices_cable = [
            (cx,      cy,      0,            0),   
            (cx + cw, cy,      self.cable_w, 0),   
            (cx + cw, cy + ch, self.cable_w, ch),  # V = altura do cabo
            (cx,      cy + ch, 0,            ch)   
        ]

        paintTexturedPolygon(
            px_array, self.width, self.height, 
            vertices_cable, 
            self.cable_matrix, self.cable_w, self.cable_h, 
            'tiling'
        )

    def load_textures(self):
        """Carrega imagens e converte para matrizes numéricas (list of lists)."""
        # 1. Carrega Imagens
        ufo_surf = pygame.image.load("../assets/ufo.png")
        prize_surf = pygame.image.load("../assets/gabriel.png")
        cable_surf = pygame.image.load("../assets/cable.png")
        claw_surf = pygame.image.load("../assets/claw.png")
        claw_open_surf = pygame.image.load("../assets/claw_open.png")

        # 2. Converte para Matrizes (Acesso Rápido)
        self.ufo_matrix, self.ufo_w, self.ufo_h = self.surface_to_matrix(ufo_surf)
        self.prize_matrix, self.prize_w, self.prize_h = self.surface_to_matrix(prize_surf)
        self.cable_matrix, self.cable_w, self.cable_h = self.surface_to_matrix(cable_surf)
        self.claw_matrix, self.claw_w, self.claw_h = self.surface_to_matrix(claw_surf)
        self.claw_open_matrix, self.claw_open_w, self.claw_open_h = self.surface_to_matrix(claw_open_surf)

    def surface_to_matrix(self, surface):
        """Converte Surface Pygame para lista 2D de cores [x][y]."""
        w = surface.get_width()
        h = surface.get_height()
        matrix = []
        for x in range(w):
            col = []
            for y in range(h):
                col.append(surface.get_at((x, y)))
            matrix.append(col)
        return matrix, w, h
"""
Módulo principal do loop de jogo.
Contém a lógica de renderização e orquestração da atualização do jogo.
"""
import pygame
from raster import drawPolygon, paintPolygon, rect_to_polygon, paintTexturedEllipse, paintTexturedPolygon
from entities.world import World
import constants as const

class GameLoop:
    """
    Controlador principal da sessão de jogo ativa.
    
    Atua como a camada de 'View' e 'Controller', orquestrando a atualização 
    da lógica física (delegada para a classe World) e gerenciando a 
    pipeline de renderização dos polígonos na tela.
    """
    
    def __init__(self, width, height, difficulty="NORMAL"):
        """
        Inicializa uma nova sessão de jogo.
        """
        self.width = width
        self.height = height
        self.difficulty = difficulty
        
        # Instancia o 'Modelo' do jogo (Física e Estado)
        self.world = World(width, height)
        
        # Inicia música de fundo
        from audio_manager import play_soundtrack
        play_soundtrack(volume=0.5)

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

            # Garra (Muda cor baseada no estado aberto/fechado)
            poly = rect_to_polygon(self.world.claw.get_rect())
            color = const.COLOR_CLAW_CLOSED if self.world.claw.is_closed else const.COLOR_CLAW_OPEN
            
            # Nota: paintPolygon e drawPolygon em raster.py TAMBÉM devem ser 
            # atualizados para aceitar pixel_array no lugar de surface!
            paintPolygon(px_array, poly, color)
            drawPolygon(px_array, poly, const.COLOR_CLAW_BORDER)

            # Debug: Hitbox da garra
            if self.show_hitbox:
                poly = rect_to_polygon(self.world.claw.get_grab_hitbox())
                drawPolygon(px_array, poly, const.COLOR_HITBOX_DEBUG)

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

        # 2. Converte para Matrizes (Acesso Rápido)
        self.ufo_matrix, self.ufo_w, self.ufo_h = self.surface_to_matrix(ufo_surf)
        self.prize_matrix, self.prize_w, self.prize_h = self.surface_to_matrix(prize_surf)
        self.cable_matrix, self.cable_w, self.cable_h = self.surface_to_matrix(cable_surf)

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
"""
Módulo principal do loop de jogo.
Contém a lógica de renderização e orquestração da atualização do jogo.
"""
import pygame
import os
from engine.raster import drawPolygon, paintPolygon, rect_to_polygon, paintTexturedEllipse, paintTexturedPolygon
from game.model.world import World
from game.model.difficulty import Difficulty
from game.model import config as const
from engine.viewport_utils import viewport_window
from engine.transformations import multiply_matrix_vector
from game.model.config import COLOR_TRANSITION, COLOR_TITLE, COLOR_TEXT_SELECTED, COLOR_TEXT, FONT_SIZE_LARGE, FONT_SIZE_MEDIUM


def _resolve_asset_path(filename):
    """Helper: retorna caminho absoluto para assets"""
    # Raiz do projeto
    base_path = os.path.dirname(os.path.abspath(__file__))
    asset_path = os.path.join(base_path, "..", "..", "assets", filename)
    return os.path.normpath(asset_path)

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
        self.start_time = pygame.time.get_ticks()
        self.duration = 120000  # 2 minutos (120 segundos)
        self.game_over = False

        if not isinstance(difficulty, Difficulty):
            raise TypeError("difficulty must be a Difficulty instance")

        self.difficulty = difficulty

        print(f"Iniciando jogo com: {self.difficulty.name}")
        
        # Instancia o 'Modelo' do jogo (Física e Estado)
        self.world = World(width, height, self.difficulty)

        # Carrega texturas e converte para MATRIZES (Regra de Performance)
        self.load_textures()
        
        # Flags de Debug Visual
        self.show_hitbox = True

        self.inventory_window = (0, 100, 100, 0)        # espaço lógico
        self.inventory_viewport = (width-80, 20, width, 100)  # 80x80 px
        self.VW_inventory = viewport_window(
            self.inventory_window,
            self.inventory_viewport
        )
        
    def handle_input(self, event):
        """
        Processa eventos discretos de input.
        """
        if event.type == pygame.KEYDOWN:
            if not self.game_over:
                return self.handle_normal_input(event)
            else:
                return self.game_over_input(event)
        return None
    
    def handle_normal_input(self, event):
            if event.key == pygame.K_SPACE:
                self.world.handle_input_trigger()
            elif event.key == pygame.K_ESCAPE:
                return "BACK_TO_MENU"
            
    def game_over_input(self, event):
        if self.game_over and event.key == pygame.K_RETURN:
            return "RESTART_GAME"
        elif self.game_over and event.key == pygame.K_ESCAPE:
            return "BACK_TO_MENU"
        return None
    
    def update(self, keys):
        """
        Avança um frame na simulação do jogo.
        """
        if not self.game_over:
            self.game_over = self.check_defeat()
            self.world.update(keys)
    
    def render(self, screen):
        """
        Renderiza o frame atual. Limpa a tela e desenha as entidades.
        Usa PixelArray para cumprir a regra de "Set Pixel" com performance.
        """
        # Background estático (usa blit otimizado ao invés de repintar todo frame)
        screen.blit(self.bg_cache, (0, 0))
        
        # Prepara da superfície para acesso direto à memória (mais rápido que set_at)
        with pygame.PixelArray(screen) as px_array:
            
            # Cabo
            self.render_cable(px_array)

            # UFO (Corpo + Borda) - ELIPSE
            ufo_hitbox = self.world.ufo.get_ellipse_hitbox()
            ufo_center = ufo_hitbox['center']
            ufo_rx = ufo_hitbox['rx']
            ufo_ry = ufo_hitbox['ry']
            # Pinta o interior com a textura (Passando Matriz e Array)
            paintTexturedEllipse(
                px_array, self.width, self.height, 
                ufo_center, ufo_rx, ufo_ry, 
                self.ufo_matrix, self.ufo_w, self.ufo_h
            )

            # Garra (Muda baseada no estado aberto/fechado)
            claw_rect = self.world.claw.get_rect()
            cx, cy, cw, ch = claw_rect

            # Escolhe a textura da garra com base no estado
            if self.world.claw.is_closed:
                # Define vertices with UV Mapping (X, Y, U, V)
                # U vai de 0 a texture_width (self.claw_w)
                # V vai de 0 a texture_height (self.claw_h)
                vertices_claw = [
                    (cx,      cy,      0,           0),            # Topo esquerdo
                    (cx + cw, cy,      self.claw_w, 0),            # Topo direito
                    (cx + cw, cy + ch, self.claw_w, self.claw_h),  # Inferior direito
                    (cx,      cy + ch, 0,           self.claw_h)   # Inferior esquerdo
                ]
                paintTexturedPolygon(
                    px_array, self.width, self.height, 
                    vertices_claw,  # Nova lista com UVs
                    self.claw_matrix, self.claw_w, self.claw_h, 
                    'standard'
                )
            else:
                # Define vertices com UV Mapping (X, Y, U, V)
                vertices_claw_open = [
                    (cx,      cy,      0,               0),                  # Topo esquerdo
                    (cx + cw, cy,      self.claw_open_w, 0),                 # Topo direito
                    (cx + cw, cy + ch, self.claw_open_w, self.claw_open_h),  # Inferior direito
                    (cx,      cy + ch, 0,               self.claw_open_h)    # Inferior esquerdo
                ]
                paintTexturedPolygon(
                    px_array, self.width, self.height, 
                    vertices_claw_open,  # Nova lista com UVs
                    self.claw_open_matrix, self.claw_open_w, self.claw_open_h, 
                    'standard'
                )

            # Prêmios (Gabrielzitos) - Animação por frame
            for prize in self.world.prizes:
                if not prize.captured:
                    half = prize.size // 2
                    p_x = prize.x
                    p_y = prize.y
                    
                    # Dados do frame atual da animação
                    frame_idx = int(prize.frame_index)
                    # Verificação de segurança (índice válido)
                    frame_idx = frame_idx % len(self.prize_assets)
                    
                    current_asset = self.prize_assets[frame_idx]
                    current_matrix = current_asset['matrix']
                    current_w = current_asset['w']
                    current_h = current_asset['h']

                    # Determina coordenadas UV (Flipa com direção) e dimensões
                    if prize.direction == 1:
                        u_left = 0
                        u_right = current_w
                    else:
                        u_left = current_w
                        u_right = 0

                    # Define vertices 
                    vertices_prize = [
                        (p_x - half, p_y - half, u_left,  0),            
                        (p_x + half, p_y - half, u_right, 0),            
                        (p_x + half, p_y + half, u_right, current_h), 
                        (p_x - half, p_y + half, u_left,  current_h)  
                    ]
                    paintTexturedPolygon(
                        px_array, self.width, self.height, 
                        vertices_prize, 
                        current_matrix, current_w, current_h, 
                        'standard'
                    )

            self.render_inventory(px_array)

        # Renderiza o timer do jogo
        self.render_timer(screen)

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
        bg_surf = pygame.image.load(_resolve_asset_path("pelourinho.png"))
        # OTIMIZAÇÃO: Cache do background em Surface (blit é ~100x mais rápido)
        # Renderiza o background uma vez, depois usa blit() todo frame
        bg_matrix, bg_w, bg_h = self.surface_to_matrix(bg_surf)
        
        # Renderiza background em Surface cache (uma vez só)
        self.bg_cache = pygame.Surface((self.width, self.height))
        with pygame.PixelArray(self.bg_cache) as px_array:
            vertices_bg = [
                (0, 0, 0, 0),
                (self.width, 0, bg_w, 0),
                (self.width, self.height, bg_w, bg_h),
                (0, self.height, 0, bg_h)
            ]
            paintTexturedPolygon(
                px_array, self.width, self.height,
                vertices_bg, bg_matrix, bg_w, bg_h, 'standard'
            )

        self.prize_assets = []
        self.prize_w = 0
        self.prize_h = 0
        # Carrega step1.png até step12.png (animação de movimento)
        for i in range(1, 13):
            fname = f"gabrielzito/movement/step{i}.png"
            surf = pygame.image.load(_resolve_asset_path(fname))
            
            # Converte cada frame para matriz
            matrix, w, h = self.surface_to_matrix(surf)
            # Guarda a largura/altura de cada imagem
            self.prize_assets.append({
                'matrix': matrix,
                'w': w,
                'h': h
            })
        
        ufo_surf = pygame.image.load(_resolve_asset_path("ufo.png"))
        cable_surf = pygame.image.load(_resolve_asset_path("cable.png"))
        claw_surf = pygame.image.load(_resolve_asset_path("claw.png"))
        claw_open_surf = pygame.image.load(_resolve_asset_path("claw_open.png"))

        # 2. Converte para Matrizes (Acesso Rápido)
        self.ufo_matrix, self.ufo_w, self.ufo_h = self.surface_to_matrix(ufo_surf)
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
    
    def render_inventory(self, px_array):
        """
        Renderiza os prêmios capturados dentro da viewport do inventário.
        """
        captured = [p for p in self.world.prizes if p.captured]
        if not self.prize_assets: return # Verificação de segurança

        icon_asset = self.prize_assets[0]
        icon_matrix = icon_asset['matrix']
        icon_w = icon_asset['w']
        icon_h = icon_asset['h']

        for i, prize in enumerate(captured):
            # posição lógica simples (grade)
            col = i % 4
            row = i // 4
            x = 15 + col * 25
            y = 15 + row * 25

            half = prize.size // 2

            vertices = [
                (x - half, y - half, 0, 0),
                (x + half, y - half, icon_w, 0),
                (x + half, y + half, icon_w, icon_h),
                (x - half, y + half, 0, icon_h)
            ]

            # transforma para a viewport do inventário
            vertices_t = []
            for vx, vy, u, v in vertices:
                P = [vx, vy, 1]
                x_t, y_t, _ = multiply_matrix_vector(self.VW_inventory, P)
                vertices_t.append((x_t, y_t, u, v))

            paintTexturedPolygon(
                px_array, self.width, self.height,
                vertices_t,
                icon_matrix, icon_w, icon_h,
                'standard'
            )

    def check_defeat(self):
        """Verifica se o tempo do jogo acabou."""
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.start_time
        if elapsed >= self.duration:
            return True
        return False
    
    def render_timer(self, screen):
        elapsed = pygame.time.get_ticks() - self.start_time
        remaining = max(0, self.duration - elapsed)

        seconds = remaining // 1000
        centiseconds = (remaining % 1000) // 10

        timer_text = f"{seconds:02}:{centiseconds:02}"

        font = pygame.font.SysFont(None, 36)
        text_surf = font.render(timer_text, True, (255, 255, 255))
        screen.blit(text_surf, (20, 20))

    def render_game_over(self, screen):
        # Overlay no padrão do menu
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(220)
        overlay.fill(COLOR_TRANSITION)
        screen.blit(overlay, (0, 0))

        # Fontes no padrão do menu
        font_title = pygame.font.Font(None, FONT_SIZE_LARGE)
        font_text = pygame.font.Font(None, FONT_SIZE_MEDIUM)

        # Textos
        title = font_title.render("TEMPO ESGOTADO", True, COLOR_TITLE)
        restart = font_text.render("ENTER - JOGAR NOVAMENTE", True, COLOR_TEXT_SELECTED)
        menu = font_text.render("ESC - VOLTAR AO MENU", True, COLOR_TEXT)

        # Posições
        screen.blit(
            title,
            title.get_rect(center=(self.width // 2, self.height // 2 - 80))
        )
        screen.blit(
            restart,
            restart.get_rect(center=(self.width // 2, self.height // 2))
        )
        screen.blit(
            menu,
            menu.get_rect(center=(self.width // 2, self.height // 2 + 50))
        )
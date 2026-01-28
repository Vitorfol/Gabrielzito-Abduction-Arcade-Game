"""
Módulo principal do loop de jogo.
Contém a lógica de renderização e orquestração da atualização do jogo.
"""
import pygame
import os
from engine.raster import drawPolygon, paintPolygon, rect_to_polygon, paintTexturedEllipse, paintTexturedPolygon, draw_text_raster
from game.model.world import World
from game.model.difficulty import Difficulty
from game.model import config as const
from engine.viewport_utils import viewport_window
from engine.transformations import multiply_matrix_vector
from game.model.config import COLOR_TRANSITION, COLOR_TITLE, COLOR_TEXT_SELECTED, COLOR_TEXT, FONT_SIZE_LARGE, FONT_SIZE_MEDIUM
from engine.raster import paintPolygon


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
    
    def __init__(self, width, height, difficulty: Difficulty, debug=False):
        """
        Inicializa uma nova sessão de jogo.
        
        Args:
            width (int): Largura da tela
            height (int): Altura da tela
            difficulty (Difficulty): Instância da classe Difficulty
            debug (bool): Se True, exibe informações de debug
        """
        self.width = width
        self.height = height
        self.start_time = pygame.time.get_ticks()
        self.duration = 120000  # 2 minutos (120 segundos)
        self.game_over = False
        self.debug = debug

        if not isinstance(difficulty, Difficulty):
            raise TypeError("difficulty must be a Difficulty instance")

        self.difficulty = difficulty

        if self.debug:
            print(f"Iniciando jogo com: {self.difficulty.name}")
        
        # Instancia o 'Modelo' do jogo (Física e Estado)
        self.world = World(width, height, self.difficulty, debug=self.debug)

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
        
        # Lock da superfície para acesso direto à memória (mais rápido que set_at)
        with pygame.PixelArray(screen) as px_array:
            
            # OTIMIZAÇÃO: Cópia de Memória do Background (Cache)
            with pygame.PixelArray(self.bg_cache) as bg_array:
                # Copia todos os pixels do cache para a tela
                # [:] substitui todo o conteúdo do array de destino
                px_array[:] = bg_array[:]

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
        # OTIMIZAÇÃO: Cache do background em Surface (Evita reprocessar todo frame)
        # Renderiza o background uma vez, depois usa cópia de memória
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

        # Converter para minutos e segundos
        total_seconds = remaining // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60

        # Formatar como mm:ss
        digit1 = minutes // 10
        digit2 = minutes % 10
        digit3 = seconds // 10
        digit4 = seconds % 10

        # Posição inicial no canto superior direito
        start_x = self.width - 180
        start_y = 20
        
        # Renderizar os 4 dígitos + dois pontos
        with pygame.PixelArray(screen) as px_array:
            self._draw_7seg_digit(px_array, start_x, start_y, digit1)
            self._draw_7seg_digit(px_array, start_x + 35, start_y, digit2)
            self._draw_7seg_colon(px_array, start_x + 70, start_y)
            self._draw_7seg_digit(px_array, start_x + 90, start_y, digit3)
            self._draw_7seg_digit(px_array, start_x + 125, start_y, digit4)
    
    def _draw_7seg_digit(self, px_array, x, y, digit):
        """Desenha um dígito no formato de display de 7 segmentos (Mais curto e grosso)"""
        
        # Mapeamento de dígitos para segmentos ativos
        segments_map = {
            0: [1, 1, 1, 1, 1, 1, 0],
            1: [0, 1, 1, 0, 0, 0, 0],
            2: [1, 1, 0, 1, 1, 0, 1],
            3: [1, 1, 1, 1, 0, 0, 1],
            4: [0, 1, 1, 0, 0, 1, 1],
            5: [1, 0, 1, 1, 0, 1, 1],
            6: [1, 0, 1, 1, 1, 1, 1],
            7: [1, 1, 1, 0, 0, 0, 0],
            8: [1, 1, 1, 1, 1, 1, 1],
            9: [1, 1, 1, 1, 0, 1, 1],
        }
        
        segments = segments_map.get(digit, [0, 0, 0, 0, 0, 0, 0])
        
        # --- NOVAS DIMENSÕES ---
        seg_width = 20       # Largura total horizontal
        seg_height = 6       # Espessura da barra horizontal (era 4)
        seg_length = 14      # Altura da barra vertical (era 25) - ISSO ENCURTA O DÍGITO
        thickness = 6        # Espessura visual das barras verticais
        
        color_on = (255, 255, 255)
        color_off = (50, 50, 50)
        
        # Segmento superior (top)
        if segments[0]:
            poly = [
                (x + thickness, y), 
                (x + seg_width + thickness, y), 
                (x + seg_width + 2, y + seg_height), 
                (x + thickness + 2, y + seg_height)
            ]
            paintPolygon(px_array, poly, color_on)
        
        # Segmento superior direito (top-right)
        if segments[1]:
            poly = [
                (x + seg_width + thickness, y + 2), 
                (x + seg_width + thickness + thickness, y + 4),
                (x + seg_width + thickness + thickness, y + seg_length + 2), 
                (x + seg_width + thickness, y + seg_length + 4)
            ]
            paintPolygon(px_array, poly, color_on)
        
        # Segmento inferior direito (bottom-right)
        if segments[2]:
            poly = [
                (x + seg_width + thickness, y + seg_length + 6), 
                (x + seg_width + thickness + thickness, y + seg_length + 8),
                (x + seg_width + thickness + thickness, y + 2 * seg_length + 6), 
                (x + seg_width + thickness, y + 2 * seg_length + 8)
            ]
            paintPolygon(px_array, poly, color_on)
        
        # Segmento inferior (bottom)
        if segments[3]:
            poly = [
                (x + thickness + 2, y + 2 * seg_length + 8), 
                (x + seg_width + 2, y + 2 * seg_length + 8),
                (x + seg_width + thickness, y + 2 * seg_length + 8 + seg_height), 
                (x + thickness, y + 2 * seg_length + 8 + seg_height)
            ]
            paintPolygon(px_array, poly, color_on)
        
        # Segmento inferior esquerdo (bottom-left)
        if segments[4]:
            poly = [
                (x, y + seg_length + 8), 
                (x + thickness, y + seg_length + 6),
                (x + thickness, y + 2 * seg_length + 8), 
                (x, y + 2 * seg_length + 6)
            ]
            paintPolygon(px_array, poly, color_on)
        
        # Segmento superior esquerdo (top-left)
        if segments[5]:
            poly = [
                (x, y + 4), 
                (x + thickness, y + 2),
                (x + thickness, y + seg_length + 4), 
                (x, y + seg_length + 2)
            ]
            paintPolygon(px_array, poly, color_on)
        
        # Segmento do meio (middle)
        if segments[6]:
            poly = [
                (x + thickness + 2, y + seg_length + 2), 
                (x + seg_width + 2, y + seg_length + 2),
                (x + seg_width + thickness, y + seg_length + 2 + seg_height), 
                (x + thickness, y + seg_length + 2 + seg_height)
            ]
            paintPolygon(px_array, poly, color_on)

    def _draw_7seg_colon(self, px_array, x, y):
        """Desenha os dois pontos separadores (:) ajustados para a nova altura"""
        
        color = (255, 255, 255)
        size = 4 # Aumentei um pouco o tamanho do ponto (era 3)
        
        # Ponto superior (Ajustado para o novo seg_length de 14)
        poly_top = [(x, y + 10), (x + size, y + 10), (x + size, y + 10 + size), (x, y + 10 + size)]
        paintPolygon(px_array, poly_top, color)
        
        # Ponto inferior (Ajustado para o novo seg_length de 14)
        poly_bottom = [(x, y + 25), (x + size, y + 25), (x + size, y + 25 + size), (x, y + 25 + size)]
        paintPolygon(px_array, poly_bottom, color)

    def render_game_over(self, screen):
        # 1. Desenha o Overlay (Fundo escuro)
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(220)
        overlay.fill(COLOR_TRANSITION)

        # 2. Configura as fontes
        font_path = _resolve_asset_path("fonts/ThaleahFat.ttf")
        
        # Carrega fontes customizadas
        try:
            font_title = pygame.font.Font(font_path, 55)
            font_text = pygame.font.Font(font_path, 35)
        except FileNotFoundError:
            # Fallback se esquecer de colocar o arquivo
            font_title = pygame.font.Font(None, FONT_SIZE_LARGE)
            font_text = pygame.font.Font(None, FONT_SIZE_MEDIUM)

        # 3. Abre o contexto de acesso direto aos pixels
        with pygame.PixelArray(screen) as px_array:

            # OTIMIZAÇÃO: Cópia de Memória do Background (Cache)
            with pygame.PixelArray(self.bg_cache) as bg_array:
                px_array[:] = bg_array[:]

            
            # --- TÍTULO ---
            text_title = "TEMPO ESGOTADO"
            # Calcula largura/altura para centralizar
            w, h = font_title.size(text_title) 
            x = (self.width - w) // 2
            y = (self.height // 2) - 80 - (h // 2)
            
            draw_text_raster(px_array, font_title, text_title, x, y, COLOR_TITLE)

            # --- RESTART ---
            text_restart = "ENTER - JOGAR NOVAMENTE"
            w, h = font_text.size(text_restart)
            x = (self.width - w) // 2
            y = (self.height // 2) - (h // 2)
            
            draw_text_raster(px_array, font_text, text_restart, x, y, COLOR_TEXT_SELECTED)

            # --- MENU ---
            text_menu = "ESC - VOLTAR AO MENU"
            w, h = font_text.size(text_menu)
            x = (self.width - w) // 2
            y = (self.height // 2) + 50 - (h // 2)
            
            draw_text_raster(px_array, font_text, text_menu, x, y, COLOR_TEXT)
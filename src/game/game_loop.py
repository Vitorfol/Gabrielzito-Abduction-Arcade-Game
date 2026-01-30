"""
Módulo principal do loop de jogo.
Contém a lógica de renderização e orquestração da atualização do jogo.
"""
import pygame
import os
from datetime import datetime
from engine.raster import drawPolygon, paintPolygon, rect_to_polygon, paintTexturedEllipse, paintTexturedPolygon, draw_text_raster, draw_gradient_rect
from game.audio_manager import play_audio
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
    
    Responsabilidades:
    1. Atuar como 'View' e 'Controller', orquestrando a atualização da lógica física.
    2. Gerenciar o Estado (Game Over, Vitória, Tempo).
    3. Gerenciar a pipeline de renderização manual (engine.raster).
    
    Iplementação:
    Utiliza uma engine de rasterização via software. Os arrays de pixels são manipulados diretamente para desenhar polígonos texturizados.
    """
    
    def __init__(self, width, height, difficulty: Difficulty, debug=False):
        """
        Inicializa uma nova sessão de jogo.
        
        Args:
            width (int): Largura da tela em pixels.
            height (int): Altura da tela em pixels.
            difficulty (Difficulty): Instância com configurações de dificuldade.
            debug (bool): Se True, exibe informações de debug no console.
        """
        self.width = width
        self.height = height
        self.start_time = pygame.time.get_ticks()
        self.duration = 60000  # 60 segundos
        
        # --- Flags de Controle de Estado ---
        self.game_over = False       # Trava a atualização da física
        self.victory = False         # Define qual tela final exibir (Parabéns vs Game Over)
        self.score_saved = False     # Flag de segurança para evitar múltiplos salvamentos de I/O
        
        self.debug = debug

        if not isinstance(difficulty, Difficulty):
            raise TypeError("difficulty must be a Difficulty instance")

        self.difficulty = difficulty

        if self.debug:
            print(f"Iniciando jogo com: {self.difficulty.name}")
        
        # Instancia o 'Modelo' do jogo (Física e Estado)
        self.world = World(width, height, self.difficulty, debug=self.debug)

        # Carrega texturas e converte para MATRIZES (Otimização de Performance)
        self.load_textures()
        
        # Flags de Debug Visual
        self.show_hitbox = True

        # Configuração da UI (Inventário)
        self.inventory_window = (0, 80, 80, 0)        # espaço lógico
        self.inventory_viewport = (360, 15, 440, 95)  # Centralizado no topo, 80x80 px
        self.VW_inventory = viewport_window(
            self.inventory_window,
            self.inventory_viewport
        )
        
    def handle_input(self, event):
        """
        Processa eventos discretos de input e delega para o estado correto.
        """
        if event.type == pygame.KEYDOWN:
            if not self.game_over:
                return self.handle_normal_input(event)
            else:
                return self.game_over_input(event)
        return None
    
    def handle_normal_input(self, event):
        """Processa inputs durante a gameplay ativa."""
        if event.key == pygame.K_SPACE:
            self.world.handle_input_trigger()
        elif event.key == pygame.K_ESCAPE:
            return "BACK_TO_MENU"
            
    def game_over_input(self, event):
        """Processa inputs na tela de fim de jogo."""
        if self.game_over and event.key == pygame.K_RETURN:
            return "RESTART_GAME"
        elif self.game_over and event.key == pygame.K_ESCAPE:
            return "BACK_TO_MENU"
        return None
    
    def update(self, keys):
        """
        Avança um frame na simulação do jogo.
        Verifica condições de vitória (captura total) e derrota (tempo).
        """
        if not self.game_over:
            # Atualiza física
            self.world.update(keys)
            
            # Vitória se todos os grabrielzitos foram capturados
            all_captured = all(prize.captured for prize in self.world.prizes)
            
            if all_captured:
                self.game_over = True
                self.victory = True
                self.bg_cache = self.bg_cache_win
                self.save_high_score()
                play_audio("ufo")
                
            
            # Game Over se tempo esgotado
            elif self.check_defeat():
                self.game_over = True
                self.victory = False
                self.bg_cache = self.bg_cache_lose
                play_audio("game-over")
    
    def save_high_score(self):
        """
        Salva a pontuação em arquivo se o jogador vencer.
        Garante escrita única no disco por sessão.
        """
        if self.score_saved: return
        
        elapsed = pygame.time.get_ticks() - self.start_time
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        entry = f"{self.difficulty.name}|{elapsed}|{timestamp}\n"
        
        try:
            # Salva em highscores.txt na raiz do projeto
            base_path = os.path.dirname(os.path.abspath(__file__))
            score_path = os.path.join(base_path, "..", "..", "highscores.txt")
            
            with open(score_path, "a") as f:
                f.write(entry)
                
            self.score_saved = True
            if self.debug: print(f"Score salvo: {entry.strip()}")
        except Exception as e:
            print(f"Erro ao salvar score: {e}")

    def render(self, screen):
        """
        Gerencia o pipeline gráfico.
        Utiliza pygame.PixelArray para acesso direto ao buffer de memória.
        """
        
        # Lock da superfície para acesso direto à memória
        with pygame.PixelArray(screen) as px_array:
            
            # OTIMIZAÇÃO: Cópia de Memória do Background (Cache)
            # Copia os pixels já processados do cache para a tela atual.
            with pygame.PixelArray(self.bg_cache) as bg_array:
                px_array[:] = bg_array[:]

            # Renderiza Elementos do Mundo
            self.render_cable(px_array)

            # UFO (Corpo + Borda) - ELIPSE
            ufo_hitbox = self.world.ufo.get_ellipse_hitbox()
            paintTexturedEllipse(
                px_array, self.width, self.height, 
                ufo_hitbox['center'], ufo_hitbox['rx'], ufo_hitbox['ry'], 
                self.ufo_matrix, self.ufo_w, self.ufo_h
            )

            # Garra (Geometria muda baseada no estado aberto/fechado)
            claw_rect = self.world.claw.get_rect()
            cx, cy, cw, ch = claw_rect

            if self.world.claw.is_closed:
                # Vértices [x, y, u, v]
                vertices_claw = [
                    (cx,      cy,      0,           0),
                    (cx + cw, cy,      self.claw_w, 0),
                    (cx + cw, cy + ch, self.claw_w, self.claw_h),
                    (cx,      cy + ch, 0,           self.claw_h)
                ]
                paintTexturedPolygon(
                    px_array, self.width, self.height, 
                    vertices_claw,
                    self.claw_matrix, self.claw_w, self.claw_h, 'standard'
                )
            else:
                vertices_claw_open = [
                    (cx,      cy,      0,               0),
                    (cx + cw, cy,      self.claw_open_w, 0),
                    (cx + cw, cy + ch, self.claw_open_w, self.claw_open_h),
                    (cx,      cy + ch, 0,               self.claw_open_h)
                ]
                paintTexturedPolygon(
                    px_array, self.width, self.height, 
                    vertices_claw_open,
                    self.claw_open_matrix, self.claw_open_w, self.claw_open_h, 'standard'
                )

            # 3. Renderiza Prêmios (Gabrielzitos)
            for prize in self.world.prizes:
                if not prize.captured:
                    half = prize.size // 2
                    p_x = prize.x
                    p_y = prize.y
                    
                    # LÓGICA DE FEEDBACK VISUAL:

                    if prize.being_held:
                        # Se está sendo segurado, troca para "held"
                        current_matrix = self.held_matrix
                        current_w = self.held_w
                        current_h = self.held_h

                    # Se perdeu (Game Over e !Victory), troca a textura para mocking.
                    elif self.game_over and not self.victory:
                        current_matrix = self.mock_matrix
                        current_w = self.mock_w
                        current_h = self.mock_h
                    else:
                        # Animação normal
                        frame_idx = int(prize.frame_index)
                        frame_idx = frame_idx % len(self.prize_assets)
                        
                        current_asset = self.prize_assets[frame_idx]
                        current_matrix = current_asset['matrix']
                        current_w = current_asset['w']
                        current_h = current_asset['h']

                    # Determina coordenadas UV (Inverte horizontalmente com a direção)
                    if prize.direction == 1:
                        u_left = 0
                        u_right = current_w
                    else:
                        u_left = current_w
                        u_right = 0

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

        # 4. Renderiza UI (Timer)
        # Feito fora do PixelArray principal para usar primitivas vetorizadas do timer
        self.render_timer(screen)
        
        # 5. Renderiza Tela de Fim de Jogo (se aplicável)
        if self.game_over:
            self.render_game_over(screen)

    def render_cable(self, px_array):
        """
        Renderiza o cabo do UFO com textura repetida (Tiling).
        Recebe px_array ao invés de screen para performance.
        """
        cable_rect = self.world.cable.get_rect() # Retorna (x, y, w, h)
        cx, cy, cw, ch = cable_rect

        # Mapeamento UV para repetição:
        # V vai de 0 a 'ch' (altura do segmento do cabo), causando repetição da textura
        vertices_cable = [
            (cx,      cy,      0,            0),   
            (cx + cw, cy,      self.cable_w, 0),   
            (cx + cw, cy + ch, self.cable_w, ch),
            (cx,      cy + ch, 0,            ch)   
        ]

        paintTexturedPolygon(
            px_array, self.width, self.height, 
            vertices_cable, 
            self.cable_matrix, self.cable_w, self.cable_h, 
            'tiling'
        )

    def load_textures(self):
        """
        Carrega imagens do disco e converte para matrizes numéricas.
        Gera cache do background para otimização.
        """
        # Carrega e pré-renderiza os 3 Backgrounds
        self.bg_cache_normal = self._prerender_background("pelourinho.png")
        self.bg_cache_win = self._prerender_background("pelourinho-ufo.png")
        self.bg_cache_lose = self._prerender_background("pelourinho-mocking-lens.png")

        # Define o background inicial
        self.bg_cache = self.bg_cache_normal

        # Carrega sprites da animação de movimento
        self.prize_assets = []
        self.prize_w, self.prize_h = 0, 0
        for i in range(1, 13):
            fname = f"gabrielzito/movement/step{i}.png"
            surf = pygame.image.load(_resolve_asset_path(fname))
            
            matrix, w, h = self.surface_to_matrix(surf)
            self.prize_assets.append({
                'matrix': matrix,
                'w': w,
                'h': h
            })

        # Carrega sprite de mocking            
        mock_surf = pygame.image.load(_resolve_asset_path("gabrielzito/mocking/gabriel-mocking4.png"))
        self.mock_matrix, self.mock_w, self.mock_h = self.surface_to_matrix(mock_surf)

        # Carrega Sprite de "Sendo Segurado"
        held_surf = pygame.image.load(_resolve_asset_path("gabrielzito/caught/gabriel-caught3.png"))
        self.held_matrix, self.held_w, self.held_h = self.surface_to_matrix(held_surf)
        
        # Carrega outras texturas (UFO, Garra, Cabo)
        ufo_surf = pygame.image.load(_resolve_asset_path("ufo.png"))
        cable_surf = pygame.image.load(_resolve_asset_path("cable.png"))
        claw_surf = pygame.image.load(_resolve_asset_path("claw.png"))
        claw_open_surf = pygame.image.load(_resolve_asset_path("claw_open.png"))

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
        Utiliza transformação de coordenadas (World -> Viewport).
        """
        captured = [p for p in self.world.prizes if p.captured]
        if not self.prize_assets: return

        icon_asset = self.prize_assets[0]
        icon_matrix = icon_asset['matrix']
        icon_w = icon_asset['w']
        icon_h = icon_asset['h']

        for i, prize in enumerate(captured):
            # Posição lógica em grade
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

            # Transforma vértices para a viewport do inventário
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
        """Calcula o tempo restante e desenha o display de 7 segmentos."""
        if not hasattr(self, 'final_time'):
            self.final_time = None
            
        if self.game_over and self.final_time is None:
            # Congela o tempo quando o jogo acaba
            self.final_time = pygame.time.get_ticks()
        
        if self.game_over and self.final_time is not None:
            elapsed = self.final_time - self.start_time
        else:
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
        """Desenha um dígito no formato de display de 7 segmentos (Vetorizado)."""
        
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
        
        # Dimensões do Display
        seg_width = 20
        seg_height = 6
        seg_length = 14
        thickness = 6
        
        color_on = (255, 255, 255)
        
        # Segmento superior
        if segments[0]:
            poly = [
                (x + thickness, y), 
                (x + seg_width + thickness, y), 
                (x + seg_width + 2, y + seg_height), 
                (x + thickness + 2, y + seg_height)
            ]
            paintPolygon(px_array, poly, color_on)
        
        # Segmento superior direito
        if segments[1]:
            poly = [
                (x + seg_width + thickness, y + 2), 
                (x + seg_width + thickness + thickness, y + 4),
                (x + seg_width + thickness + thickness, y + seg_length + 2), 
                (x + seg_width + thickness, y + seg_length + 4)
            ]
            paintPolygon(px_array, poly, color_on)
        
        # Segmento inferior direito
        if segments[2]:
            poly = [
                (x + seg_width + thickness, y + seg_length + 6), 
                (x + seg_width + thickness + thickness, y + seg_length + 8),
                (x + seg_width + thickness + thickness, y + 2 * seg_length + 6), 
                (x + seg_width + thickness, y + 2 * seg_length + 8)
            ]
            paintPolygon(px_array, poly, color_on)
        
        # Segmento inferior
        if segments[3]:
            poly = [
                (x + thickness + 2, y + 2 * seg_length + 8), 
                (x + seg_width + 2, y + 2 * seg_length + 8),
                (x + seg_width + thickness, y + 2 * seg_length + 8 + seg_height), 
                (x + thickness, y + 2 * seg_length + 8 + seg_height)
            ]
            paintPolygon(px_array, poly, color_on)
        
        # Segmento inferior esquerdo
        if segments[4]:
            poly = [
                (x, y + seg_length + 8), 
                (x + thickness, y + seg_length + 6),
                (x + thickness, y + 2 * seg_length + 8), 
                (x, y + 2 * seg_length + 6)
            ]
            paintPolygon(px_array, poly, color_on)
        
        # Segmento superior esquerdo
        if segments[5]:
            poly = [
                (x, y + 4), 
                (x + thickness, y + 2),
                (x + thickness, y + seg_length + 4), 
                (x, y + seg_length + 2)
            ]
            paintPolygon(px_array, poly, color_on)
        
        # Segmento do meio
        if segments[6]:
            poly = [
                (x + thickness + 2, y + seg_length + 2), 
                (x + seg_width + 2, y + seg_length + 2),
                (x + seg_width + thickness, y + seg_length + 2 + seg_height), 
                (x + thickness, y + seg_length + 2 + seg_height)
            ]
            paintPolygon(px_array, poly, color_on)

    def _draw_7seg_colon(self, px_array, x, y):
        """Desenha os dois pontos separadores (:)"""
        
        color = (255, 255, 255)
        size = 4
        
        # Ponto superior
        poly_top = [(x, y + 10), (x + size, y + 10), (x + size, y + 10 + size), (x, y + 10 + size)]
        paintPolygon(px_array, poly_top, color)
        
        # Ponto inferior
        poly_bottom = [(x, y + 25), (x + size, y + 25), (x + size, y + 25 + size), (x, y + 25 + size)]
        paintPolygon(px_array, poly_bottom, color)

    def render_game_over(self, screen):
        """
        Exibe a tela de resultado (Vitória ou Derrota) sobreposta ao jogo.
        Diferente do render() principal, desenha os textos por cima da cena atual,
        permitindo que o jogador veja o estado final.
        """
        
        # Configura as fontes
        font_path = _resolve_asset_path("fonts/ThaleahFat.ttf")
        try:
            font_title = pygame.font.Font(font_path, 55)
            font_text = pygame.font.Font(font_path, 35)
        except FileNotFoundError:
            font_title = pygame.font.Font(None, FONT_SIZE_LARGE)
            font_text = pygame.font.Font(None, FONT_SIZE_MEDIUM)

        # Define Texto e Cores
        if self.victory:
            text_title = "SUCCESS!"
            text_subtitle = "VOCE ABDUZIU TODOS!"
            color_title = (100, 255, 100) # Verde
        else:
            text_title = "GAME OVER!"
            text_subtitle = "GABRIELZITOS ESCAPARAM..."
            color_title = (255, 80, 80)   # Vermelho
        
        # Cores do Gradiente
        color_top = (40, 40, 90)      # Azul Cyberpunk
        color_bottom = (10, 10, 20)   # Quase Preto

        # Geometria da Moldura - Metade superior da tela
        margin_x = 50
        margin_top = 80
        
        # A altura máxima é a metade da tela menos uma margem
        limit_y = (self.height // 2) - 20
        
        x0 = margin_x
        y0 = margin_top
        x1 = self.width - margin_x
        y1 = limit_y

        width_rect = x1 - x0
        height_rect = y1 - y0
        
        # Vértices para o rasterizador desenhar o polígono
        rect_frame = [
            (x0, y0),
            (x1, y0),
            (x1, y1),
            (x0, y1)
        ]

        # Renderização via PixelArray
        with pygame.PixelArray(screen) as px_array:
            
            # --- MOLDURA (Fundo e Borda) ---
            # Fundo com gradiente e borda branca sólida
            draw_gradient_rect(px_array, x0, y0, width_rect, height_rect, color_top, color_bottom)
            drawPolygon(px_array, rect_frame, (255, 255, 255))

            # --- TEXTOS (Posicionados relativos ao centro da moldura) ---
            center_frame_x = self.width // 2
            # O centro Y da moldura para alinhar o texto
            center_frame_y = y0 + (y1 - y0) // 2 

            # TÍTULO (acima do centro da moldura)
            w, h = font_title.size(text_title)
            x = center_frame_x - (w // 2)
            y = center_frame_y - 90 
            draw_text_raster(px_array, font_title, text_title, x, y, color_title)

            # SUBTÍTULO
            w_sub, h_sub = font_text.size(text_subtitle)
            x_sub = center_frame_x - (w_sub // 2)
            y_sub = y + 55
            draw_text_raster(px_array, font_text, text_subtitle, x_sub, y_sub, COLOR_TEXT)

            # OPÇÕES (Restart / Menu) - abaixo do centro
            text_restart = "ENTER: JOGAR NOVAMENTE"
            w_res, h_res = font_text.size(text_restart)
            x_res = center_frame_x - (w_res // 2)
            y_res = center_frame_y + 30
            draw_text_raster(px_array, font_text, text_restart, x_res, y_res, COLOR_TEXT_SELECTED)

            text_menu = "ESC: VOLTAR AO MENU"
            w_menu, h_menu = font_text.size(text_menu)
            x_menu = center_frame_x - (w_menu // 2)
            y_menu = y_res + 25
            draw_text_raster(px_array, font_text, text_menu, x_menu, y_menu, COLOR_TEXT)
    

    def _prerender_background(self, filename):
        """
        Helper para carregar imagem e gerar superfície de cache já rasterizada.
        """
        try:
            surf = pygame.image.load(_resolve_asset_path(filename))
        except FileNotFoundError:
            if self.debug: print(f"AVISO: Background {filename} não encontrado.")
            return None

        matrix, w, h = self.surface_to_matrix(surf)
        
        cache = pygame.Surface((self.width, self.height))
        with pygame.PixelArray(cache) as px_array:
            vertices = [
                (0, 0, 0, 0),
                (self.width, 0, w, 0),
                (self.width, self.height, w, h),
                (0, self.height, 0, h)
            ]
            paintTexturedPolygon(
                px_array, self.width, self.height,
                vertices, matrix, w, h, 'standard'
            )
        return cache
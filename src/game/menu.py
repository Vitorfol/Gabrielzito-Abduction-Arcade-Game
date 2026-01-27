"""
Sistema de menu interativo para o Claw Machine Game.
Inclui navegação por teclado, seleção de dificuldade e animações nos cantos.
"""
import pygame
import math
import os
from engine.raster import drawPolygon, paintPolygon, draw_circle, flood_fill_iterativo, paintTexturedPolygon
from engine.transformations import rotation, scale, multiply_matrices, apply_matrix_to_point
from game.menu_scene import ClawMachineScene
from game.model.config import *
from game.audio_manager import play_audio


def _resolve_asset_path(filename):
    """Helper: Resolve absolute path to asset file"""
    # Get project root (three levels up from game/menu.py: game/ -> src/ -> root/)
    base_path = os.path.dirname(os.path.abspath(__file__))
    asset_path = os.path.join(base_path, "..", "..", "assets", filename)
    return os.path.normpath(asset_path)


class TargetCircle:
    """Círculo tipo 'alvo' com anéis concêntricos que pulsa (escala)"""
    
    def __init__(self, x, y, base_radius=35):
        self.center_x = x
        self.center_y = y
        self.base_radius = base_radius
        
        # Estado da animação (apenas escala, sem rotação)
        self.scale_factor = 1.0
        self.scale_direction = 1
        
        # Velocidades de animação
        self.scale_speed = SCALE_SPEED
        self.min_scale = SCALE_MIN
        self.max_scale = SCALE_MAX
        
        # Cores dos anéis concêntricos (alvo tipo tiro ao alvo)
        self.ring_colors = [
            (255, 50, 50),   # Vermelho (centro)
            (255, 255, 255), # Branco
            (255, 50, 50),   # Vermelho (externo)
        ]
        self.border_color = (200, 200, 200)  # Cinza para bordas
        
    def update(self):
        """Atualiza animação de escala pulsante"""
        self.scale_factor += self.scale_speed * self.scale_direction
        
        if self.scale_factor >= self.max_scale:
            self.scale_factor = self.max_scale
            self.scale_direction = -1
        elif self.scale_factor <= self.min_scale:
            self.scale_factor = self.min_scale
            self.scale_direction = 1
    
    def render(self, screen):
        """Renderiza o alvo com 3 anéis concêntricos"""
        # Calcula raios dos 3 anéis com escala aplicada
        radii = [
            int(self.base_radius * self.scale_factor),         # Externo
            int(self.base_radius * 0.66 * self.scale_factor),  # Médio
            int(self.base_radius * 0.33 * self.scale_factor),  # Centro
        ]
        
        # Desenha do maior para o menor (de fora para dentro)
        for i, radius in enumerate(radii):
            if radius > 0:
                # Desenha borda do círculo
                draw_circle(screen, (self.center_x, self.center_y), 
                           radius, self.border_color)
                
                # Preenche com flood fill (usa cor do anel correspondente)
                # Inverte índice: anel externo usa ring_colors[2], centro usa [0]
                fill_color = self.ring_colors[2 - i]
                
                # Flood fill a partir do centro de cada anel
                try:
                    flood_fill_iterativo(screen, self.center_x, self.center_y, 
                                       fill_color, self.border_color)
                except:
                    pass  # Evita crash se flood fill falhar


class TexturedBox:
    """Box texturizada que rotaciona e escala nos cantos da tela"""
    
    def __init__(self, x, y, texture_path, size=ROTATING_BOX_SIZE):
        self.center_x = x
        self.center_y = y
        self.base_size = size
        
        # Carregar textura
        self.texture_matrix, self.tex_w, self.tex_h = self._load_texture(texture_path)
        
        # Estado da animação
        self.rotation_angle = 0
        self.scale_factor = 1.0
        self.scale_direction = 1
        
        # Velocidades
        self.rotation_speed = ROTATION_SPEED
        self.scale_speed = SCALE_SPEED
        self.min_scale = SCALE_MIN
        self.max_scale = SCALE_MAX
    
    def _load_texture(self, path):
        """Carrega PNG e converte para matriz de textura"""
        try:
            surf = pygame.image.load(path)
            w, h = surf.get_width(), surf.get_height()
            matrix = []
            for x in range(w):
                col = []
                for y in range(h):
                    col.append(surf.get_at((x, y)))
                matrix.append(col)
            return matrix, w, h
        except Exception as e:
            # Retorna uma matriz 1x1 transparente como fallback
            return [[(0, 0, 0, 0)]], 1, 1
    
    def update(self):
        """Atualiza animação de rotação e escala"""
        self.rotation_angle += self.rotation_speed
        if self.rotation_angle >= 360:
            self.rotation_angle -= 360
            
        self.scale_factor += self.scale_speed * self.scale_direction
        
        if self.scale_factor >= self.max_scale:
            self.scale_factor = self.max_scale
            self.scale_direction = -1
        elif self.scale_factor <= self.min_scale:
            self.scale_factor = self.min_scale
            self.scale_direction = 1
    
    def render(self, pixel_array, screen_width, screen_height):
        """Renderiza a box texturizada com transformações aplicadas"""
        
        # Vértices originais da box (quadrado centrado na origem)
        # UVs em coordenadas de textura absolutas (0 a tex_w, 0 a tex_h)
        half_size = self.base_size / 2
        vertices_local = [
            (-half_size, -half_size, 0, 0),                      # top-left
            (half_size, -half_size, self.tex_w, 0),              # top-right
            (half_size, half_size, self.tex_w, self.tex_h),      # bottom-right
            (-half_size, half_size, 0, self.tex_h)               # bottom-left
        ]
        
        # Aplicar transformações: escala -> rotação -> translação
        scale_matrix = scale(self.scale_factor, self.scale_factor)
        rot_matrix = rotation(math.radians(self.rotation_angle))
        transform = multiply_matrices(rot_matrix, scale_matrix)
        
        # Aplicar às vertices (mantém UV)
        vertices_uv = []
        for x, y, u, v in vertices_local:
            tx, ty = apply_matrix_to_point((x, y), transform)
            screen_x = int(tx + self.center_x)
            screen_y = int(ty + self.center_y)
            vertices_uv.append((screen_x, screen_y, u, v))
        
        # Renderizar texturizado (sem criar novo PixelArray)
        paintTexturedPolygon(
            pixel_array,
            screen_width,
            screen_height,
            vertices_uv,
            self.texture_matrix,
            self.tex_w,
            self.tex_h,
            method='standard'
        )


class TexturedEllipse:
    """Elipse texturizada que pulsa (apenas escala, sem rotação)"""
    
    def __init__(self, x, y, texture_path, base_rx=40, base_ry=20):
        self.center_x = x
        self.center_y = y
        self.base_rx = base_rx
        self.base_ry = base_ry
        
        # Carregar textura
        self.texture_matrix, self.tex_w, self.tex_h = self._load_texture(texture_path)
        
        # Estado da animação (apenas escala)
        self.scale_factor = 1.0
        self.scale_direction = 1
        
        # Velocidades
        self.scale_speed = SCALE_SPEED
        self.min_scale = SCALE_MIN
        self.max_scale = SCALE_MAX
    
    def _load_texture(self, path):
        """Carrega PNG e converte para matriz de textura"""
    def _load_texture(self, path):
        """Carrega PNG e converte para matriz de textura"""
        try:
            surf = pygame.image.load(path)
            w, h = surf.get_width(), surf.get_height()
            matrix = []
            for x in range(w):
                col = []
                for y in range(h):
                    col.append(surf.get_at((x, y)))
                matrix.append(col)
            return matrix, w, h
        except Exception as e:
            # Retorna uma matriz 1x1 transparente como fallback
            print(f"Error loading texture '{path}': {e}")
            return [[(0, 0, 0, 0)]], 1, 1
    
    def update(self):
        """Atualiza animação de escala pulsante"""
        self.scale_factor += self.scale_speed * self.scale_direction
        
        if self.scale_factor >= self.max_scale:
            self.scale_factor = self.max_scale
            self.scale_direction = -1
        elif self.scale_factor <= self.min_scale:
            self.scale_factor = self.min_scale
            self.scale_direction = 1
    
    def render(self, pixel_array, screen_width, screen_height):
        """Renderiza elipse texturizada (aproximada por polígono)"""
        from engine.raster import paintTexturedPolygon
        
        # Aproximar elipse com polígono de 16 lados
        num_segments = 16
        vertices_uv = []
        
        rx = self.base_rx * self.scale_factor
        ry = self.base_ry * self.scale_factor
        
        for i in range(num_segments):
            angle = (2 * math.pi * i) / num_segments
            x = self.center_x + rx * math.cos(angle)
            y = self.center_y + ry * math.sin(angle)
            
            # UV mapping (coordenadas absolutas de textura)
            u = (0.5 + 0.5 * math.cos(angle)) * self.tex_w
            v = (0.5 + 0.5 * math.sin(angle)) * self.tex_h
            
            vertices_uv.append((int(x), int(y), u, v))
        
        # Renderizar texturizado (sem criar novo PixelArray)
        paintTexturedPolygon(
            pixel_array,
            screen_width,
            screen_height,
            vertices_uv,
            self.texture_matrix,
            self.tex_w,
            self.tex_h,
            method='standard'
        )


class DifficultySelector:
    """Submenu de seleção de dificuldade com navegação horizontal"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.difficulties = ["EASY", "NORMAL", "HARD"]
        self.selected_index = 1  # Começa em NORMAL
        
        # Layout
        self.spacing = MENU_DIFFICULTY_SPACING
        self.arrow_size = MENU_ARROW_SIZE
        
        # Cores
        self.text_color = COLOR_TEXT
        self.selected_color = COLOR_TEXT_SELECTED
        self.arrow_color = COLOR_ARROW
        
    def handle_input(self, event):
        """Processa input de setas horizontais"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.selected_index = max(0, self.selected_index - 1)
                return True
            elif event.key == pygame.K_RIGHT:
                self.selected_index = min(len(self.difficulties) - 1, self.selected_index + 1)
                return True
        return False
    
    def get_selected_difficulty(self):
        """Retorna a dificuldade selecionada"""
        return self.difficulties[self.selected_index]
    
    def render(self, screen, font):
        """Renderiza o seletor de dificuldade centralizado"""
        # Calcular largura total para centralizar
        total_width = (len(self.difficulties) - 1) * self.spacing
        start_x = self.x - total_width // 2
        
        # Renderizar cada opção (todas visíveis, só a selecionada em verde)
        for i, difficulty in enumerate(self.difficulties):
            color = self.selected_color if i == self.selected_index else self.text_color
            text_surf = font.render(difficulty, True, color)
            text_rect = text_surf.get_rect(center=(start_x + i * self.spacing, self.y))
            screen.blit(text_surf, text_rect)


class Menu:
    """Menu principal com navegação e animações"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # Cenário de fundo
        self.scene = ClawMachineScene(width, height)
        
        # Opções do menu
        self.options = ["JOGAR", "DIFICULDADE", "GUIA"]
        self.selected_index = 0
        
        # Estado do menu
        self.in_difficulty_menu = False
        self.in_guia_menu = False
        self.difficulty_selector = DifficultySelector(width // 2, height // 2 + 80)
        
        # Layout
        self.option_spacing = MENU_OPTION_SPACING
        self.start_y = height // 2 + MENU_START_Y_OFFSET
        
        # Cores
        self.text_color = COLOR_TEXT
        self.selected_color = COLOR_TEXT_SELECTED
        self.title_color = COLOR_TITLE
        
        # Font
        self.font = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        self.title_font = pygame.font.Font(None, FONT_SIZE_LARGE)
        
        # Elementos texturizados nos cantos
        margin = ROTATING_BOX_MARGIN
        self.corner_elements = [
            TexturedBox(margin, margin, _resolve_asset_path("mocking/gabriel-mocking4.png")),                    # Superior esquerdo
            TexturedEllipse(width - margin, margin, _resolve_asset_path("ufo.png"), base_rx=40, base_ry=25),     # Superior direito (UFO)
            TexturedBox(margin, height - margin, _resolve_asset_path("gabriel-frente.png")),                     # Inferior esquerdo
            TexturedBox(width - margin - 110, height - margin, _resolve_asset_path("gabriel.png"))               # Inferior direito (MOVIDO)
        ]
        
        # Círculo alvo no canto inferior direito (posição original)
        self.target_circle = TargetCircle(width - margin, height - margin, base_radius=35)
        
        # Transição suave
        self.transition_alpha = 0
        self.transitioning = False
        self.transition_speed = TRANSITION_SPEED
        self.transition_complete = False
        
    def handle_input(self, event):
        """Processa input do teclado"""
        if self.transitioning:
            return None
            
        # Se estamos no submenu de guia
        if self.in_guia_menu:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                    self.in_guia_menu = False
                    return None
            return None
            
        # Se estamos no submenu de dificuldade
        if self.in_difficulty_menu:
            if self.difficulty_selector.handle_input(event):
                # Retornar indicação de que dificuldade mudou
                return "DIFFICULTY_CHANGED"
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                    self.in_difficulty_menu = False
                    return None
        else:
            # Menu principal
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    return self._handle_selection()
        
        return None
    
    def _handle_selection(self):
        """Processa a seleção de uma opção do menu"""
        selected_option = self.options[self.selected_index]
        
        if selected_option == "JOGAR":
            # Tocar áudio antes da transição
            self._play_start_audio()
            # Iniciar transição para o jogo
            self.start_transition()
            return "PLAY"
        elif selected_option == "DIFICULDADE":
            # Abrir submenu de dificuldade (agora LEFT/RIGHT funcionam)
            self.in_difficulty_menu = True
            return None
        elif selected_option == "GUIA":
            # Abrir submenu de guia
            self.in_guia_menu = True
            return None
        
        return None
    
    def _play_start_audio(self):
        """Toca efeito sonoro ao iniciar o jogo"""
        play_audio("homens-verde", volume=0.8)
       
    
    def start_transition(self):
        """Inicia animação de transição"""
        self.transitioning = True
        self.transition_alpha = 0
        self.transition_complete = False
    
    def update(self):
        """Atualiza estado do menu e animações"""
        # Atualizar elementos dos cantos
        for element in self.corner_elements:
            element.update()
        
        # Atualizar círculo alvo
        self.target_circle.update()
        
        # Atualizar transição
        if self.transitioning:
            self.transition_alpha += self.transition_speed
            if self.transition_alpha >= 255:
                self.transition_alpha = 255
                self.transition_complete = True
    
    def is_transition_complete(self):
        """Retorna True quando a transição está completa"""
        return self.transition_complete
    
    def get_selected_difficulty(self):
        """Retorna a dificuldade selecionada"""
        return self.difficulty_selector.get_selected_difficulty()
    
    def render(self, screen):
        """Renderiza o menu completo"""
        # Renderizar cenário de fundo
        self.scene.render(screen)
        
        # Renderizar texturas em um único PixelArray (performance)
        with pygame.PixelArray(screen) as pixel_array:
            screen_width = screen.get_width()
            screen_height = screen.get_height()
            
            # Renderizar elementos texturizados nos cantos
            for element in self.corner_elements:
                element.render(pixel_array, screen_width, screen_height)
        
        # Renderizar círculo alvo (não usa textura)
        self.target_circle.render(screen)
        
        # Título
        title_text = self.title_font.render("GABRIELZITO MACHINE", True, self.title_color)
        title_rect = title_text.get_rect(center=(self.width // 2, 80))
        screen.blit(title_text, title_rect)
        
        if self.in_difficulty_menu:
            # Renderizar submenu de dificuldade
            self._render_difficulty_menu(screen)
        elif self.in_guia_menu:
            # Renderizar submenu de guia
            self._render_guia_menu(screen)
        else:
            # Renderizar opções do menu principal
            self._render_main_menu(screen)
        
        # Renderizar overlay de transição
        if self.transitioning:
            self._render_transition(screen)
    
    def _render_main_menu(self, screen):
        """Renderiza as opções do menu principal"""
        for i, option in enumerate(self.options):
            color = self.selected_color if i == self.selected_index else self.text_color
            text_surf = self.font.render(option, True, color)
            text_rect = text_surf.get_rect(center=(self.width // 2, self.start_y + i * self.option_spacing))
            screen.blit(text_surf, text_rect)
            
            # Indicador de seleção (retângulo ao redor)
            if i == self.selected_index:
                padding = 10
                rect_poly = [
                    (text_rect.left - padding, text_rect.top - padding),
                    (text_rect.right + padding, text_rect.top - padding),
                    (text_rect.right + padding, text_rect.bottom + padding),
                    (text_rect.left - padding, text_rect.bottom + padding)
                ]
                drawPolygon(screen, rect_poly, self.selected_color)
    
    def _render_difficulty_menu(self, screen):
        """Renderiza o submenu de seleção de dificuldade"""
        # Título do submenu
        subtitle = self.font.render("SELECIONE A DIFICULDADE", True, self.title_color)
        subtitle_rect = subtitle.get_rect(center=(self.width // 2, self.height // 2 - 50))
        screen.blit(subtitle, subtitle_rect)
        
        # Renderizar seletor
        self.difficulty_selector.render(screen, self.font)
    
    def _render_guia_menu(self, screen):
        """Renderiza o submenu de guia/explicação"""
        # Título (mesmo tamanho do menu de dificuldade)
        title = self.font.render("GUIA", True, self.title_color)
        title_rect = title.get_rect(center=(self.width // 2, self.height // 2 - 160))
        screen.blit(title, title_rect)
        
        # Calcular dimensões da caixa de texto
        box_padding = 40
        box_x = 100
        box_y = 170
        box_w = self.width - 200
        box_h = 320
        
        # Fundo cinza para facilitar leitura
        box_surface = pygame.Surface((box_w, box_h))
        box_surface.fill((40, 40, 50))
        box_surface.set_alpha(220)
        screen.blit(box_surface, (box_x, box_y))
        
        # Borda da caixa
        pygame.draw.rect(screen, COLOR_TEXT, pygame.Rect(box_x, box_y, box_w, box_h), 2)
        
        # Descrição (multi-linha, mais formal baseada no README)
        description_font = pygame.font.Font(None, 24)
        description_lines = [
            "Gabrielzito Machine é um jogo arcade 2D inspirado nas clássicas",
            "máquinas de garra, desenvolvido para a disciplina de Computação",
            "Gráfica. O jogador controla uma garra mecânica dentro da máquina,",
            "tentando capturar gabrielzitos em movimento.",
            "",
            "Controles:",
            "  • SETAS: Movimentar a garra (eixos X e Y).",
            "  • ESPAÇO: Descer a garra / Fechar a garra para capturar gabrielzitos.",
            "",
            "Níveis de Dificuldade:",
            "A dificuldade selecionada no menu afeta a velocidade dos gabrielzitos",
            "e a quantidade de gabrielzitos em movimento dentro da máquina."
        ]
        
        start_y = box_y + 25
        line_spacing = 24
        for i, line in enumerate(description_lines):
            text = description_font.render(line, True, COLOR_TEXT)
            text_rect = text.get_rect(left=box_x + 30, top=start_y + i * line_spacing)
            screen.blit(text, text_rect)
    
    def _render_transition(self, screen):
        """Renderiza overlay de transição fade to black"""
        overlay = pygame.Surface((self.width, self.height))
        overlay.fill(COLOR_TRANSITION)
        overlay.set_alpha(self.transition_alpha)
        screen.blit(overlay, (0, 0))

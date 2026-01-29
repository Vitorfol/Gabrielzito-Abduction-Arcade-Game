"""
Sistema de menu interativo para o Claw Machine Game.
Inclui navegação por teclado, seleção de dificuldade e animações nos cantos.
"""
import sys
import pygame
import math
import os
from engine.raster import drawPolygon, draw_circle, flood_fill_iterativo, paintTexturedPolygon, draw_text_raster, draw_gradient_rect, paint_ellipse
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
    
    def render(self, pixel_array):
        """
        Renderiza o alvo. 
        Recebe 'pixel_array'.
        """
        # Calcula raios
        radii = [
            int(self.base_radius * self.scale_factor),
            int(self.base_radius * 0.66 * self.scale_factor),
            int(self.base_radius * 0.33 * self.scale_factor),
        ]
        
        # Desenha do maior para o menor
        for i, radius in enumerate(radii):
            if radius > 0:
                # 1. Desenha borda (função otimizada do raster.py)
                draw_circle(pixel_array, (self.center_x, self.center_y), 
                           radius, self.border_color)
                
                # 2. Preenche
                fill_color = self.ring_colors[2 - i]
                
                # REMOVIDO O TRY/EXCEPT para podermos ver erros se existirem
                flood_fill_iterativo(pixel_array, self.center_x, self.center_y, 
                                   fill_color, self.border_color)


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
            (-half_size, -half_size, 0, 0),                      # Topo esquerdo
            (half_size, -half_size, self.tex_w, 0),              # topo direito
            (half_size, half_size, self.tex_w, self.tex_h),      # inferior direito
            (-half_size, half_size, 0, self.tex_h)               # inferior esquerdo
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
    
    def __init__(self, x, y, current_difficulty="NORMAL"):
        self.x = x
        self.y = y
        self.difficulties = ["EASY", "NORMAL", "HARD"]
        # Iniciar com a dificuldade atual
        try:
            self.selected_index = self.difficulties.index(current_difficulty)
        except ValueError:
            self.selected_index = 1  # Fallback para NORMAL
        
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
    
    def render(self, pixel_array, font):
        """Renderiza o seletor de dificuldade usando rasterização direta"""
        # Calcular largura total para centralizar
        total_width = (len(self.difficulties) - 1) * self.spacing
        start_x = self.x - total_width // 2
        
        for i, difficulty in enumerate(self.difficulties):
            color = self.selected_color if i == self.selected_index else self.text_color
            # Calcular dimensões e posição centralizada
            w, h = font.size(difficulty)
            # Posição X baseada no índice + offset para centralizar o texto
            pos_x = (start_x + i * self.spacing) - (w // 2)
            # Posição Y centralizada
            pos_y = self.y - (h // 2)
            draw_text_raster(pixel_array, font, difficulty, pos_x, pos_y, color)


class Menu:
    """Menu principal com navegação e animações"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # Cenário de fundo
        self.scene = ClawMachineScene(width, height)
        
        # Opções do menu
        self.options = ["JOGAR", "DIFICULDADE", "GUIA", "SAIR"]
        self.selected_index = 0
        
        # Estado do menu
        self.in_difficulty_menu = False
        self.in_guia_menu = False
        self.current_difficulty = "NORMAL"
        self.difficulty_selector = DifficultySelector(width // 2, height // 2 + 80, self.current_difficulty)
        
        # Layout
        self.option_spacing = MENU_OPTION_SPACING
        self.start_y = height // 2 + MENU_START_Y_OFFSET
        
        # Cores
        self.text_color = COLOR_TEXT
        self.selected_color = COLOR_TEXT_SELECTED
        self.title_color = COLOR_TITLE
        
        # Fontes
        font_path = _resolve_asset_path("fonts/ThaleahFat.ttf")
        pixel_font_path = _resolve_asset_path("fonts/PixeloidSans.ttf")
        
        self.font = pygame.font.Font(font_path, 35)       
        self.title_font = pygame.font.Font(font_path, 55)
        
        # Fonte específica para a lista de highscores
        self.small_font = pygame.font.Font(pixel_font_path, 20)
        
        # Carrega os highscores
        self.highscores = self._load_highscores()
        
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
                # Atualizar a dificuldade atual quando o usuário navega
                self.current_difficulty = self.difficulty_selector.get_selected_difficulty()
                # Retornar indicação de que dificuldade mudou
                return "DIFFICULTY_CHANGED"
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                    # Salvar a dificuldade selecionada antes de sair
                    self.current_difficulty = self.difficulty_selector.get_selected_difficulty()
                    self.in_difficulty_menu = False
                    # Retornar indicação de que dificuldade pode ter mudado
                    return "DIFFICULTY_CHANGED"
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
            # Recriar o seletor de dificuldade com a dificuldade atual
            self.difficulty_selector = DifficultySelector(self.width // 2, self.height // 2 + 80, self.current_difficulty)
            # Abrir submenu de dificuldade (agora LEFT/RIGHT funcionam)
            self.in_difficulty_menu = True
            return None
        elif selected_option == "GUIA":
            # Abrir submenu de guia
            self.in_guia_menu = True
            return None
        elif selected_option == "SAIR":
            # Sair do jogo
            pygame.quit()
            sys.exit()
        
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
    
    def set_current_difficulty(self, difficulty):
        """Define a dificuldade atual do menu"""
        self.current_difficulty = difficulty
    
    def render(self, screen):
        """Renderiza o menu completo"""
        # Renderizar cenário de fundo
        self.scene.render(screen)
        
        # Renderização por pixel (Texto, Polígonos e Gradientes)
        # OTIMIZAÇÃO: Um único PixelArray para tudo
        with pygame.PixelArray(screen) as pixel_array:
            screen_width = screen.get_width()
            screen_height = screen.get_height()

            # FUNDO DO GUIA (GRADIENTE)
            if self.in_guia_menu:
                box_x = 100
                box_y = 170
                box_w = self.width - 200
                box_h = 320
                
                # Cores do Gradiente: Azul Cyberpunk a Preto
                color_top = (40, 40, 90)
                color_bottom = (10, 10, 20)
                
                # Desenha o fundo com gradiente
                draw_gradient_rect(pixel_array, box_x, box_y, box_w, box_h, color_top, color_bottom)
                
                # Desenha a Borda Branca (Manual, pixel a pixel)
                border_color = (255, 255, 255)
                # Topo e Base
                pixel_array[box_x:box_x+box_w, box_y] = border_color
                pixel_array[box_x:box_x+box_w, box_y+box_h-1] = border_color
                # Laterais
                pixel_array[box_x, box_y:box_y+box_h] = border_color
                pixel_array[box_x+box_w-1, box_y:box_y+box_h] = border_color
            
            # ELEMENTOS DO MENU
            # Elementos texturizados nos cantos
            for element in self.corner_elements:
                element.render(pixel_array, screen_width, screen_height)
            
            # Círculo alvo
            self.target_circle.render(pixel_array)
        
            # Título Principal
            title_str = "GABRIELZITO ABDUCTION"
            tw, th = self.title_font.size(title_str)
            tx = (self.width - tw) // 2
            ty = 80 - (th // 2)
            draw_text_raster(pixel_array, self.title_font, title_str, tx, ty, self.title_color)
            
            if not self.in_guia_menu and not self.in_difficulty_menu:
                self._render_best_times(pixel_array)

            # Renderizar Submenus (Textos)
            if self.in_difficulty_menu:
                self._render_difficulty_menu(pixel_array)
            elif self.in_guia_menu:
                self._render_guia_menu(pixel_array)
            else:
                self._render_main_menu(pixel_array)
        
        # Transição
        if self.transitioning:
             with pygame.PixelArray(screen) as px_array:
                self._render_transition(px_array)
    
    def _render_main_menu(self, pixel_array):
        """Renderiza as opções do menu principal via raster"""
        for i, option in enumerate(self.options):
            color = self.selected_color if i == self.selected_index else self.text_color
            # Calcula posição
            w, h = self.font.size(option)
            x = (self.width - w) // 2
            y = self.start_y + i * self.option_spacing - (h // 2)
            
            draw_text_raster(pixel_array, self.font, option, x, y, color)
            
            if i == self.selected_index:    # Indicador de seleção (retângulo ao redor)
                padding = 10
                # Coordenadas do retângulo
                rect_left = x - padding
                rect_top = y - padding
                rect_right = x + w + padding
                rect_bottom = y + h + padding
                rect_poly = [
                    (rect_left, rect_top),
                    (rect_right, rect_top),
                    (rect_right, rect_bottom),
                    (rect_left, rect_bottom)
                ]
                # drawPolygon usa bresenham
                drawPolygon(pixel_array, rect_poly, self.selected_color)
    
    def _render_difficulty_menu(self, pixel_array):
        """Renderiza o submenu de seleção de dificuldade via raster"""
        # Título do submenu
        sub_text = "SELECIONE A DIFICULDADE"
        w, h = self.font.size(sub_text)
        x = (self.width - w) // 2
        y = (self.height // 2 - 50) - (h // 2)
        
        draw_text_raster(pixel_array, self.font, sub_text, x, y, self.title_color)
        
        # Renderizar seletor
        self.difficulty_selector.render(pixel_array, self.font)
    
    def _render_guia_menu(self, pixel_array):
        """Renderiza o texto do guia via raster"""
        # Título
        title_text = "GUIA"
        w, h = self.font.size(title_text)
        x = (self.width - w) // 2
        y = (self.height // 2 - 160) - (h // 2)
        
        draw_text_raster(pixel_array, self.font, title_text, x, y, self.title_color)
        
        # Configurações da caixa de texto
        box_x = 100
        box_y = 170
        start_y = box_y + 10
        line_spacing = 24
        
        # Carrega a fonte customizada da pasta assets
        font_path = _resolve_asset_path("fonts/PixeloidSans.ttf")
        description_font = pygame.font.Font(font_path, 15)
        description_lines = [
            "Gabrielzito Machine é um jogo arcade 2D inspirado nas clássicas",
            "máquinas de garra, desenvolvido para a disciplina de Computação",
            "Gráfica. O jogador controla uma garra mecânica dentro da máquina,",
            "tentando capturar gabrielzitos em movimento.",
            "",
            "Controles:",
            "• SETAS: Movimentar a garra (eixos X e Y).",
            "• ESPAÇO: Descer a garra / Fechar a garra para capturar gabrielzitos.",
            "",
            "Níveis de Dificuldade:",
            "A dificuldade selecionada no menu afeta a velocidade dos gabrielzitos",
            "e a quantidade de gabrielzitos em movimento dentro da máquina."
        ]
        
        for i, line in enumerate(description_lines):
            if not line: continue # Pula linhas vazias
            
            # Renderiza linha por linha
            line_y = start_y + i * line_spacing
            draw_text_raster(pixel_array, description_font, line, box_x + 20, line_y, COLOR_TEXT)
    
    def _render_transition(self, screen):
        """
        Efeito de 'Cortina' (Wipe Down).
        Usa manipulação direta de memória(PixelArray).
        """
        # Mapeia o progresso (0 a 255) para a altura da tela (0 a height)
        progress = self.transition_alpha / 255.0
        curtain_height = int(self.height * progress)
        
        # Garante limites
        if curtain_height > self.height:
            curtain_height = self.height
            
        if curtain_height > 0:
                screen[0:self.width, 0:curtain_height] = COLOR_TRANSITION

    def _format_time(self, ms):
        """Converte milissegundos para mm:ss"""
        seconds = ms // 1000
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02d}:{secs:02d}"
    
    def _load_highscores(self):
        """
        Lê o arquivo de scores, filtra por dificuldade e retorna os Top 3.
        Retorna: Dicionário {'HARD': [t1, t2, t3], 'NORMAL': [t1, t2, t3]}
        """
        scores = {'NORMAL': [], 'HARD': []}
        base_path = os.path.dirname(os.path.abspath(__file__))
        score_path = os.path.join(base_path, "..", "..", "highscores.txt")

        if not os.path.exists(score_path):
            return scores

        try:
            with open(score_path, "r") as f:
                for line in f:
                    parts = line.strip().split('|')
                    if len(parts) >= 2:
                        diff = parts[0]
                        try:
                            time_ms = int(parts[1])
                            if diff in scores:
                                scores[diff].append(time_ms)
                        except ValueError:
                            continue
            
            # Ordena (menor tempo é melhor) e pega os top 3
            scores['NORMAL'] = sorted(scores['NORMAL'])[:3]
            scores['HARD'] = sorted(scores['HARD'])[:3]
            
        except Exception as e:
            print(f"Erro ao ler highscores: {e}")
            
        return scores
    
    def _render_best_times(self, pixel_array):
        """
        Renderiza a lista de melhores tempos no canto superior direito.
        Utiliza apenas renderização de texto raster.
        """
        start_x = self.width - 200  # Coluna alinhada à direita
        start_y = 180
        line_height = 23

        # Desenho da elipse de fundo
        # Calcula e alinha o tamanho do texto para centralizar a elipse
        title_text = "BEST TIMES"
        title_w, title_h = self.small_font.size(title_text)
        ellipse_cx = start_x + (title_w // 2)
        ellipse_cy = start_y + (title_h // 2)
        
        # Raios da elipse (rx mais largo, ry mais achatado)
        rx = (title_w // 2) + 15  # Um pouco mais larga que o texto
        ry = (title_h // 2) + 5   # Um pouco mais alta que o texto
        
        # Cor de fundo da elipse (Roxo escuro)
        color_bg_ellipse = (60, 40, 90) 
        
        # Scanline fill
        paint_ellipse(pixel_array, (ellipse_cx, ellipse_cy), rx, ry, color_bg_ellipse)
        
        # Título da Seção
        draw_text_raster(pixel_array, self.small_font, "BEST TIMES!", start_x, start_y, COLOR_HIGHSCORE)
        start_y += line_height + 10 # Espaço extra após o título

        # Seção HARD
        draw_text_raster(pixel_array, self.small_font, "--- HARD ---", start_x, start_y, COLOR_HIGHSCORE)
        start_y += line_height
        
        if not self.highscores['HARD']:
            draw_text_raster(pixel_array, self.small_font, "---", start_x, start_y, COLOR_TEXT)
            start_y += line_height
        else:
            for i, time_ms in enumerate(self.highscores['HARD']):
                time_str = f"{i+1}. {self._format_time(time_ms)}"
                draw_text_raster(pixel_array, self.small_font, time_str, start_x, start_y, COLOR_TEXT)
                start_y += line_height

        start_y += 10 # Espaço entre categorias

        # Seção NORMAL
        draw_text_raster(pixel_array, self.small_font, "-- NORMAL --", start_x, start_y, COLOR_HIGHSCORE)
        start_y += line_height
        
        if not self.highscores['NORMAL']:
            draw_text_raster(pixel_array, self.small_font, "---", start_x, start_y, COLOR_TEXT)
            start_y += line_height
        else:
            for i, time_ms in enumerate(self.highscores['NORMAL']):
                time_str = f"{i+1}. {self._format_time(time_ms)}"
                draw_text_raster(pixel_array, self.small_font, time_str, start_x, start_y, COLOR_TEXT)
                start_y += line_height
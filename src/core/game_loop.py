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

        Args:
            width (int): Largura da janela renderizável.
            height (int): Altura da janela renderizável.
            difficulty (str): Configuração de dificuldade (afeta comportamento das entidades).
        """
        self.width = width
        self.height = height
        self.difficulty = difficulty
        
        # Instancia o 'Modelo' do jogo (Física e Estado)
        self.world = World(width, height)
        
        # Inicia música de fundo
        from audio_manager import play_soundtrack
        play_soundtrack(volume=0.5)

        # Carrega texturas
        # !Nota: Verificar localização própia para carregamento de texturas
        self.ufo_texture = pygame.image.load("../assets/ufo.png")
        self.prize_texture = pygame.image.load("../assets/gabriel.png")
        self.cable_texture = pygame.image.load("../assets/cable.png")
        
        # Flags de Debug Visual
        self.show_hitbox = True
        
    def handle_input(self, event):
        """
        Processa eventos discretos de input (ex: pressionar tecla única).

        Args:
            event (pygame.event.Event): O evento capturado pelo Pygame.

        Returns:
            str | None: Retorna "BACK_TO_MENU" se o jogo deve ser encerrado,
                        caso contrário retorna None.
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Delega o gatilho de ação para a máquina de estados do World
                self.world.handle_input_trigger()
                
            elif event.key == pygame.K_ESCAPE:
                # Sinaliza para o main.py que devemos trocar de cena
                return "BACK_TO_MENU"
        return None
    
    def update(self, keys):
        """
        Avança um frame na simulação do jogo.
        
        Args:
            keys (pygame.key.ScancodeWrapper): Estado atual de todas as teclas (para movimento contínuo).
        """
        self.world.update(keys)
    
    def render(self, screen):
        """
        Renderiza o frame atual. Limpa a tela e desenha as entidades.
        
        A ordem de desenho define o 'z-index' (camadas):
        Background -> UFO -> Cabo -> Garra -> Debug -> Prêmios.
        
        Args:
            screen (pygame.Surface): A superfície principal onde o jogo será desenhado.
        """
        screen.fill(const.COLOR_BG_DARK)
        
        # UFO (Corpo + Borda) - ELIPSE
        ufo_hitbox = self.world.ufo.get_ellipse_hitbox()
        ufo_center = ufo_hitbox['center']
        ufo_rx = ufo_hitbox['rx']
        ufo_ry = ufo_hitbox['ry']
        # Pinta o interior com a textura
        paintTexturedEllipse(screen, ufo_center, ufo_rx, ufo_ry, self.ufo_texture)

        # Cabo
        self.render_cable(screen)

        # Garra (Muda cor baseada no estado aberto/fechado)
        poly = rect_to_polygon(self.world.claw.get_rect())
        color = const.COLOR_CLAW_CLOSED if self.world.claw.is_closed else const.COLOR_CLAW_OPEN
        paintPolygon(screen, poly, color)
        drawPolygon(screen, poly, const.COLOR_CLAW_BORDER)

        # Debug: Hitbox da garra
        if self.show_hitbox:
            poly = rect_to_polygon(self.world.claw.get_grab_hitbox())
            drawPolygon(screen, poly, const.COLOR_HITBOX_DEBUG)

        # Prêmios não capturados
        for prize in self.world.prizes:
            if not prize.captured:
                pw = self.prize_texture.get_width()
                ph = self.prize_texture.get_height()
                half = prize.size // 2
                p_x = prize.x
                p_y = prize.y

                vertices_prize = [
                    (p_x - half, p_y - half, 0,  0),   # Topo Esquerda
                    (p_x + half, p_y - half, pw, 0),   # Topo Direita
                    (p_x + half, p_y + half, pw, ph),  # Base Direita
                    (p_x - half, p_y + half, 0,  ph)   # Base Esquerda
                ]
                paintTexturedPolygon(screen, vertices_prize, self.prize_texture, 'standard')


    def render_cable(self, screen):
            """
            Renderiza o cabo do UFO com textura repetida.
            
            Args:
                screen (pygame.Surface): A superfície principal onde o jogo será desenhado.
            """
            cable_rect = self.world.cable.get_rect() # Retorna (x, y, w, h)
            cx, cy, cw, ch = cable_rect

            tex_w = self.cable_texture.get_width()
            tex_h = self.cable_texture.get_height()

            # Mapeamento UV para repetição:
            # U vai de 0 a tex_w (largura da imagem)
            # V vai de 0 a ch (altura DO CABO, não da imagem!)
            # Como ch geralmente é maior que tex_h, o módulo (%) fará a repetição.

            vertices_cable = [
                (cx,      cy,      0,     0),   # Topo Esq
                (cx + cw, cy,      tex_w, 0),   # Topo Dir
                (cx + cw, cy + ch, tex_w, ch),  # Base Dir (V = altura do cabo)
                (cx,      cy + ch, 0,     ch)   # Base Esq (V = altura do cabo)
            ]

            paintTexturedPolygon(screen, vertices_cable, self.cable_texture, 'tiling')
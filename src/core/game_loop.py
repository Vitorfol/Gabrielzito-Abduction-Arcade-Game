"""
Módulo principal do loop de jogo.
Contém a lógica de renderização e orquestração da atualização do jogo.
"""
import pygame
from raster import drawPolygon, paintPolygon, rect_to_polygon
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
        
        # UFO (Corpo + Borda)
        poly = rect_to_polygon(self.world.ufo.get_rect())
        paintPolygon(screen, poly, const.COLOR_UFO)
        drawPolygon(screen, poly, const.COLOR_UFO_BORDER)

        # Cabo
        poly = rect_to_polygon(self.world.cable.get_rect())
        paintPolygon(screen, poly, const.COLOR_CABLE)

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
                poly = rect_to_polygon((
                    prize.x - prize.size // 2,
                    prize.y - prize.size // 2,
                    prize.size,
                    prize.size
                ))
                paintPolygon(screen, poly, const.COLOR_PRIZE)
                drawPolygon(screen, poly, const.COLOR_PRIZE_BORDER)
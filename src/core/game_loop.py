"""
Módulo principal do loop de jogo.
Contém a lógica de renderização e atualização do jogo.
"""
import pygame
from raster import drawPolygon, paintPolygon, rect_to_polygon
from entities.world import World
import constants as const

class GameLoop:
    """Gerencia o loop principal do jogo (opção JOGAR do menu)"""
    
    def __init__(self, width, height, difficulty="NORMAL"):
        self.width = width
        self.height = height
        self.difficulty = difficulty
        
        # Criar o mundo do jogo
        self.world = World(width, height)
        
        # Debug mode
        self.show_hitbox = True
        
    def handle_input(self, event):
        """Processa input do jogo"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.world.claw.is_closed = not self.world.claw.is_closed
            elif event.key == pygame.K_ESCAPE:
                # Sinaliza volta ao menu
                return "BACK_TO_MENU"
        return None
    
    def update(self, keys):
        """Atualiza estado do jogo"""
        self.world.update(keys)
    
    def render(self, screen):
        """Renderiza todos os elementos do jogo"""
        screen.fill(const.COLOR_BG_DARK)
        
        # UFO
        poly = rect_to_polygon(self.world.ufo.get_rect())
        paintPolygon(screen, poly, const.COLOR_UFO)
        drawPolygon(screen, poly, const.COLOR_UFO_BORDER)

        # Cable
        poly = rect_to_polygon(self.world.cable.get_rect())
        paintPolygon(screen, poly, const.COLOR_CABLE)

        # Claw
        poly = rect_to_polygon(self.world.claw.get_rect())
        color = const.COLOR_CLAW_CLOSED if self.world.claw.is_closed else const.COLOR_CLAW_OPEN
        paintPolygon(screen, poly, color)
        drawPolygon(screen, poly, const.COLOR_CLAW_BORDER)

        # Hitbox (debug)
        if self.show_hitbox:
            poly = rect_to_polygon(self.world.claw.get_grab_hitbox())
            drawPolygon(screen, poly, const.COLOR_HITBOX_DEBUG)

        # Prizes
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

"""
Módulo reutilizável que renderiza a visão clássica de dentro de uma claw machine.
Usado tanto no menu quanto na tela de explicação.
"""
import pygame
from raster import drawPolygon, paintPolygon, drawLine
from constants import COLOR_BG_SCENE, COLOR_FLOOR, COLOR_WALL, COLOR_METAL, COLOR_GLASS_REFLECTION


class ClawMachineScene:
    """Renderiza o cenário interno de uma claw machine com vidro e decorações"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # Definir áreas da máquina
        self.glass_thickness = 8
        self.floor_y = height - 80
        self.wall_thickness = 60
        
        # Cores (usando constantes)
        self.bg_color = COLOR_BG_SCENE
        self.glass_color = COLOR_GLASS_REFLECTION
        self.floor_color = COLOR_FLOOR
        self.wall_color = COLOR_WALL
        self.metal_color = COLOR_METAL
        
    def render(self, screen):
        """Renderiza o cenário completo da claw machine"""
        # Fundo interno da máquina
        screen.fill(self.bg_color)
        
        # Chão da máquina
        floor_poly = [
            (0, self.floor_y),
            (self.width, self.floor_y),
            (self.width, self.height),
            (0, self.height)
        ]
        paintPolygon(screen, floor_poly, self.floor_color)
        
        # Linhas de detalhe no chão (padronagem)
        for i in range(0, self.width, 40):
            drawLine(screen, i, self.floor_y, i, self.height, (80, 60, 120))
        
        # Paredes laterais (simulando profundidade)
        # Parede esquerda
        left_wall = [
            (0, 0),
            (self.wall_thickness, 40),
            (self.wall_thickness, self.floor_y - 40),
            (0, self.floor_y)
        ]
        paintPolygon(screen, left_wall, self.wall_color)
        drawPolygon(screen, left_wall, self.metal_color)
        
        # Parede direita
        right_wall = [
            (self.width, 0),
            (self.width - self.wall_thickness, 40),
            (self.width - self.wall_thickness, self.floor_y - 40),
            (self.width, self.floor_y)
        ]
        paintPolygon(screen, right_wall, self.wall_color)
        drawPolygon(screen, right_wall, self.metal_color)
        
        # Vidro frontal (efeito de reflexo com linhas diagonais sutis)
        self._render_glass_effect(screen)
        
        # Moldura do vidro (bordas metálicas)
        self._render_frame(screen)
        
    def _render_glass_effect(self, screen):
        """Renderiza efeito de vidro com linhas de reflexo"""
        # Linhas diagonais sutis simulando reflexo
        for i in range(0, self.width + self.height, 80):
            x1 = i
            y1 = 0
            x2 = i - self.height
            y2 = self.height
            
            # Garantir que as linhas ficam dentro da tela
            if x1 > self.width:
                y1 = x1 - self.width
                x1 = self.width
            if x2 < 0:
                y2 = y2 + x2
                x2 = 0
                
            drawLine(screen, x2, y2, x1, y1, (120, 170, 220, 30))
    
    def _render_frame(self, screen):
        """Renderiza moldura metálica ao redor do vidro"""
        # Moldura superior
        top_frame = [
            (0, 0),
            (self.width, 0),
            (self.width - self.glass_thickness, self.glass_thickness),
            (self.glass_thickness, self.glass_thickness)
        ]
        paintPolygon(screen, top_frame, self.metal_color)
        
        # Moldura inferior
        bottom_frame = [
            (0, self.height),
            (self.width, self.height),
            (self.width - self.glass_thickness, self.height - self.glass_thickness),
            (self.glass_thickness, self.height - self.glass_thickness)
        ]
        paintPolygon(screen, bottom_frame, self.metal_color)
        
        # Moldura esquerda
        left_frame = [
            (0, 0),
            (self.glass_thickness, self.glass_thickness),
            (self.glass_thickness, self.height - self.glass_thickness),
            (0, self.height)
        ]
        paintPolygon(screen, left_frame, self.metal_color)
        
        # Moldura direita
        right_frame = [
            (self.width, 0),
            (self.width - self.glass_thickness, self.glass_thickness),
            (self.width - self.glass_thickness, self.height - self.glass_thickness),
            (self.width, self.height)
        ]
        paintPolygon(screen, right_frame, self.metal_color)

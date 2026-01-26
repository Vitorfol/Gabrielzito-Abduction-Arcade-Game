"""
Módulo reutilizável que renderiza a visão clássica de dentro de uma claw machine.
Usado tanto no menu quanto na tela de explicação.
Otimizado para usar PixelArray (acesso direto à memória).
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
        """Renderiza o cenário completo da claw machine usando PixelArray"""
        
        # Fundo interno da máquina (Otimização: fill é mais rápido em Surface direto)
        screen.fill(self.bg_color)
        
        # Inicia o contexto de PixelArray para desenho de primitivas otimizado
        with pygame.PixelArray(screen) as px_array:
        
            # Chão da máquina
            floor_poly = [
                (0, self.floor_y),
                (self.width, self.floor_y),
                (self.width, self.height),
                (0, self.height)
            ]
            paintPolygon(px_array, floor_poly, self.floor_color)
            
            # Linhas de detalhe no chão (padronagem)
            for i in range(0, self.width, 40):
                drawLine(px_array, i, self.floor_y, i, self.height, (80, 60, 120))
            
            # Paredes laterais (simulando profundidade)
            # Parede esquerda
            left_wall = [
                (0, 0),
                (self.wall_thickness, 40),
                (self.wall_thickness, self.floor_y - 40),
                (0, self.floor_y)
            ]
            paintPolygon(px_array, left_wall, self.wall_color)
            drawPolygon(px_array, left_wall, self.metal_color)
            
            # Parede direita
            right_wall = [
                (self.width, 0),
                (self.width - self.wall_thickness, 40),
                (self.width - self.wall_thickness, self.floor_y - 40),
                (self.width, self.floor_y)
            ]
            paintPolygon(px_array, right_wall, self.wall_color)
            drawPolygon(px_array, right_wall, self.metal_color)
            
            # Vidro frontal (efeito de reflexo com linhas diagonais sutis)
            self._render_glass_effect(px_array)
            
            # Moldura do vidro (bordas metálicas)
            self._render_frame(px_array)
        
    def _render_glass_effect(self, px_array):
        """Renderiza efeito de vidro com linhas de reflexo usando PixelArray"""
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
                
            drawLine(px_array, x2, y2, x1, y1, (120, 170, 220, 30))
    
    def _render_frame(self, px_array):
        """Renderiza moldura metálica ao redor do vidro usando PixelArray"""
        # Moldura superior
        top_frame = [
            (0, 0),
            (self.width, 0),
            (self.width - self.glass_thickness, self.glass_thickness),
            (self.glass_thickness, self.glass_thickness)
        ]
        paintPolygon(px_array, top_frame, self.metal_color)
        
        # Moldura inferior
        bottom_frame = [
            (0, self.height),
            (self.width, self.height),
            (self.width - self.glass_thickness, self.height - self.glass_thickness),
            (self.glass_thickness, self.height - self.glass_thickness)
        ]
        paintPolygon(px_array, bottom_frame, self.metal_color)
        
        # Moldura esquerda
        left_frame = [
            (0, 0),
            (self.glass_thickness, self.glass_thickness),
            (self.glass_thickness, self.height - self.glass_thickness),
            (0, self.height)
        ]
        paintPolygon(px_array, left_frame, self.metal_color)
        
        # Moldura direita
        right_frame = [
            (self.width, 0),
            (self.width - self.glass_thickness, self.glass_thickness),
            (self.width - self.glass_thickness, self.height - self.glass_thickness),
            (self.width, self.height)
        ]
        paintPolygon(px_array, right_frame, self.metal_color)
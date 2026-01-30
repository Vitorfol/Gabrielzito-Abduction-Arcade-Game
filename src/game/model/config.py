"""
Constantes globais do jogo.
Centralizadas para evitar duplicação e facilitar ajustes.
"""

# Cores
# Background
COLOR_BG_DARK = (20, 20, 30)        # Cor de fundo escura principal
COLOR_BG_SCENE = (25, 20, 35)       # Cor de fundo da cena (claw machine)

# UI - Interface do usuário (menus e texto)
COLOR_TEXT = (200, 200, 200)        # Cor padrão de texto (cinza claro)
COLOR_TEXT_SELECTED = (100, 255, 100)  # Cor de texto selecionado (verde)
COLOR_TITLE = (255, 200, 100)       # Cor de títulos (laranja)
COLOR_INSTRUCTION = (150, 150, 150) # Cor de instruções (cinza médio)
COLOR_HIGHSCORE = (255, 230, 80) # Amarelo Arcade

# Game Elements - Elementos do jogo
COLOR_UFO = (180, 180, 255)         # Cor do UFO (azul claro)
COLOR_UFO_BORDER = (255, 255, 255)  # Borda do UFO (branco)
COLOR_CABLE = (200, 200, 200)       # Cor do cabo (cinza)
COLOR_CLAW_OPEN = (0, 255, 0)       # Garra aberta (verde)
COLOR_CLAW_CLOSED = (255, 0, 0)     # Garra fechada (vermelho)
COLOR_CLAW_BORDER = (255, 255, 255) # Borda da garra (branco)
COLOR_HITBOX_DEBUG = (255, 255, 0)  # Cor da hitbox para debug (amarelo)
COLOR_PRIZE = (255, 200, 0)         # Cor do prêmio/Gabrielzito (laranja)
COLOR_PRIZE_BORDER = (255, 255, 255) # Borda do prêmio (branco)

# Scene Colors - Cores da cena da claw machine
COLOR_FLOOR = (60, 40, 80)          # Chão da máquina (roxo escuro)
COLOR_WALL = (80, 60, 100)          # Paredes da máquina (roxo)
COLOR_METAL = (150, 150, 170)       # Partes metálicas (cinza azulado)
COLOR_GLASS_REFLECTION = (120, 170, 220, 30)  # Reflexão do vidro (azul com alpha)

# Animated Boxes - Elementos animados (não mais usado, legado)
COLOR_BOX = (100, 200, 255)         # Cor das boxes animadas
COLOR_BOX_BORDER = (150, 220, 255)  # Borda das boxes
COLOR_ARROW = (255, 200, 100)       # Cor das setas

# Transition - Transição entre estados
COLOR_TRANSITION = (0, 0, 0)        # Cor do fade to black (preto)

# Dimensões
# Screen - Dimensões da janela do jogo
SCREEN_WIDTH = 800                  # Largura da tela em pixels
SCREEN_HEIGHT = 600                 # Altura da tela em pixels

# Font Sizes - Tamanhos de fonte
FONT_SIZE_SMALL = 24                # Fonte pequena (instruções)
FONT_SIZE_MEDIUM = 48               # Fonte média (opções de menu)
FONT_SIZE_LARGE = 64                # Fonte grande (títulos)

# Menu Layout - Layout do menu principal
MENU_OPTION_SPACING = 70            # Espaçamento vertical entre opções do menu (pixels)
MENU_START_Y_OFFSET = -50           # Offset vertical inicial das opções (pixels)
MENU_DIFFICULTY_SPACING = 150       # Espaçamento horizontal entre dificuldades (pixels)
MENU_ARROW_SIZE = 15                # Tamanho das setas (pixels)

# Menu Animation (TexturedBox, TexturedEllipse, TargetCircle)
# Estas constantes são usadas exclusivamente para os elementos animados do menu principal:
# - TexturedBox: Boxes texturizadas que rotacionam e escalam nos cantos
# - TexturedEllipse: Elipse texturizada (UFO) que pulsa
# - TargetCircle: Círculo alvo com anéis concêntricos
ROTATING_BOX_SIZE = 90              # Tamanho base dos elementos texturizados (pixels)
ROTATING_BOX_MARGIN = 80            # Margem dos cantos da tela (pixels)
ROTATION_SPEED = 3.0                # Velocidade de rotação (graus/frame) - apenas TexturedBox
SCALE_SPEED = 0.015                 # Velocidade de pulsação (fator/frame)
SCALE_MIN = 0.7                     # Escala mínima do efeito de pulsação
SCALE_MAX = 1.3                     # Escala máxima do efeito de pulsação

# Game Transition (menu -> jogo)
TRANSITION_SPEED = 8                # Velocidade do fade to black (alpha/frame)

# FPS - Taxa de atualização
TARGET_FPS = 60                     # Frames por segundo alvo

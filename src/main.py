"""
Ponto de entrada principal do Claw Machine Game.
Gerencia estados do jogo (Menu, Jogando, Explicação).
"""
from sys import flags
import pygame
from menu import Menu
from core.game_loop import GameLoop
from enums.gamestate import GameState
from constants import *

pygame.init()

flags = pygame.SCALED | pygame.RESIZABLE | pygame.FULLSCREEN
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
pygame.display.set_caption("Claw Machine Game")
clock = pygame.time.Clock()

# Sistema de estados
current_state = GameState.MENU
menu = Menu(SCREEN_WIDTH, SCREEN_HEIGHT)
game_loop = None

running = True
while running:
    clock.tick(TARGET_FPS)

    # ===== PROCESSAMENTO DE EVENTOS =====
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Estado: MENU
        if current_state == GameState.MENU:
            action = menu.handle_input(event)
            
            if action == "EXPLANATION":
                current_state = GameState.EXPLANATION
        
        # Estado: JOGANDO
        elif current_state == GameState.MOVE:
            action = game_loop.handle_input(event)
            
            if action == "BACK_TO_MENU":
                current_state = GameState.MENU
                menu = Menu(SCREEN_WIDTH, SCREEN_HEIGHT)  # Reiniciar menu
                game_loop = None
        
        # Estado: EXPLICAÇÃO
        elif current_state == GameState.EXPLANATION:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    current_state = GameState.MENU

    # ===== ATUALIZAÇÃO =====
    if current_state == GameState.MENU:
        menu.update()
        
        # Verificar se transição do menu completou
        if menu.is_transition_complete():
            selected_difficulty = menu.get_selected_difficulty()
            game_loop = GameLoop(SCREEN_WIDTH, SCREEN_HEIGHT, selected_difficulty)
            current_state = GameState.MOVE
    
    elif current_state == GameState.MOVE:
        keys = pygame.key.get_pressed()
        game_loop.update(keys)

    # ===== RENDERIZAÇÃO =====
    if current_state == GameState.MENU:
        menu.render(screen)
    
    elif current_state == GameState.EXPLANATION:
        screen.fill(COLOR_BG_DARK)
        font = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        text = font.render("EXPLICACAO - Pressione ESC para voltar", True, COLOR_TEXT)
        screen.blit(text, text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))
    
    elif current_state == GameState.MOVE:
        game_loop.render(screen)

    pygame.display.flip()

pygame.quit()

"""
Ponto de entrada principal do Claw Machine Game.
Gerencia estados do jogo (Menu, Jogando, Explicação).
"""
import sys
import pygame
from game.menu import Menu
from game.game_loop import GameLoop
from game.model.gamestate_enum import GameState
from game.model.difficulty import Difficulty
from game.model.config import *
from game.audio_manager import play_soundtrack

pygame.init()

# Allow running in windowed mode with `--window`; default remains fullscreen
windowed = "--window" in sys.argv or "--WINDOW" in sys.argv
if windowed:
    flags = pygame.SCALED | pygame.RESIZABLE
else:
    flags = pygame.SCALED | pygame.RESIZABLE | pygame.FULLSCREEN

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
pygame.display.set_caption("Claw Machine Game")
clock = pygame.time.Clock()

play_soundtrack(volume=0.25)

# Sistema de dificuldade (instância global)
current_difficulty = Difficulty("NORMAL")

# Sistema de estados
current_state = GameState.MENU
menu = Menu(SCREEN_WIDTH, SCREEN_HEIGHT)
game_loop = None

running = True
while running:
    clock.tick(TARGET_FPS)

    # Processamento de eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Estado: MENU
        if current_state == GameState.MENU:
            action = menu.handle_input(event)
            
            # Atualizar dificuldade se mudou
            if action == "DIFFICULTY_CHANGED":
                difficulty_name = menu.get_selected_difficulty()
                current_difficulty = Difficulty(difficulty_name)
        
        # Estado: JOGANDO
        elif current_state == GameState.MOVE:
            action = game_loop.handle_input(event)
            
            if action == "BACK_TO_MENU":
                current_state = GameState.MENU
                menu = Menu(SCREEN_WIDTH, SCREEN_HEIGHT)  # Reiniciar menu
                game_loop = None

            elif action == "RESTART_GAME":
                game_loop = GameLoop(SCREEN_WIDTH, SCREEN_HEIGHT, current_difficulty)

    # Atualização
    if current_state == GameState.MENU:
        menu.update()
        
        # Verificar se transição do menu completou
        if menu.is_transition_complete():
            game_loop = GameLoop(SCREEN_WIDTH, SCREEN_HEIGHT, current_difficulty)
            current_state = GameState.MOVE
    
    elif current_state == GameState.MOVE:
        keys = pygame.key.get_pressed()
        game_loop.update(keys)

    # Renderização
    if current_state == GameState.MENU:
        menu.render(screen)
    
    elif current_state == GameState.MOVE:
        game_loop.render(screen)

    from game.fps import show_fps
    show_fps(screen, clock)
    pygame.display.flip()

pygame.quit()




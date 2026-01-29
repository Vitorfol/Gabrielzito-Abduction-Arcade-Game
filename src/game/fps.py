import pygame

def show_fps(screen, clock):
    """Desenha o FPS no canto superior esquerdo. Inicializa a fonte apenas uma vez.
    ESTA FUNÇÃO É APENAS UMA FERRAMENTA DE DEBUG!
    """
    if not hasattr(show_fps, "font"):
        show_fps.font = pygame.font.SysFont("Arial", 18, bold=True)
    
    fps = int(clock.get_fps())
    color = (0, 255, 0) if fps >= 55 else (255, 255, 0) if fps >= 30 else (255, 0, 0)
    screen.blit(show_fps.font.render(f"FPS: {fps}", True, color), (10, 10))
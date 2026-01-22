import pygame
from raster import drawPolygon, paintPolygon
from entities.world import World

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


def rect_to_polygon(rect):
    x, y, w, h = rect
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


world = World(WIDTH, HEIGHT)

running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                world.claw.is_closed = not world.claw.is_closed

    keys = pygame.key.get_pressed()
    world.update(keys)

    screen.fill((20, 20, 30))

    # UFO
    poly = rect_to_polygon(world.ufo.get_rect())
    paintPolygon(screen, poly, (180, 180, 255))
    drawPolygon(screen, poly, (255, 255, 255))

    # Cable
    poly = rect_to_polygon(world.cable.get_rect())
    paintPolygon(screen, poly, (200, 200, 200))

    # Claw
    poly = rect_to_polygon(world.claw.get_rect())
    color = (255, 0, 0) if world.claw.is_closed else (0, 255, 0)
    paintPolygon(screen, poly, color)
    drawPolygon(screen, poly, (255, 255, 255))

    # Hitbox (debug)
    poly = rect_to_polygon(world.claw.get_grab_hitbox())
    drawPolygon(screen, poly, (255, 255, 0))

    # Prize
    for prize in world.prizes:
        if not prize.captured:
            poly = rect_to_polygon((
                prize.x - prize.size // 2,
                prize.y - prize.size // 2,
                prize.size,
                prize.size
            ))
            paintPolygon(screen, poly, (255, 200, 0))
            drawPolygon(screen, poly, (255, 255, 255))

    pygame.display.flip()

pygame.quit()

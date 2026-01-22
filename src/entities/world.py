import pygame
from systems.colision import simple_grab
from entities.cable import Cable
from entities.ufo import UFO
from entities.prize import Prize
from entities.claw import Claw
class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.ufo = UFO(width // 2, 100)
        self.claw = Claw(self.ufo.x, self.ufo.y + 50, self.ufo)
        self.cable = Cable(self.ufo, self.claw)

        self.prizes = [
            Prize(400, 450),
            Prize(200, 450),
            Prize(600, 450),
        ]

    def update(self, keys):
        self.handle_movement(keys)
        self.apply_limits()
        self.check_grabs()
        self.update_prizes()

    def handle_movement(self, keys):
        if keys[pygame.K_LEFT]:
            self.ufo.x -= self.ufo.speed
            self.claw.x -= self.ufo.speed

        if keys[pygame.K_RIGHT]:
            self.ufo.x += self.ufo.speed
            self.claw.x += self.ufo.speed

        if keys[pygame.K_DOWN]:
            self.claw.drop()

        if keys[pygame.K_UP]:
            self.claw.lift()

    def apply_limits(self):
        self.ufo.x = max(
            self.ufo.width // 2,
            min(self.width - self.ufo.width // 2, self.ufo.x)
        )

        self.claw.x = self.ufo.x
        self.claw.y = max(self.ufo.y + 40, self.claw.y)
        self.claw.y = min(self.height - 50, self.claw.y)

    def check_grabs(self):
        for prize in self.prizes:
            simple_grab(self.claw, prize)

            if prize.captured:
                prize.x = self.claw.x
                prize.y = self.claw.y + 20

    def update_prizes(self):
        for prize in self.prizes:
            prize.update(50, self.width - 50)

            simple_grab(self.claw, prize)

            if prize.captured:
                prize.x = self.claw.x
                prize.y = self.claw.y + 20
  
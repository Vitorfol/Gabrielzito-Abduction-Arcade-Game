class Claw:
    def __init__(self, x, y, ufo):
        self.ufo = ufo
        self.y = ufo.y + 50
        self.x = x

        # dimensões visuais
        self.width = 40
        self.height = 60

        # dimensões da área de captura
        self.grab_width = 20
        self.grab_height = 15

        self.speed = 4
        self.is_closed = False

    def get_rect(self):
        return (self.x - self.width // 2,
                self.y - self.height // 2,
                self.width,
                self.height)

    def get_grab_hitbox(self):
        return (self.x - self.grab_width // 2,
                self.y - self.grab_height // 2,
                self.grab_width,
                self.grab_height)

    def move(self, dx):
        self.x += dx

    def drop(self):
        self.y += self.speed

    def lift(self):
        self.y -= self.speed

    def close(self):
        self.is_closed = True

    def open(self):
        self.is_closed = False

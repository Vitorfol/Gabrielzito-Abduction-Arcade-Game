class Cable:
    def __init__(self, ufo, claw):
        self.ufo = ufo
        self.claw = claw
        self.width = 18

    def get_rect(self):
        # Converte floats para ints para renderizar
        x = int(self.ufo.x - self.width // 2)
        y = int(self.ufo.y)
        h = int(abs(self.claw.y - self.ufo.y))
        return (x, y, self.width, h)
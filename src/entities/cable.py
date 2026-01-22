class Cable:
    def __init__(self, ufo, claw):
        self.ufo = ufo
        self.claw = claw
        self.width = 6

    def get_rect(self):
        x = self.ufo.x - self.width // 2
        y = self.ufo.y
        h = abs(self.claw.y - self.ufo.y)
        return (x, y, self.width, h)
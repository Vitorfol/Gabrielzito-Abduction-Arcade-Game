class Prize:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 12
        self.captured = False
        self.speed = 2
        self.direction = 1

    def capture(self):
        self.captured = True

    def update(self, min_x, max_x):
        if self.captured:
            return

        self.x += self.speed * self.direction

        half = self.size // 2
        if self.x - half <= min_x or self.x + half >= max_x:
            self.direction *= -1
    

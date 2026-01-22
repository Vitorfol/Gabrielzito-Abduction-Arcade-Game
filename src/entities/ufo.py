class UFO:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        # área lógica
        self.width = 80
        self.height = 40

        self.speed = 4

    def get_rect(self):
        return (self.x - self.width // 2,
                self.y - self.height // 2,
                self.width,
                self.height)
    
    def move(self, dx):
        self.x += dx
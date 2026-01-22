class Prize:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 12
        self.captured = False

    def capture(self):
        self.captured = True
    

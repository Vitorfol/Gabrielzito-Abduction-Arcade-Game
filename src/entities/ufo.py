class UFO:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 80
        self.height = 40

        # Propriedades de física
        self.velocity_x = 0
        self.acceleration = 0.6  # aceleração
        self.friction = 0.92     # desaceleração (0.0 a 1.0)
        self.max_speed = 8       # velocidade maxima

    def get_rect(self):
        return (int(self.x - self.width // 2),
                int(self.y - self.height // 2),
                self.width,
                self.height)
    
    def apply_force(self, direction):
        """Direction: -1 (left) or 1 (right)"""
        self.velocity_x += direction * self.acceleration
        
        # Limit speed
        if self.velocity_x > self.max_speed:
            self.velocity_x = self.max_speed
        elif self.velocity_x < -self.max_speed:
            self.velocity_x = -self.max_speed

    def update_physics(self):
        """Apply velocity and friction"""
        self.x += self.velocity_x
        self.velocity_x *= self.friction
        
        # Stop completely if very slow (prevents micro-sliding)
        if abs(self.velocity_x) < 0.1:
            self.velocity_x = 0
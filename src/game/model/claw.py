class Claw:
    def __init__(self, x, y, ufo):
        self.ufo = ufo
        self.y = ufo.y + 50
        self.x = x
        
        # Dimensões visuais
        self.width = 40
        self.height = 60
        self.grab_width = 45
        self.grab_height = 30

        # Física
        self.velocity_y = 0
        self.gravity = 0.2       # acelera para baixo
        self.motor_speed = 4     # aceleraçao constante
        self.is_closed = False

    def get_rect(self):
        return (int(self.x - self.width // 2),
                int(self.y - self.height // 2),
                self.width,
                self.height)

    def get_grab_hitbox(self):
        return (int(self.x - self.grab_width // 2),
                int(self.y - self.grab_height // 2),
                self.grab_width,
                self.grab_height)

    def drop(self):
        """Apply gravity"""
        self.velocity_y += self.gravity
        self.y += self.velocity_y

    def lift(self):
        """Apply motor force (constant speed)"""
        self.velocity_y = -self.motor_speed
        self.y += self.velocity_y

    def stop(self):
        """Kill velocity (collision or stop)"""
        self.velocity_y = 0

    def close(self):
        self.is_closed = True

    def open(self):
        self.is_closed = False
class Prize:
    """Prêmio (gabrielzito) que se move horizontalmente e pode ser capturado."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 60
        self.captured = False
        self.speed = 2
        self.direction = 1
        
        # Estado da Animação
        self.frame_index = 0.0      # Frame atual (float para incrementos graduais)
        self.anim_cycle_speed = 0.15 # Ajuste para mudar a velocidade global da animação

    def capture(self):
        self.captured = True

    def update(self, min_x, max_x):
        if self.captured:
            return

        # Lógica de movimento
        self.x += self.speed * self.direction

        # Lógica de animação:
        # Incrementa o frame baseado na velocidade (movimento mais rápido = animação mais rápida)
        # abs(self.speed): velocidade negativa não reverte o contador de frames
        self.frame_index += abs(self.speed) * self.anim_cycle_speed
        
        # Mantém o índice dentro do intervalo 0-11 (12 quadros)
        if self.frame_index >= 12:
            self.frame_index %= 12

        # Lógica de Boundary
        half = self.size // 2
        if self.x - half <= min_x or self.x + half >= max_x:
            self.direction *= -1
    

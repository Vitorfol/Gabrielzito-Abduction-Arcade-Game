"""
Sistema de dificuldade do jogo.
Define ranges de número de Gabrielzitos e velocidades baseado na dificuldade selecionada.
Valores são aleatórios dentro dos ranges para evitar comportamento determinístico.
Cada Gabrielzito tem sua própria velocidade.
"""
import random

class Difficulty:
    """
    Classe que encapsula configurações de dificuldade do jogo.
    Centraliza todos os parâmetros relacionados à dificuldade em um único local.
    Usa ranges para gerar valores aleatórios a cada instância.
    Cada Gabrielzito recebe uma velocidade individual.
    """
    
    # Configurações de dificuldade (nome: (range_gabrielzitos, range_velocidade))
    CONFIGS = {
        "EASY": {
            "num_prizes_range": (1, 3),        # 1-3 Gabrielzitos
            "prize_speed_range": (1.0, 1.5)    # 100-150% da velocidade base
        },
        "NORMAL": {
            "num_prizes_range": (3, 5),        # 3-5 Gabrielzitos
            "prize_speed_range": (1.5, 2.5)    # 150-250% da velocidade base
        },
        "HARD": {
            "num_prizes_range": (5, 6),        # 5-6 Gabrielzitos
            "prize_speed_range": (2.5, 3.5)    # 250-350% da velocidade base
        }
    }
    
    def __init__(self, difficulty_name="NORMAL"):
        """
        Inicializa a dificuldade com base no nome fornecido.
        Gera valores aleatórios dentro dos ranges definidos.
        Cada Gabrielzito recebe uma velocidade única.
        
        Args:
            difficulty_name (str): Nome da dificuldade ("EASY", "NORMAL", "HARD")
        """
        if difficulty_name not in self.CONFIGS:
            print(f"Warning: Dificuldade '{difficulty_name}' inválida. Usando NORMAL.")
            difficulty_name = "NORMAL"
        
        self.name = difficulty_name
        config = self.CONFIGS[difficulty_name]
        
        # Gerar número aleatório de Gabrielzitos
        num_min, num_max = config["num_prizes_range"]
        self.num_prizes = random.randint(num_min, num_max)
        
        # Gerar array de velocidades (uma para cada Gabrielzito)
        speed_min, speed_max = config["prize_speed_range"]
        self.prize_speeds = [
            random.uniform(speed_min, speed_max) 
            for _ in range(self.num_prizes)
        ]
    
    def __str__(self):
        speeds_str = ", ".join([f"{s:.2f}x" for s in self.prize_speeds])
        return f"{self.name}: {self.num_prizes} Gabrielzitos, velocidades: [{speeds_str}]"
    
    def __repr__(self):
        return f"Difficulty(name={self.name}, prizes={self.num_prizes}, speeds={self.prize_speeds})"
    
    @staticmethod
    def get_available_difficulties():
        """Retorna lista de nomes de dificuldades disponíveis"""
        return list(Difficulty.CONFIGS.keys())

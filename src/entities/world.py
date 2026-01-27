import pygame
import random
from systems.colision import simple_grab
from entities.cable import Cable
from entities.ufo import UFO
from entities.prize import Prize
from entities.claw import Claw
from enums.gamestate import GameState

class World:
    """
    Gerencia o estado global do jogo, contendo todas as entidades (UFO, Garra, Prêmios)
    e a lógica principal de interação e atualização física.
    """
    def __init__(self, width, height, difficulty):
        """
        Inicializa o mundo do jogo com dimensões específicas e instancia
        os objetos iniciais e o estado da máquina de estados.
        
        Args:
            width (int): Largura da tela
            height (int): Altura da tela
            difficulty (Difficulty): Instância da classe Difficulty
        """
        self.width = width
        self.height = height

        self.ufo = UFO(width // 2, 100)
        self.claw = Claw(self.ufo.x, self.ufo.y + 50, self.ufo)
        self.cable = Cable(self.ufo, self.claw)

        self.state = GameState.MOVE 

        # Cria gabrielzitos dinamicamente baseado na dificuldade
        self.prizes = []
        num_prizes = difficulty.num_prizes
        prize_y = 490  # Posição Y fixa (mais abaixo para melhor visual)
        
        # Distribui gabrielzitos em posições aleatórias sem sobreposição
        spacing = width // (num_prizes + 1)
        min_x = 50
        max_x = width - 50
        min_gap = 80  # distância mínima entre gabrielzitos (px)
        for i in range(num_prizes):
            attempts = 0
            prize_x = None
            while attempts < 200:
                candidate = random.randint(min_x, max_x)
                if all(abs(candidate - p.x) >= min_gap for p in self.prizes):
                    prize_x = candidate
                    break
                attempts += 1

            # Fallback: usar espaçamento regular se não encontrou posição válida
            if prize_x is None:
                prize_x = spacing * (i + 1)

            prize = Prize(prize_x, prize_y)
            # Aplica velocidade individual do array de dificuldade
            prize.speed = difficulty.prize_speeds[i]
            self.prizes.append(prize)
        
        # Mostra gabrielzitos criados
        print(f"{num_prizes} gabrielzitos")
        for i, p in enumerate(self.prizes):
            print(f"  Gabrielzito {i+1}: pos=({p.x}, {p.y}), speed={p.speed:.2f}")

    def handle_input_trigger(self):
        """
        Gerencia a reação ao botão de ação (Espaço).
        Controla as transições de estado: de Mover para Descer, e de Descer para Agarrar.
        """
        # Se estiver movendo, inicia a descida
        if self.state == GameState.MOVE:
            self.state = GameState.DROP
            self.claw.open()
        
        # Se já estiver descendo, tenta agarrar imediatamente
        elif self.state == GameState.DROP:
            self.state = GameState.GRAB

    def update(self, keys):
        """
        Loop principal de lógica. Atualiza física, gerencia a máquina de estados
        (Move, Drop, Grab, Lift) e sincroniza posições das entidades.
        """
        self.ufo.update_physics()

        # Lógica de Estados
        match self.state:
            case GameState.MOVE:
                self.handle_lateral_movement(keys)

            case GameState.DROP:
                self.claw.drop()
                if self.claw.y >= self.height - 80:
                    self.claw.stop() # Zera a velocidade vertical
                    self.state = GameState.LIFT

            case GameState.GRAB:
                self.claw.close()
                self.check_grabs()
                self.state = GameState.LIFT

            case GameState.LIFT:
                self.claw.lift()
                # Se voltou ao topo, muda para MOVE
                if self.claw.y <= self.ufo.y + 50:
                    self.claw.y = self.ufo.y + 50 # Garante a posição exata (snap)
                    self.claw.stop()  # para o impulso de subida
                    self.state = GameState.MOVE

        # Atualizações Gerais
        self.apply_limits()
        self.update_prizes()

        # Mantém a garra alinhada ao UFO no eixo X
        self.claw.x = self.ufo.x

    def handle_lateral_movement(self, keys):
        """
        Verifica as teclas pressionadas (Esquerda/Direita) e aplica forças
        ao UFO, respeitando a física inercial.
        """
        if keys[pygame.K_LEFT]:
            self.ufo.apply_force(-1) 
        if keys[pygame.K_RIGHT]:
            self.ufo.apply_force(1)

    def apply_limits(self):
        """
        Restringe a posição horizontal do UFO para garantir que ele não
        saia dos limites laterais da janela do jogo.
        """
        self.ufo.x = max(
            self.ufo.width // 2,
            min(self.width - self.ufo.width // 2, self.ufo.x)
        )

    def check_grabs(self):
        """
        Percorre a lista de prêmios e verifica colisões com a garra
        para determinar se algum objeto foi capturado.
        """
        for prize in self.prizes:
            # simple_grab já verifica internamente se a garra está fechada
            simple_grab(self.claw, prize)

    def update_prizes(self):
        """
        Atualiza a lógica de cada prêmio. Se um prêmio estiver capturado,
        sua posição é travada na posição da garra.
        """
        for prize in self.prizes:
            prize.update(50, self.width - 50)
            
            # Se o premio for capturado, ele acompanha a posição da garra
            if prize.captured:
                prize.x = self.claw.x
                prize.y = self.claw.y + 20
# Core Module (GameLoop)

Este módulo encapsula a sessão de jogo ativa. Ele atua como o **gerenciador central** que conecta o input do usuário, a simulação física (`World`) e o sistema de desenho (`raster`).

## Estrutura e Fluxo de Dados

O `GameLoop` organiza o código separando a lógica de simulação da parte visual:

1.  **Gerenciamento (`GameLoop`):** Recebe os eventos do teclado e decide se deve passar o comando para o jogo ou encerrar a sessão (ex: voltar ao menu).
2.  **Simulação (`entities.World`):** Contém a lógica do jogo (física, posições, estados de colisão). O `GameLoop` apenas comanda que o World avance um passo no tempo chamando `update()`.
3.  **Visualização (`render`):** A cada frame, o loop lê as posições atuais das entidades no `World` e desenha os polígonos correspondentes na tela.

## Como Utilizar

```python
from core.game_loop import GameLoop

# 1. Instanciação (Geralmente feita pelo Menu)
# Cria uma nova sessão com configurações específicas
game = GameLoop(width=800, height=600, difficulty="NORMAL")

# 2. No Loop Principal (main.py)
running = True
while running:
    # A. Input: Gerencia teclas únicas (Espaço, Esc)
    for event in pygame.event.get():
        action = game.handle_input(event)
        if action == "BACK_TO_MENU":
            # Trocar de cena/estado
            pass

    # B. Update: Gerencia movimento contínuo e física
    keys = pygame.key.get_pressed()
    game.update(keys)

    # C. Render: Desenha o frame atual
    game.render(screen)
```


## Pipeline de Renderização
O método render desenha os elementos em camadas (Z-Order) para garantir a sobreposição correta. Se precisar adicionar novos elementos visuais, respeite esta ordem de desenho:

1. Background (fill)

2. UFO (Nave)

3. Cabo

4. Garra

5. Debug Hitboxes (Visível apenas se self.show_hitbox = True)

6. Prêmios (Itens coletáveis)

Nota: Todas as entidades devem ser convertidas para polígonos (usando rect_to_polygon) antes de serem passadas para as funções de desenho (paintPolygon ou drawPolygon).

Ferramentas de Debug
A classe possui uma flag interna self.show_hitbox.

True: Desenha o retângulo de colisão da garra em uma cor de destaque (útil para ajustar a sensibilidade da mecânica de pegar prêmios).

False: Renderização normal para o jogador final.

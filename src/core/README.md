# Core Module

Este módulo contém a lógica central do jogo, mantendo o `main.py` limpo e organizado.

## Estrutura

- **game_loop.py**: Gerencia o loop principal do jogo (opção "JOGAR" do menu)
  - `GameLoop`: Classe que encapsula a lógica de atualização e renderização do jogo
  - Processa input do jogador
  - Renderiza todos os elementos (UFO, Cable, Claw, Prizes)
  - Retorna "BACK_TO_MENU" quando ESC é pressionado

## Uso

```python
from core.game_loop import GameLoop

# Criar instância do jogo
game = GameLoop(width=800, height=600, difficulty="NORMAL")

# No loop principal
game.update(keys)  # Atualizar estado
game.render(screen)  # Renderizar

# Processar eventos
action = game.handle_input(event)
if action == "BACK_TO_MENU":
    # Voltar ao menu
    pass
```

## Responsabilidades

O módulo `core` é responsável por:
- Gerenciar o loop de jogo (update/render)
- Processar input do jogador durante o jogo
- Renderizar todos os elementos visuais do jogo
- Manter a lógica do jogo isolada do sistema de menus
